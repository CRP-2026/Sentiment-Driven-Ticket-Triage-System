# Hệ thống Xếp ưu tiên Ticket CSKH Thương mại điện tử

**Kiến trúc:** Neuro-Symbolic Priority Pipeline | **Lĩnh vực:** E-commerce | **Ngôn ngữ:** Tiếng Anh **Tác giả:** Nguyễn Văn Lê Duy | **Tình trạng:** Tài liệu thiết kế (các tham số là giả thuyết, sẽ hiệu chỉnh bằng thực nghiệm)

## 1. Bài toán và mục tiêu

Trung tâm CSKH thường xử lý ticket theo FIFO, nên ticket khẩn cấp (trừ tiền hai lần, dọa kiện, hàng không đến) bị chôn dưới các câu hỏi thường. Mục tiêu: tự động chấm **điểm ưu tiên 0-100** cho mỗi ticket và đưa ticket quan trọng lên đầu hàng đợi, kèm lý do chấm điểm để nhân viên kiểm tra được.

Ý tưởng chính: **mức độ nghiêm trọng của vấn đề là nền, cảm xúc khách hàng chỉ khuếch đại**. Một khách bình tĩnh báo "bị trừ tiền hai lần" quan trọng hơn một khách giận dữ chê bao bì xấu.

## 2. Dữ liệu đầu vào

| Trường | Bắt buộc | Mô tả |
| --- | --- | --- |
| `ticket_id` | Có | Mã ticket |
| `text` | Có | Nội dung tiếng Anh (email, form, chat) |
| `created_at` | Có | Thời điểm tạo |
| `channel` | Không | email / chat / twitter... (kênh công khai được cộng điểm ngữ cảnh) |
| `is_vip` | Không | Khách VIP hay không |
| `repeat_24h` | Không | Khách đã gửi ticket trước đó trong 24h |

Trường không bắt buộc bị thiếu thì mặc định là không cộng điểm.

## 3. Dữ liệu đầu ra

| Trường | Mô tả |
| --- | --- |
| `score` | Điểm gốc 0-100 (quyết định màu) |
| `priority_level` | Critical / High / Medium / Low |
| `effective_priority` | `score` + điểm chờ (quyết định thứ tự trong Inbox) |
| `risk_group` | Nhóm rủi ro chính (legal, fraud, not_received, churn, defect, none) |
| `sentiment` | (P_neg, P_neu, P_pos) |
| `needs_review` | Cờ cần người xem xét |
| `breakdown` | JSON giải trình từng thành phần điểm |

Ví dụ `breakdown`:

```json
{"risk_group":"fraud","severity":35,"multiplier":1.15,
 "escalation":5,"context":0,"score":45.3,"level":"High"}
```

## 4. Kiến trúc 5 module

### Module 1: Tiền xử lý

Hai luồng văn bản:

- `raw_text`: chỉ chuẩn hóa nhẹ (Unicode, bỏ HTML, che dữ liệu cá nhân, mở rộng slang như pls → please). Giữ chữ hoa, dấu `!` và từ phủ định. Dùng cho RoBERTa, luật từ khóa và cường độ.
- `clean_text`: chỉ cho baseline TF-IDF, vẫn giữ từ phủ định.

Tách câu bằng spaCy. Ticket quá 512 token thì giữ 128 token đầu và 384 token cuối để không mất phần kết.

### Module 2: Phân loại cảm xúc

- Baseline: TF-IDF + SVM hoặc Naive Bayes.
- Chính: fine-tune RoBERTa, hiệu chỉnh xác suất bằng temperature scaling. RoBERTa + VADER là cấu hình thử nghiệm trong ablation.
- Đầu ra là vector xác suất (P_neg, P_neu, P_pos), không phải nhãn cứng.
- Dữ liệu huấn luyện: review sản phẩm (1-2 sao = Negative, 3 = Neutral, 4-5 = Positive), dùng class weights và chia stratified. Review không phải ticket thật, đây là hạn chế đã biết.

### Module 3: Priority Engine

```
score              = min(100, severity × multiplier + escalation + context)
effective_priority = score + min(15, 0.5 × giờ_chờ)
```

**Severity (tối đa 40):** lấy giá trị lớn nhất trong các nhóm khớp. Khớp từ khóa bằng regex có ranh giới từ (`\bsue\b`).

| Nhóm | Ví dụ từ khóa | Điểm |
| --- | --- | --- |
| legal | sue, lawyer, lawsuit | 40 |
| fraud | scam, fraud, charged twice, chargeback | 35 |
| not_received | not received, never arrived, missing | 25 |
| churn | cancel, refund, money back | 20 |
| defect | broken, damaged, defective | 15 |

Từ khóa nằm trong phủ định hoặc ngữ cảnh đã giải quyết ("won't cancel", "thanks for the refund") thì severity giảm 80%. Mỗi nhóm chỉ tính một lần.

**Multiplier (hệ số cảm xúc):** `clamp(1 + 0.5×P_neg − 0.3×P_pos, 0.7, 1.5)`. Nhóm legal và fraud có multiplier tối thiểu 1.0.

