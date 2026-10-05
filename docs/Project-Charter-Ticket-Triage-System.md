# PROJECT CHARTER

**Học phần:** Quản trị dự án phần mềm   
**Giảng viên hướng dẫn:** *Nguyễn Thanh Tuấn*   
**Ngày lập tài liệu:** *21/09/2026* (Cập nhật: *05/10/2026*)   
**Phiên bản tài liệu:** Version 2.0   
**Mã dự án:** `TICKET-TRIAGE-01`

---

## 1. THÔNG TIN CHUNG VỀ DỰ ÁN

| Mục | Chi tiết |
| :--- | :--- |
| **Tên dự án** | Hệ thống phân loại & định tuyến phản hồi khách hàng theo cảm xúc (*Sentiment-Driven Ticket Triage System*) |
| **Tên viết tắt / Mã dự án** | `TICKET-TRIAGE-01` |
| **Học phần** | `Quản trị dự án phần mềm` |
| **Tên nhóm** | *DogTowFaces* |
| **Ngày khởi tạo** | *21/09/2026* |
| **Phiên bản tài liệu** | Version 2.0 (Updated theo Pivot v4.1) |
| **Repository GitHub chính** | *https://github.com/CRP-2026/Sentiment-Driven-Ticket-Triage-System* |
| **GitHub Project Board URL** | *http://github.com/orgs/CRP-2026/projects/1/views/1* |

---

## 2. NGUỒN GỐC & BỐI CẢNH THỰC TẾ CỦA DỰ ÁN

- [x] **Hướng 2: Bài toán nghiệp vụ thực tế mô phỏng (dựa trên dữ liệu công khai)**
  *Bài toán được xác thực dựa trên nhu cầu vận hành thực tế của các bộ phận chăm sóc khách hàng (Customer Support), sử dụng bộ dữ liệu phản hồi thương mại công khai tiếng Anh (Amazon Polarity / SemEval) làm tập huấn luyện chính cho mô hình phân loại cảm xúc; kết hợp bộ dữ liệu tiếng Việt (AIVIVN 2019 / UIT-VSFC) và tập ticket CSKH mô phỏng song ngữ (EN + VI) gán nhãn thủ công để kiểm chứng luồng xử lý đa ngôn ngữ Translate-then-Classify, do dự án không có khách hàng/doanh nghiệp tài trợ trực tiếp.*

> **Lưu ý minh bạch:** Khác với các dự án có khách hàng thật (client sponsor), dự án này dùng **dữ liệu mô phỏng** cho phần đánh giá mức độ ưu tiên (Priority Engine - xem mục 5.2 và 11.2). Điều này cần được nêu rõ trong mọi báo cáo để đảm bảo tính minh bạch về nguồn gốc dữ liệu.

---

## 3. TÓM TẮT ĐIỀU HÀNH & LUẬN CỨ DỰ ÁN (BUSINESS CASE)

- **Bối cảnh vận hành:** Các trung tâm chăm sóc khách hàng tiếp nhận hàng trăm–hàng nghìn phản hồi mỗi ngày qua nhiều kênh (email, chat, biểu mẫu, mạng xã hội) bằng cả tiếng Anh lẫn tiếng Việt.
- **Vấn đề cốt lõi:** Cách xử lý phổ biến hiện nay theo nguyên tắc FIFO (đến trước – phục vụ trước) khiến một khách hàng đang rất bức xúc (nguy cơ hủy đơn, khiếu nại, ảnh hưởng uy tín thương hiệu) phải chờ ngang bằng một khách hàng chỉ hỏi thông tin thông thường. Việc đánh giá mức độ nghiêm trọng hiện phụ thuộc cảm tính của nhân viên, thiếu nhất quán và dễ tắc nghẽn vào giờ cao điểm.
- **Giải pháp đề xuất:** Xây dựng hệ thống ứng dụng kỹ thuật phân tích cảm xúc (Sentiment Analysis) sử dụng mô hình học sâu họ **BERT** để tự động đọc, đánh giá mức độ tiêu cực/khẩn cấp của từng phản hồi, từ đó tự động tính điểm và sắp xếp thứ tự ưu tiên xử lý thông qua 5 module xử lý tuần tự (Tiền xử lý & Cổng ngôn ngữ → Phân loại cảm xúc / Khía cạnh → Priority Engine → Hàng đợi & Lưu trữ → Dashboard điều phối). Hệ thống áp dụng khung quản lý phạm vi MoSCoW với tầng cốt lõi (Must-have: Sentence-level) chạy độc lập vững chắc và tầng mở rộng (Should-have: Aspect-Based Sentiment Analysis - ABSA) nâng cao giá trị nghiệp vụ.

