# 📌 Báo Cáo & Danh Sách Vấn Đề Cần Xử Lý (Issues Tracker)

> **Dự án:** Hệ thống phân loại & định tuyến phản hồi khách hàng theo cảm xúc (*Sentiment-Driven Ticket Triage System*)  
> **Mã dự án:** `TICKET-TRIAGE-01` | **Ngày rà soát:** 2026-10-31  
> **Trạng thái baseline:** `22/22 test backend PASSED`, `frontend check/test PASSED` nhưng tồn tại nhiều lỗi hành vi biên và sai lệch kiến trúc.

---

## 🔍 I. Phân Tích Chi Tiết 8 Lỗi Nặng (Bản Chất Kỹ Thuật & Root Cause)

### 1. Langdetect nhận nhầm câu ngắn tiếng Anh thành ngoại ngữ
* **Hiện tượng:** 12/30 ticket tiếng Anh ngắn bị gắn cờ ngoại ngữ (tỷ lệ lỗi 40%). Ví dụ: *"Item arrived broken"* bị nhận là tiếng Đan Mạch (`da`), *"Order missing"* là tiếng Đức (`de`), *"Need help"* là tiếng Hà Lan (`nl`).
* **Root Cause:** Thư viện `langdetect` dựa trên phân phối xác suất n-gram. Với câu cực ngắn (1–4 từ), số lượng n-gram quá ít dẫn đến việc dự đoán sai lệch hoàn toàn.
* **Tác động nguy hiểm:** Khi bị gán là ngoại ngữ, ticket lập tức bị gắn cờ `needs_manual_review = True`, nhận điểm sàn cố định `50.0` (`MEDIUM`) và **bị bỏ qua hoàn toàn bước phân tích khía cạnh (ABSA)**. Khách hàng khiếu nại khẩn cấp bị phân loại sai vào diện chờ duyệt thủ công.
* **Lệch Docstring:** Docstring ghi ngưỡng `0.70`, nhưng code thực tế ở `lang_validator.py` dòng 60 đang để `top.prob >= 0.65`.

---

### 2. Logic phủ định triệt tiêu từ khóa khẩn cấp thật (`_is_negated`)
* **Hiện tượng:** *"I did not receive my refund"*, *"Why won't you refund me"*, *"I have not received my refund yet"* đều bị tính `urgency_bonus = 0`.
* **Root Cause:** Trong `priority_engine.py`:
  ```python
  def _is_negated(sentence: str, kw_index: int) -> bool:
      prefix = sentence[:kw_index]
      for neg in NEGATION_PATTERNS:  # not, never, don't, won't...
          match = re.search(neg, prefix, re.IGNORECASE)
          if match and (kw_index - match.end() < 25):
              return True
      return False
  ```
* **Hậu quả:** Ý đồ ban đầu là loại bỏ các câu hạ nhiệt như *"not urgent"*, *"no rush"*. Nhưng vì áp dụng cho mọi từ khóa khẩn cấp (trong đó có `refund`), nên với câu *"I did not receive my refund"*, từ `not` đứng trước `refund` trong cự ly 12 ký tự (< 25) $\rightarrow$ thuật toán coi `refund` bị phủ định $\rightarrow$ **triệt tiêu toàn bộ điểm khẩn cấp (`urgency_bonus = 0`)**. Đây là lỗi logic nghiêm trọng vì khách hàng khiếu nại luôn dùng cấu trúc phủ định (*"chưa nhận được"*, *"không thấy hoàn tiền"*).

---

### 3. Mock model dùng Substring matching & Random không seed
* **Hiện tượng:** 
  * *"I have an issue with my account"* bị nhận diện là `negative (0.89)` vì chứa chuỗi con `"sue"` (kiện tụng).
  * *"goodbye"* bị nhận diện là `positive` vì chứa chuỗi con `"good"`.
* **Root Cause:** Trong `mock.py`:
  ```python
  has_neg = any(w in text_lower for w in ["bad", "terrible", "sue", ...])
  ```
  Sử dụng toán tử `in` trên chuỗi thay vì khớp ranh giới từ (`\b`). Đồng thời dùng `random.uniform()` không cố định seed.
* **Hậu quả:** Ticket bình thường bị nhận nhầm thành tiêu cực nghiêm trọng (dọa kiện). Mock model không có tính tái lập (non-deterministic), gây sai lệch kết quả giữa các lần chạy demo và kiểm thử.

---