**Escalation (tối đa 15):** cộng các dấu hiệu, kẹp trần 15.

- Từ khóa rủi ro nằm ở phần kết ticket: +10; phần thân: +5; phần chào: +2 (ticket một câu tính là phần thân).
- Đe dọa có điều kiện ("or I will", "otherwise"): +5.
- Đe dọa công khai (mạng xã hội, review): +5.
- Cường độ (chữ hoa > 50% hoặc `!!!`): +5, chỉ khi P_pos không chiếm ưu thế.

**Context (tối đa 10):** VIP +5, lặp trong 24h +5, kênh công khai +4.

**Ticket không khớp nhóm nào:**

- Nếu P_pos + P_neu ≥ 0.9: coi là ticket thường, `score` = 10 (Low).
- Ngược lại: gắn `needs_review` và đặt `score` = 30 (Medium) để không chìm xuống đáy.

**Ngưỡng mức:** Critical ≥ 60, High ≥ 40, Medium ≥ 25, Low \< 25 (tính trên `score` gốc).

### Module 4: Hàng đợi và lưu trữ

- SQLite + SQLAlchemy. `effective_priority` tính tại thời điểm truy vấn, sắp theo `effective_priority` giảm dần rồi `created_at` tăng dần.
- Aging k = 0.5 điểm/giờ, trần 15 điểm, để ticket điểm thấp không bị kẹt mãi.
- Vòng đời: New → Assigned → In Progress → Resolved. Bảng `ticket_events` lưu lịch sử chuyển trạng thái.
- Lưu `breakdown` cho mỗi ticket. Nhân viên được phép ghi đè ưu tiên, việc ghi đè được lưu lại làm dữ liệu hiệu chỉnh.

### Module 5: Dashboard

- Inbox sắp theo `effective_priority`, màu theo `score` gốc, mỗi thẻ hiển thị lý do chấm điểm.
- Ticket `needs_review` có huy hiệu riêng.
- Biểu đồ cảm xúc theo thời gian, ô nhập thử trực tiếp (hiện breakdown), trang so sánh với FIFO bằng mô phỏng.

## 5. Ví dụ đầu vào → đầu ra

| Ticket | Nhóm | Tính | Score | Mức |
| --- | --- | --- | --- | --- |
| "I was charged twice for the same order." (bình tĩnh, P_neg≈0.3) | fraud | 35×1.15 + 5 | ≈ 45 | High |
| "Hi, my order hasn't arrived after 12 days. I want my money back or I'll dispute the charge." (P_neg≈0.7) | not_received | 25×1.35 + 15 | ≈ 49 | High |
| "I will sue you if this isn't fixed. This is my last warning!!!" (P_neg≈0.9) | legal | 40×1.45 + 15 | ≈ 73 | Critical |
| "Your packaging is ugly!!!" (P_neg≈0.9) | không khớp | needs_review | 30 | Medium + cờ xem xét |
| "Where can I see my invoice?" (trung tính) | không khớp | ticket thường | 10 | Low |
| "Thanks, the refund arrived today!" (tích cực) | churn (đã giải quyết) | 20×0.2×0.7 | ≈ 3 | Low |

Các con số này là minh họa theo công thức, sẽ được kiểm tra lại khi chạy engine trên dữ liệu mẫu.

## 6. Kế hoạch đánh giá

1. **Cảm xúc:** Macro-F1, confusion matrix, ECE; so sánh Baseline, RoBERTa, RoBERTa + VADER.
2. **Ground truth ưu tiên:** tự gán nhãn 200-300 ticket (4 mức khẩn cấp) bởi hai người, báo cáo weighted kappa. Chia một phần để hiệu chỉnh tham số, phần còn lại giữ kín để kiểm thử.
3. **Xếp hạng:** so sánh FIFO, chỉ cảm xúc, chỉ severity, Phương án A (cộng điểm + luật sàn) và Phương án B (công thức trên) bằng NDCG@10, Precision@k, Spearman.
4. **Vận hành:** mô phỏng ticket đến theo thời gian, nhiều lần chạy, so sánh thời gian chờ của nhóm Critical với FIFO và thời gian chờ tối đa của nhóm Low.

Kết quả thực nghiệm sẽ được báo cáo sau khi chạy; tài liệu này chưa chứa số liệu đo.

## 7. Hạn chế

- Chỉ xử lý tiếng Anh, chỉ lĩnh vực e-commerce.
- Mỉa mai (sarcasm) vẫn khó với mô hình cảm xúc.
- Dữ liệu huấn luyện là review sản phẩm; tập kiểm thử tự gán nhãn, quy mô nhỏ; metadata (VIP, lặp 24h) chỉ thử được bằng dữ liệu giả lập.
- Trọng số, ngưỡng và từ khóa là giả thuyết thiết kế, cần hiệu chỉnh khi triển khai thực tế. Luật VIP có thể gây đối xử khác biệt giữa các nhóm khách.
- SQLite chỉ phù hợp bản demo.