---

## 4. MỤC TIÊU DỰ ÁN (SMART OBJECTIVES)

1. **Mục tiêu 1 (Năng lực kỹ thuật cốt lõi – Mô hình cảm xúc họ BERT):**
   - Xây dựng và đánh giá mô hình phân loại cảm xúc cơ sở (TF-IDF + Linear SVM/Naive Bayes) đạt **F1-macro ≥ 0.75** trên tập kiểm thử, hoàn thành trước Tuần 6.
   - Tinh chỉnh mô hình nâng cao dựa trên kiến trúc **BERT** (fine-tuned BERT sentence-level) đạt **F1-macro ≥ 0.85** trên tập kiểm thử tiếng Anh, hoàn thành và đóng băng bàn giao trước Tuần 9.
   - *(Mục tiêu mở rộng Should-have sau M5):* Nghiên cứu thử nghiệm mô hình họ BERT cho bài toán phân tích khía cạnh (ABSA), hướng tới F1-macro per-aspect ≥ 0.75 cho phân loại cảm xúc theo nhóm khía cạnh (ACSA) và F1 entity-level ≥ 0.65 cho trích xuất thực thể khía cạnh (ABTE).
2. **Mục tiêu 2 (Priority Engine & Xác thực nghiệp vụ):**
   Triển khai đầy đủ công thức tính điểm ưu tiên rule-based (Module 3) và xác thực trên tập mẫu tự gán nhãn thủ công (150–200 ticket mô phỏng song ngữ EN–VI), đạt **mức đồng thuận ≥ 80%** giữa điểm hệ thống và đánh giá thủ công của nhóm, hoàn thành trước Tuần 10.
3. **Mục tiêu 3 (Kỷ luật kỹ thuật & Chất lượng mã nguồn):**
   Duy trì 100% commit tuân thủ Conventional Commits, thiết lập CI (GitHub Actions) chạy tự động kiểm tra lint và unit test trên mọi Pull Request, không có code nào được merge vào `main` mà chưa qua review chéo.
4. **Mục tiêu 4 (Sản phẩm minh họa & Bàn giao):**
   Triển khai dashboard minh họa (Streamlit) chạy ổn định với dữ liệu thật/mô phỏng, hỗ trợ hiển thị danh sách ưu tiên theo thời gian thực, hoàn tất trình diễn (demo) trước giảng viên hướng dẫn và bảo vệ đồ án trước Tuần 15.

---

## 5. PHẠM VI DỰ ÁN (SCOPE & BOUNDARIES)

Hệ thống được thiết kế theo cấu trúc phân tầng MoSCoW chặt chẽ nhằm kiểm soát rủi ro và cam kết bàn giao:

### 5.1. Trong phạm vi triển khai (Cam kết thực hiện)

#### A. Tầng cốt lõi — Bắt buộc bàn giao (MUST-HAVE)
- **Module 1 (Tiền xử lý & Cổng ngôn ngữ):**
  - Chuẩn hóa văn bản Unicode NFC, rút gọn ký tự lặp, loại bỏ HTML/URLs/nhiễu kỹ thuật.
  - Nhận diện ngôn ngữ (`langdetect`): Tiếng Anh (pass-through trực tiếp); Tiếng Việt (chuyển qua dịch máy `opus-mt-vi-en` sang tiếng Anh theo cơ chế Translate-then-Classify); Ngôn ngữ khác (gắn cờ `needs_manual_review = True`).