### 4. `clean_text` làm hỏng từ gốc tiếng Anh
* **Hiện tượng:** *"coool"* $\rightarrow$ *"col"*, *"goood"* $\rightarrow$ *"god"*, *"AAA batteries"* $\rightarrow$ *"A batteries"*.
* **Root Cause:** Trong `normalizer.py`:
  ```python
  text = REPEATED_LETTERS_RE.sub(r"\1", text)
  ```
  Ký tự chữ cái lặp $\ge 3$ lần bị nén về **1 ký tự duy nhất** thay vì 2 ký tự.
* **Hậu quả:** Biến đổi sai lệch ngữ nghĩa từ gốc tiếng Anh vốn có 2 chữ cái lặp (*good, cool, feel, book, look*). Chuẩn NLP là nén về 2 ký tự (`r"\1\1"`).

---

### 5. Nhận ticket rỗng / spam / DoS
* **Hiện tượng:** Chuỗi `"   "`, tag rỗng `<b></b>`, hoặc chuỗi dấu `"..."` đều trả về HTTP 201 Created và lọt vào hàng đợi với điểm 50 `MEDIUM`. Chuỗi 350.000 ký tự cũng được tiếp nhận.
* **Root Cause:** Pydantic schema tại `schemas.py` chỉ đặt `min_length=1`, không strip khoảng trắng trước khi kiểm tra, và hoàn toàn không có `max_length`.
* **Hậu quả:** Dữ liệu rác/rỗng làm bẩn database và hàng đợi. Nguy cơ DoS, tràn bộ nhớ khi client gửi payload kích thước lớn.

---

### 6. Múi giờ UTC trả về thiếu hậu tố "Z"
* **Hiện tượng:** Database lưu UTC nhưng API trả về `2026-10-26T04:30:53` (naive datetime không có `Z` hoặc `+00:00`).
* **Root Cause:** SQLite lưu trữ datetime không kèm thông tin timezone (`naive datetime`). Pydantic khi serialize mặc định không gắn `Z`.
* **Hậu quả:** Trình duyệt JavaScript tự động hiểu đây là giờ địa phương (Local Time). Tại Việt Nam (GMT+7), thời gian hiển thị trên giao diện bị lệch 7 giờ so với thực tế.

---

### 7. Hàng đợi `heapq` không đồng bộ với trạng thái Ticket
* **Hiện tượng:** Sau khi gọi API giải quyết một ticket (`PATCH /tickets/{id}/status` sang `resolved`), chỉ số `queue_size` vẫn giữ nguyên.
* **Root Cause:** `PriorityTicketQueue` trong `priority_queue.py` là một hàng đợi in-memory (`heapq`). Endpoint cập nhật trạng thái chỉ thao tác trên database SQLite mà không đồng bộ hoặc loại bỏ phần tử tương ứng trong heap.
* **Hậu quả:** Queue in-memory bị stale; ticket đã giải quyết vẫn nằm trong hàng đợi ưu tiên.

---

### 8. Lệch hợp đồng API & lệnh `make gen-api` sẽ phá vỡ Frontend
* **Hiện tượng:** Chạy `make gen-api` sẽ khiến Frontend lập tức báo lỗi biên dịch TypeScript.
* **Root Cause:**
  1. File `ticket-triage-fe/src/api/schema.d.ts` đang được viết tay với các export kiểu đối tượng: `export interface TicketOut`, `export interface AspectOut`.
  2. Lệnh `make gen-api` sử dụng `openapi-typescript` sinh tự động với cấu trúc chuẩn: `export interface paths { ... }` và `export interface components { schemas: { ... } }`.
  3. `contracts/openapi.json` hiện đang thiếu route `/api/v1/tickets/triage`, các route `/stats/*` thiếu `response_model`, và trường `status` ở backend là `string` thay vì Enum.
* **Hậu quả:** Khi chạy `make gen-api`, file viết tay bị ghi đè hoàn toàn, làm vỡ toàn bộ các import type hiện có trên Frontend.

---

## ⚖️ II. Phân Tích Sự Không Đồng Nhất Giữa Tài Liệu, Cấu Hình và Code