- **Module 2A (Phân loại cảm xúc cấp câu - Sentence-level):**
  - Mô hình cơ sở (Baseline): TF-IDF (n-gram 1-2) + Linear SVM/Naive Bayes.
  - Mô hình chính (Primary): Fine-tune mô hình học sâu họ **BERT** (phân loại 3 lớp: Tiêu cực / Tích cực / Trung tính) trên tập dữ liệu tiếng Anh; đóng băng mô hình trước M5.
- **Module 3 (Priority Engine - Rule-based):**
  - Công thức tính điểm ưu tiên minh bạch kết hợp: Nhãn cảm xúc + Độ tin cậy (Confidence) + Trọng số từ khóa khẩn cấp (Keyword matching) + Cường độ câu (Dấu câu, chữ hoa).
- **Module 4 (Hàng đợi & Lưu trữ):**
  - Hàng đợi ưu tiên nội bộ bằng cấu trúc `heapq` (xử lý đồng điểm theo thời gian FIFO).
  - Lưu trữ bền vững với SQLite và ORM SQLAlchemy (Bảng `tickets`).
  - Quản trị luồng 4 trạng thái ticket: Mới tiếp nhận (`new`) → Đã phân công (`assigned`) → Đang xử lý (`in_progress`) → Đã giải quyết (`resolved`).
- **Module 5 (Dashboard điều phối):**
  - Giao diện Streamlit + Plotly hiển thị hộp thư ưu tiên (Inbox sắp xếp theo Priority Score giảm dần).
  - Ô nhập ticket kiểm thử thời gian thực, thao tác cập nhật trạng thái, biểu đồ phân bố độ ưu tiên và ngôn ngữ tiếp nhận.
- **Deliverables kỹ thuật & Quản trị:**
  - Repository GitHub bảo vệ nhánh (`main`, `dev`, `feature/absa`), quy chuẩn Conventional Commits.
  - GitHub Project Board theo dõi công việc dạng Agile Kanban / Team Planning.
  - Pipeline tích hợp qua FastAPI endpoints (POST/GET `/tickets`, PATCH `/tickets/{id}/status`).

#### B. Tầng nâng cao — Triển khai sau khi Must-have hoàn tất (SHOULD-HAVE)
- **Module 2B (Aspect-Based Sentiment Analysis - ABSA dựa trên BERT):**
  - Triển khai phân loại cảm xúc theo nhóm khía cạnh (ACSA - Aspect Category Sentiment Analysis) cho 7 nhóm nghiệp vụ CSKH chính (Chất lượng sản phẩm, Dịch vụ khách hàng, Hoàn tiền/Thanh toán, Vận chuyển, v.v.).
  - Triển khai trích xuất thực thể khía cạnh (ABTE - Aspect Term Extraction) để nhận diện cụm từ khía cạnh cụ thể trong văn bản.
- **Mở rộng Module 3, 4, 5:**
  - Tích hợp điểm trọng số khía cạnh tiêu cực nghiêm trọng nhất (worst-aspect) và nhận diện sự cố mới phát sinh (novel issues) vào điểm ưu tiên.
  - Bổ sung bảng quan hệ `ticket_aspects_acsa` và `ticket_aspects_abte` trong SQLite.
  - Bổ sung tab "Phân tích khía cạnh" trên Dashboard Streamlit hiển thị chi tiết khía cạnh và highlight thực thể.

### 5.2. Ngoài phạm vi triển khai (Ranh giới ngăn Scope Creep)

- Hệ thống đa người dùng với phân quyền đăng nhập phức tạp cho nhiều nhân viên thật (RBAC).
- Hàng đợi phân tán quy mô lớn (Kafka, RabbitMQ, Celery) — chỉ sử dụng hàng đợi nội bộ in-memory bằng `heapq` có đồng bộ cơ sở dữ liệu.
- Tích hợp trực tiếp 2 chiều với các nền tảng thương mại bên thứ ba (Zendesk, Salesforce, Gmail API...).
- Huấn luyện mô hình học máy (ML/DL) để trực tiếp dự đoán mức độ ưu tiên (Priority Score) — quyết định thiết kế có chủ đích duy trì rule-based tuyệt đối nhằm đảm bảo tính giải thích được (explainable) và có thể kiểm toán (auditable).
- Huấn luyện mô hình phân loại tiếng Việt riêng biệt từ đầu (dự án chuẩn hóa sang Translate-then-Classify để tối ưu tài nguyên và chất lượng mô hình).

---

## 6. DANH SÁCH & MA TRẬN CÁC BÊN LIÊN QUAN (STAKEHOLDER REGISTER)

### 6.1. Stakeholder Register

| Bên liên quan | Vai trò trong dự án | Quyền lực | Mức quan tâm | Chiến lược tương tác |
| :--- | :--- | :---: | :---: | :--- |
| **Giảng viên hướng dẫn** | Cố vấn học thuật & Người phê duyệt (Academic Supervisor) | Cao | Cao | **Quản lý chặt chẽ**: Báo cáo tiến độ định kỳ theo mốc (M1–M10), bảo vệ đồ án theo rubric. |
| **Nhóm dự án (5 thành viên)** | Thực thi kỹ thuật, thiết kế, kiểm thử, tích hợp | Cao | Cao | **Phối hợp hằng ngày**: Đồng bộ qua GitHub, review PR chéo, họp sync định kỳ hằng tuần. |
| **Nhân viên CSKH (persona giả định)** | Người dùng cuối tham chiếu (End-user reference) | Thấp | Cao | **Giữ liên lạc**: Dùng làm căn cứ thiết kế luồng thao tác UX trên Dashboard, không có kênh khảo sát thật. |
| **Cộng đồng học thuật/ngành (tham chiếu)** | Nguồn tham khảo dữ liệu & benchmark (HuggingFace, SemEval, AIVIVN) | Thấp | Thấp | **Theo dõi**: Khai thác dữ liệu công khai, tài liệu khoa học chuẩn mực. |

### 6.2. Ma trận Quyền lực – Mức quan tâm (Power–Interest Matrix)

```text
Quyền lực cao │  QUẢN LÝ CHẶT CHẼ                        │  GIỮ HÀI LÒNG
              │  - Giảng viên hướng dẫn                  │  (không có bên nào ở nhóm này)
              │  - Nhóm dự án
──────────────┼──────────────────────────────────────────┼───────────────────────────
Quyền lực thấp│  GIỮ LIÊN LẠC                             │  THEO DÕI
              │  - Persona nhân viên CSKH                │  - Cộng đồng học thuật/ngành
              └──────────────────────────────────────────┴───────────────────────────
                             Mức quan tâm cao                       Mức quan tâm thấp
```

---

## 7. CÔNG CỤ QUẢN LÝ DỰ ÁN & HỆ SINH THÁI GITHUB

| Hạng mục | Công cụ | Chuẩn triển khai |
| :--- | :--- | :--- |
| **Mã nguồn** | **GitHub Repository** | Bắt buộc có tiền tố trước tên nhánh: `<feature/fix/refactor>/<Task>`, nhánh `main` và `feature/absa` được bảo vệ. |
| **Theo dõi tiến độ** | **GitHub Projects** | Quy trình Kanban: To do → In Progress → In Review → Done. |
| **Work Packages** | **GitHub Issues** | Mỗi task là 1 issue có tiêu chí chấp nhận (acceptance criteria), nhãn ước lượng effort (story points), gắn milestone. |
| **Review mã nguồn** | **GitHub Pull Requests** | Bắt buộc review chéo tối thiểu 1 thành viên; kiểm tra checklist tự động trước khi merge. |
| **Theo dõi milestone** | **GitHub Milestones** | `M1: Charter & WBS`, `M2: Architecture & Schema`, `M3: Preprocessing & Baseline`, `M5: BERT Sentence Model`, `M8: Integration & Final Demo`. |
| **CI/CD** | **GitHub Actions** | Chạy tự động: kiểm tra lint/format, unit test cho Module 1–3, kiểm thử import mô hình. |
| **Huấn luyện mô hình** | **Google Colab / Kaggle Notebooks** | Môi trường GPU T4 miễn phí phục vụ fine-tune mô hình học sâu họ **BERT**. |