| Vấn đề | Hiện trạng trong Code | Tài liệu / Cấu hình | Đánh giá & Rủi ro |
|:---|:---|:---|:---|
| **File cấu hình YAML** | `configs/priority_rules.yaml` và `configs/aspect_hypotheses.yaml` **không file nào đọc**. Mọi từ khóa, trọng số, template NLI đều hard-code trong code Python. | Tài liệu ghi hệ thống cấu hình động linh hoạt qua YAML. | **File YAML hiện tại chỉ là file "ma".** Cần nạp file YAML thật vào runtime. |
| **Công thức tính Priority** | Điểm cộng dồn: `base + urgency + intensity + aspect` (ngưỡng 70/30, nhãn CRITICAL/MEDIUM/LOW). | `Backend-Plan.md` ghi: $70\%$ sentiment + $30\%$ intensity, chia bậc P0–P3 (80/60/40). | **Mâu thuẫn đặc tả:** Code khớp với `AGENT.md` và `System-Ticket-Report.md`, nhưng đá nhau với `Backend-Plan.md`. Cần thống nhất một bản chuẩn duy nhất. |
| **Trọng số từ khóa** | Cả `CRITICAL_KEYWORDS` lẫn `HIGH_KEYWORDS` đều nhận `+10` (hoặc `+20` ở câu cuối). | Chia thành 2 nhóm CRITICAL và HIGH riêng biệt. | Việc phân 2 nhóm trong code hiện tại là vô nghĩa vì cho điểm ngang nhau. |
| **Silent Fallback sang Mock** | Nếu thiếu PyTorch hoặc Hub offline, code tự `except Exception` rồi gán về `MockSentimentModel` mà `/health` vẫn báo `model_name: baseline`. | Người dùng tưởng hệ thống đang chạy mô hình AI thật. | **Cực kỳ nguy hiểm:** Dẫn đến đánh giá benchmark hoặc nghiệm thu sai lệch (đo mock mà tưởng đo NLI). |
| **ABSA 3 lớp vs 4 lớp** | Code dùng danh sách từ khóa để lọc khía cạnh, sau đó mới chạy model 3 lớp (`positive`, `neutral`, `negative`). | Tài liệu đề cập mô hình NLI 4 lớp (có nhãn `not_mentioned`). | Khía cạnh nào không có từ khóa trong `aspects.yaml` sẽ bị bỏ qua $100\%$, độ bao phủ (recall) phụ thuộc hoàn toàn vào từ khóa. |
| **Ý nghĩa cột confidence** | Ticket ngoại ngữ lưu confidence của nhận diện ngôn ngữ; ticket tiếng Anh lưu confidence cảm xúc. | Lưu thống nhất độ tin cậy của phân loại. | Trộn lẫn hai ngữ nghĩa khác nhau trong cùng một trường dữ liệu. |

---

## 💡 III. Phản Hồi & Đề Xuất Hành Động Theo Từng Bên