---

## 8. CÁC MỐC THỜI GIAN CHÍNH (HIGH-LEVEL MILESTONES)

| Mốc | Tuần mục tiêu | Deliverable chính | Người chịu trách nhiệm |
| :---: | :---: | :--- | :--- |
| **M1** | Tuần 2 | Project Charter & WBS chi tiết được duyệt, khởi tạo GitHub Project Board | Project Lead & cả nhóm |
| **M2** | Tuần 4 | Sơ đồ kiến trúc 5 module, thiết kế API Contract, Schema dữ liệu SQLite/SQLAlchemy | Technical Lead |
| **M3** | Tuần 6 | Module 1 (Tiền xử lý, Langdetect, Translation) + Module 2A baseline (TF-IDF+SVM) hoàn thành | Dev & DA |
| **M4** | Tuần 7 | Cập nhật Risk Register #1 & Báo cáo sơ kết Sprint Iteration 1 | QA/Test Engineer |
| **M5** | Tuần 9 | **Đóng băng bàn giao Must-have Module 2A:** Mô hình họ **BERT** fine-tuned sentence-level đạt chuẩn | Dev & DA / Cả nhóm |
| **M6** | Tuần 11 | Module 3 (Priority Engine) + Module 4 (Queue & DB) hoàn thành; *(Mở rộng)* Huấn luyện thử nghiệm ACSA | Dev & DA |
| **M7** | Tuần 12 | Module 5 (Dashboard Streamlit) hoàn thành, tích hợp end-to-end Must-have; *(Mở rộng)* Thử nghiệm ABTE | Cả nhóm |
| **M8** | Tuần 13 | Đóng băng toàn bộ hệ thống; Cập nhật Risk Register #2 & Scope Change Control Log | Project Lead |
| **M9** | Tuần 14 | Hoàn tất bộ hồ sơ minh chứng (Evidence Package) và kịch bản thuyết trình bảo vệ | Cả nhóm |
| **M10**| Tuần 15 | Bảo vệ đồ án tốt nghiệp & demo trực tiếp trước hội đồng chuyên môn | Cả nhóm |

---

## 9. PHƯƠNG PHÁP PHÁT TRIỂN & NHỊP ĐỘ (METHODOLOGY & CADENCE)

- **Phương pháp lựa chọn:** **Phát triển lặp & tăng trưởng (Iterative & Incremental Development)** theo chu kỳ 2 tuần/sprint, kết hợp triết lý **MoSCoW**.
- **Lý do lựa chọn:**
  1. *Đảm bảo an toàn tiến độ tốt nghiệp:* Tách biệt ranh giới Must-have và Should-have giúp nhóm luôn có một sản phẩm hoàn chỉnh độc lập (Must-have end-to-end) sẵn sàng nghiệm thu trước Tuần 12 mà không phụ thuộc vào độ phức tạp của các tính năng nâng cao.
  2. *Khám phá yêu cầu dần dần:* Công thức tính điểm ưu tiên (Module 3) cần được tinh chỉnh qua nhiều vòng thử nghiệm với dữ liệu song ngữ trước khi chốt trọng số cuối cùng.
  3. *Giảm thiểu rủi ro sớm:* Rủi ro kỹ thuật lớn nhất (huấn luyện mô hình họ BERT, bộ dịch máy VI->EN) được giải quyết và đóng băng tại mốc M5, trước khi hoàn thiện giao diện người dùng.