### 1. Về phía Data & Preprocessing:
* **Xử lý nhận diện ngôn ngữ (#1):**
  * Không dùng `langdetect` độc lập cho câu ngắn.
  * **Quy tắc:** Nếu câu ngắn ($< 5$ từ hoặc $< 35$ ký tự) và chỉ chứa bảng chữ cái Latin cơ bản `[a-zA-Z\s.,!?'-]`, mặc định coi là tiếng Anh (`en`, confidence = 1.0, `needs_manual_review = False`). Chỉ kiểm tra ngoại ngữ khi phát hiện ký tự ngoài bảng mã Latin hoặc văn bản đủ dài ($> 35$ ký tự).
* **Khía cạnh không có từ khóa:** Bổ sung cơ chế fallback: Nếu không phát hiện từ khóa nào, gán khía cạnh mặc định `general` thay vì để danh sách rỗng, hoặc cho phép chạy Zero-shot NLI trên toàn bộ danh mục khía cạnh cốt lõi.

### 2. Về phía AI / Model:
* **Chấm dứt việc âm thầm Fallback sang Mock:**
  * Endpoint `/health` phải trả về trường `is_mock: bool` và `model_loaded: bool`.
  * Khi fallback về mock, ghi log cảnh báo mức `WARNING`/`ERROR` rõ ràng để nhân viên vận hành nhận biết.
* **Chuẩn hóa Mock Model (#3):**
  * Dùng regex word boundary `\b...\b` để tránh lỗi nhận diện substring.
  * Cố định `seed=42` hoặc băm chuỗi để kết quả kiểm thử mang tính xác định (deterministic).

### 3. Về phía API & Backend Architecture:
* **Đồng bộ Hàng đợi (#7):**
  * Hàng đợi ưu tiên nên ưu tiên sử dụng **Database-backed Queue** (truy vấn với `ORDER BY priority_score DESC, created_at ASC` có index).
  * Nếu vẫn duy trì `heapq` in-memory làm cache: Cài đặt phương thức loại bỏ/đánh dấu xóa (Lazy Deletion) khi ticket chuyển trạng thái `resolved`.
* **Múi giờ UTC (#6):** Thêm helper serialize datetime chuẩn ISO 8601 kết thúc bằng hậu tố `Z` (ví dụ: `dt.replace(tzinfo=timezone.utc).isoformat()`).
* **Hợp đồng API & Frontend Types (#8):**
  * Đổi đường dẫn sinh tự động của `openapi-typescript` sang `src/api/generated.ts`.
  * File `src/api/schema.d.ts` hoặc các type module của Frontend sẽ ánh xạ từ `components['schemas']`.
  * Khai báo `StatusEnum` ở backend và bổ sung `response_model` cho toàn bộ router `/stats/*`.

---

## 👥 IV. Bảng Phân Công Nhiệm Vụ Theo Vai Trò (WBS Mapping)

| Thành viên | Vai trò dự án | Mã WBS | Vấn đề & Nhiệm vụ phụ trách |
|:---|:---|:---|:---|
| **Võ Tấn Đức** | Project Lead / PM | `1.1.2`, `1.1.4` | Chốt mâu thuẫn công thức (`Backend-Plan` vs `Agent.md`), thống nhất Scope Baseline |
| **Lê Công Quốc Mỹ** | Technical Lead | `1.3.1`, `1.3.2`, `1.8.1`, `1.8.5` | Sửa Lỗi **#1** (Langdetect), **#4** (`clean_text`), **#5** (Input rác/DoS), **#6** (Múi giờ UTC), **#8** (`gen-api` & Schema API) |
| **Nguyễn Văn Lê Duy** | Lead Dev ABSA & AI | `1.2.5`, `1.3.3`, `1.4.1`, `1.4.5` | Sửa Lỗi **#3** (Mock Substring/Seed), Nạp `aspect_hypotheses.yaml`, Minh bạch cờ `is_mock` |
| **Nguyễn Viết Pháp** | Lead Dev Priority & UI | `1.5.1`, `1.5.3`, `1.6.3`, `1.7.1` | Sửa Lỗi **#2** (Logic `_is_negated`), Lỗi **#7** (Đồng bộ `heapq`), Nạp `priority_rules.yaml`, Phân tầng điểm Critical vs High |
| **Nguyễn Phương Thảo** | QA/QC Engineer | `1.2.4`, `1.8.2`, `1.8.3` | Viết bộ kiểm thử hồi quy (Regression Tests) cho 8 lỗi, bổ sung 150 ticket ca biên |

---

## 🚀 V. Kế Hoạch Triển Khai 3 Đợt (Sprint Implementation Plan)

### Đợt 1 — Sửa các lỗi logic độc lập & Viết Regression Tests (1 - 2 ngày)
1. **Sửa #4:** Nén ký tự lặp về `\1\1` trong `normalizer.py`.
2. **Sửa #3:** Dùng regex word boundary `\b` và cố định seed cho `mock.py`.
3. **Sửa #5:** Validate `strip()`, `min_length=3`, `max_length=5000` cho input ticket trong `schemas.py`.
4. **Sửa #6:** Chuẩn hóa datetime ISO có hậu tố `Z`.
5. **Sửa #2:** Viết lại logic `_is_negated` (chỉ phủ định tính từ hạ nhiệt như *"not urgent"*, không phủ định từ khóa sự cố như *"refund"*).
6. **Thảo (QA):** Tạo `tests/test_regression_issues.py` với 8 bài kiểm thử độc lập cho từng lỗi.

### Đợt 2 — Đồng bộ Hợp đồng API, Hàng đợi & YAML (2 - 3 ngày)
1. **Sửa #8:** Cập nhật OpenAPI, thêm `StatusEnum`, bổ sung `response_model` cho `/stats/*`, cấu trúc lại `gen-api` để không ghi đè làm vỡ type của Frontend.
2. **Sửa #7:** Đồng bộ trạng thái `heapq` khi chuyển trạng thái `resolved`.
3. **Nạp YAML:** Đọc trực tiếp cấu hình từ `configs/priority_rules.yaml` và `configs/aspect_hypotheses.yaml`.
4. **Minh bạch hóa Model:** Bổ sung trường `is_mock: bool` cho endpoint `/health`.

### Đợt 3 — Hoàn thiện Tiền xử lý & Nghiệm thu Toàn diện (1 - 2 ngày)
1. **Sửa #1:** Cải tiến bộ lọc ngôn ngữ cho câu ngắn tiếng Anh.
2. Chạy toàn bộ test suite (`pytest -v`) đảm bảo 100% test (cả unit, e2e và regression) đều đạt.
3. Chạy `pnpm run check` và `pnpm run test` trên Frontend.
4. QA nghiệm thu trên tập dữ liệu kiểm thử 150–200 ticket CSKH.