---

## 10. PHÂN CÔNG VAI TRÒ & QUẢN TRỊ NHÓM

| # | Họ và tên | MSSV | GitHub Username | Vai trò dự án | Trách nhiệm chính |
| :-: | :--- | :---: | :---: | :--- | :--- |
| 1 | *Võ Tấn Đức* | *23IT.EB024* | `@Ducinviciable` | **Project Lead / PM** | Điều phối lịch trình theo milestone, duy trì GitHub Project Board, tổ chức họp sync, quản lý Risk Register, kiểm soát phạm vi MoSCoW, báo cáo tiến độ với GVHD. |
| 2 | *Nguyễn Phương Thảo* | *23IT.EB098* | `@phuongthaonee` | **QA/QC, Test Engineer** | Kiểm thử mô hình (F1-macro, confusion matrix), kiểm thử đánh giá Priority Engine trên tập gán nhãn thủ công (150–200 ticket), kiểm thử tích hợp end-to-end, tổng hợp Evidence Package. |
| 3 | *Lê Công Quốc Mỹ* | *23IT.EB060* | `@lupinname` | **Technical Lead / Architect** | Thiết kế kiến trúc 5 module, thiết kế API contract (FastAPI), schema SQLite (SQLAlchemy), review code trên PR, quyết định giải pháp kỹ thuật (mô hình họ BERT, quy tắc priority). |
| 4 | *Nguyễn Văn Lê Duy* | *23IT.EB026* | `@conangamo` | **Dev & DA** | Xây dựng Module 1–2 (tiền xử lý văn bản, module dịch máy VI->EN, huấn luyện mô hình họ **BERT** sentence-level; mở rộng ACSA/ABTE), phân tích dữ liệu EDA. |
| 5 | *Nguyễn Viết Pháp* | *23IT.EB070* | `@vietphap035` | **Dev & DA** | Xây dựng Module 3–5 (Priority Engine rule-based, hàng đợi `heapq`, cơ sở dữ liệu SQLite, dashboard Streamlit), phân tích và trực quan hóa kết quả thống kê cảm xúc. |

> **Ghi chú phân công:** Nhóm 5 thành viên được tổ chức theo 2 nhánh kỹ thuật chuyên sâu (NLP/Model vs. Priority/Data/Backend/UI) dưới sự giám sát chất lượng độc lập của QA và điều phối của PM, đảm bảo mỗi thành viên có phần đóng góp rõ ràng khi bảo vệ đồ án.

---

## 11. RÀNG BUỘC, GIẢ ĐỊNH & RỦI RO BAN ĐẦU

### 11.1. Ràng buộc & Giả định

- **Ràng buộc cứng:** Hoàn thành trong khuôn khổ chi phí hạ tầng $0 (sử dụng tài nguyên GPU Colab/Kaggle free tier, SQLite cục bộ, Streamlit Community Cloud); Priority Engine tuyệt đối dùng rule-based.
- **Giả định kỹ thuật:**
  - Bộ dữ liệu phản hồi thương mại công khai đủ đại diện cho văn phong chăm sóc khách hàng.
  - Thư viện dịch máy `opus-mt-vi-en` đáp ứng tốt việc chuyển đổi ngữ nghĩa từ tiếng Việt sang tiếng Anh cho mô hình phân loại.
  - Mô hình học sâu họ **BERT** có thể huấn luyện ổn định trên GPU T4 miễn phí trong thời lượng phiên làm việc cho phép.

### 11.2. Top rủi ro ban đầu của dự án

| Rủi ro ban đầu | Xác suất | Mức ảnh hưởng | Biện pháp phòng ngừa & giảm thiểu |
| :--- | :---: | :---: | :--- |
| **1. Phạm vi dự án bị mở rộng quá mức do thêm ABSA** | Cao | Cao | Áp dụng khung MoSCoW: Must-have (sentence-level) là hệ thống hoàn chỉnh độc lập; chỉ triển khai Should-have (ABSA) sau khi M5 hoàn tất và hệ thống lõi đã chạy ổn định. |
| **2. Sai lệch ngữ nghĩa hoặc độ trễ khi dịch VI sang EN** | Trung bình | Trung bình | Kiểm thử độ chính xác dịch thuật trên tập 50–80 ticket tiếng Việt mô phỏng; thiết lập cache cho kết quả dịch; gắn cờ xem xét thủ công nếu câu quá ngắn/mơ hồ. |
| **3. Không có bộ dữ liệu ưu tiên (priority) thực tế** | Trung bình | Trung bình | Dùng dữ liệu mô phỏng, áp dụng rule-based minh bạch có trường giải thích (`explanation`); nhóm tự gán nhãn tập đối chiếu (150–200 ticket) để đo độ đồng thuận. |
| **4. Hạn chế tài nguyên GPU Colab khi huấn luyện mô hình họ BERT** | Trung bình | Cao | Tối ưu kích thước batch size, áp dụng kỹ thuật tinh chỉnh nhẹ (như LoRA/PEFT) khi cần; lưu checkpoint định kỳ lên Google Drive để tránh mất mát dữ liệu. |
| **5. Bị chất vấn về việc không dùng ML cho phần dự đoán ưu tiên** | Thấp–Trung bình | Thấp | Chuẩn bị luận điểm bảo vệ: Rule-based đảm bảo tính minh bạch, có thể giải trình (auditable), không phụ thuộc vào hộp đen khi đưa ra quyết định vận hành kinh doanh. |

---

## 12. TIÊU CHÍ THÀNH CÔNG & ĐỊNH NGHĨA HOÀN THÀNH (DEFINITION OF DONE)

### 12.1. Tiêu chí thành công của dự án

1. 100% các module trong phạm vi cam kết Must-have hoạt động chính xác và tích hợp end-to-end mượt mà qua pipeline.
2. Mô hình phân loại cảm xúc họ **BERT** đạt F1-macro ≥ 0.85 trên tập kiểm thử; Module Priority Engine đạt mức đồng thuận ≥ 80% với đánh giá thủ công của nhóm.
3. Hồ sơ minh chứng (Evidence Package) đầy đủ: Lịch sử commit tuân thủ Conventional Commits, Project Board cập nhật thời gian thực, tài liệu kiến trúc và báo cáo kỹ thuật hoàn chỉnh.

### 12.2. Definition of Done (DoD) cho mỗi hạng mục công việc

- [ ] Code chạy ổn định, không lỗi cú pháp, có unit test kiểm thử các trường hợp biên.
- [ ] Pull Request được tạo trên GitHub, liên kết trực tiếp với GitHub Issue tương ứng (`Fixes #...`).
- [ ] Có ít nhất 1 lượt review chấp thuận (approval) từ Technical Lead hoặc thành viên nhóm trước khi merge.
- [ ] Quy trình CI (GitHub Actions) chạy thành công (pass tất cả lint và test).
- [ ] Kết quả chức năng được nghiệm thu và đối chiếu bởi QA/Test Engineer.
- [ ] PR được merge vào nhánh chính thức, Issue được đóng và thẻ công việc chuyển sang cột `Done` trên Project Board.

---

## 13. PHÊ DUYỆT CHÍNH THỨC (FORMAL APPROVAL)

*Bằng việc ký tên dưới đây, các bên liên quan xác nhận phê duyệt Project Charter này, cho phép nhóm dự án tiến hành phân rã WBS và triển khai thực hiện theo kế hoạch.*

| Đại diện nhóm / Project Lead | Giảng viên hướng dẫn |
| :---: | :---: |
| *(Ký tên)* | *(Ký tên)* |
| <br><br><br> | <br><br><br> |
| **Võ Tấn Đức** | **Nguyễn Thanh Tuấn** |
| Ngày: 05 / 10 / 2026 | Ngày: __ / __ / 2026 |

