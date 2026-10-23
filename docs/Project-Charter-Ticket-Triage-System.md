# PROJECT CHARTER

**Học phần:** Quản trị dự án phần mềm   
**Giảng viên hướng dẫn:** *Nguyễn Thanh Tuấn*   
**Ngày lập tài liệu:** *21/09/2026* (Cập nhật: *19/10/2026*)   
**Phiên bản tài liệu:** Version 3.0 (Cập nhật kiến trúc: English-only & ABSA Zero-shot NLI)   
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
| **Phiên bản tài liệu** | Version 3.0 (Tách 2 bài toán: ABSA Subsystem & Priority Queue Subsystem; English-only) |
| **Repository GitHub chính** | *https://github.com/CRP-2026/Sentiment-Driven-Ticket-Triage-System* |
| **GitHub Project Board URL** | *http://github.com/orgs/CRP-2026/projects/1/views/1* |

---

## 2. NGUỒN GỐC & BỐI CẢNH THỰC TẾ CỦA DỰ ÁN

- **Bài toán nghiệp vụ thực tế mô phỏng (dựa trên dữ liệu công khai):**
  *Bài toán được xác thực dựa trên nhu cầu vận hành thực tế của các trung tâm chăm sóc khách hàng (Customer Support), sử dụng các bộ dữ liệu phản hồi thương mại công khai tiếng Anh (Amazon Reviews 2023 / Customer Support datasets) làm nguồn dữ liệu nghiên cứu và huấn luyện/kiểm thử cho mô hình phân tích khía cạnh; kết hợp tập ticket CSKH tiếng Anh mô phỏng gán nhãn thủ công để kiểm chứng thuật toán định tuyến ưu tiên.*

---

## 3. TÓM TẮT ĐIỀU HÀNH & LUẬN CỨ DỰ ÁN (BUSINESS CASE)

- **Bối cảnh vận hành:** Các trung tâm chăm sóc khách hàng tiếp nhận hàng nghìn yêu cầu hỗ trợ (ticket) mỗi ngày bằng tiếng Anh qua nhiều kênh (email, web form, chat).
- **Vấn đề cốt lõi:** Cơ chế xử lý truyền thống theo thứ tự thời gian FIFO (First In, First Out) khiến những khách hàng gặp sự cố nghiêm trọng, bức xúc cao (nguy cơ hủy dịch vụ, khiếu nại pháp lý, hỏng hóc sản phẩm nghiêm trọng) phải xếp hàng chờ đợi ngang với các thắc mắc thông thường.
- **Giải pháp đề xuất:** Xây dựng hệ thống tự động tiếp nhận, phân tích khía cạnh cảm xúc và định tuyến ưu tiên ticket CSKH tiếng Anh, được phân tách rạch ròi thành **2 bài toán độc lập**:
  1. **Bài toán 1 — Phân tích khía cạnh cảm xúc (ABSA Subsystem):** Ứng dụng mô hình học sâu dạng **Zero-shot Classification & Natural Language Inference (NLI)** để trích xuất đa khía cạnh (Aspects) và cảm xúc tương ứng (Positive / Negative / Neutral) cùng độ tin cậy trong nội dung ticket tiếng Anh.
  2. **Bài toán 2 — Chấm điểm ưu tiên & Hàng đợi định tuyến (Priority Triage & Queue Subsystem):** Áp dụng công thức tính điểm ưu tiên **Rule-based toán học minh bạch**, trọng số từ khóa khẩn cấp và cường độ câu; sau đó đẩy vào hàng đợi ưu tiên in-memory (`heapq`) và lưu trữ bền vững vào cơ sở dữ liệu SQLite, phục vụ điều phối trên Dashboard Streamlit và backend API FastAPI.

---

## 4. MỤC TIÊU DỰ ÁN (SMART OBJECTIVES)

1. **Mục tiêu 1 (Bài toán 1: Năng lực mô hình ABSA Zero-shot NLI):**
   - Xây dựng và tinh chỉnh mô hình ABSA Zero-shot NLI cho miền dữ liệu vé hỗ trợ CSKH tiếng Anh, nhận diện được các nhóm khía cạnh nghiệp vụ chủ chốt (`Customer Service`, `Shipping`, `Product Quality`, `Refund/Payment`, v.v.).
   - Đạt **F1-macro trên từng khía cạnh (per-aspect) ≥ 0.78** và độ chính xác phân loại cảm xúc khía cạnh ≥ 80% trên tập kiểm thử aspect CSKH, hoàn thành trước Tuần 9.
2. **Mục tiêu 2 (Bài toán 2: Priority Engine & Hàng đợi định tuyến):**
   - Triển khai công thức tính điểm ưu tiên rule-based minh bạch có khả năng giải thích nguyên nhân (`explanation`), xử lý xung đột đồng điểm theo FIFO thông qua cấu trúc hàng đợi `heapq`.
   - Xác thực trên tập kiểm thử gán nhãn thủ công (150–200 ticket CSKH tiếng Anh mô phỏng), đạt **mức độ đồng thuận ≥ 80%** giữa thứ tự ưu tiên của hệ thống và đánh giá thủ công của nhóm, hoàn thành trước Tuần 11.
3. **Mục tiêu 3 (Kỷ luật kỹ thuật & Quy chuẩn phát triển):**
   - Duy trì 100% commit tuân thủ Conventional Commits, thiết lập quy trình CI (GitHub Actions) tự động kiểm tra lint và unit test trên mọi Pull Request; bảo vệ nhánh `main` và phân công review chéo tối thiểu 1 thành viên.
4. **Mục tiêu 4 (Sản phẩm tích hợp & Bàn giao):**
   - Hỗ trợ theo dõi Inbox ưu tiên thời gian thực, bảng phân tích thống kê khía cạnh cảm xúc, sẵn sàng demo trực tiếp trước hội đồng trước Tuần 15.

---

## 5. PHẠM VI DỰ ÁN (SCOPE & BOUNDARIES)

Hệ thống được tổ chức phân rã thành 2 bài toán kỹ thuật trọng tâm:

### 5.1. Trong phạm vi triển khai (In-Scope Commitments)

#### A. Bài toán 1 — Hệ thống phân tích khía cạnh (ABSA Subsystem)
- **Bài toán nghiệp vụ:** Tiếp nhận văn bản phản hồi khách hàng bằng tiếng Anh, tự động nhận diện các khía cạnh dịch vụ/sản phẩm được đề cập (`Customer Service`, `Shipping`, `Product Quality`, `Refund/Payment`, `General`...) và phân loại cảm xúc tương ứng (Positive / Negative / Neutral) cho từng khía cạnh.
- **Tiền xử lý & Cổng tiếp nhận tiếng Anh:**
  - Chuẩn hóa văn bản Unicode NFC, loại bỏ mã HTML/URLs/nhiễu kỹ thuật, rút gọn ký tự lặp.
  - Xác thực ngôn ngữ: Chỉ tiếp nhận tiếng Anh; nếu phát hiện ngôn ngữ khác thì gắn cờ `needs_manual_review = True`.
  - Bộ lọc trước từ khóa (Keyword Pre-filtering): Nhận diện tín hiệu từ khóa khía cạnh trước khi suy luận để tối ưu hóa hiệu năng tính toán.
- **Mô hình triển khai:**
  - Ứng dụng mô hình ABSA Zero-shot Classification dựa trên suy luận ngôn ngữ tự nhiên (Natural Language Inference - NLI) với kiến trúc học sâu (`distilbart-mnli` / `deberta-v3-base-zeroshot`).
  - Đầu ra chuẩn hóa: Danh sách các bộ giá trị khía cạnh `(aspect, sentiment, confidence)`.

#### B. Bài toán 2 — Hệ thống hàng đợi & Chấm điểm ưu tiên (Priority Triage & Queue Subsystem)
- **Bộ tính điểm ưu tiên (Priority Engine - Rule-based):**
  - Áp dụng nguyên tắc khía cạnh tiêu cực nghiêm trọng nhất quyết định điểm nền (*worst-aspect-wins*), kết hợp điểm phạt cộng dồn nếu phát sinh nhiều khía cạnh tiêu cực.
  - Tích hợp trọng số từ khóa khẩn cấp tiếng Anh (`urgent`, `immediately`, `lawsuit`, `refund`, `broken`, `chargeback`, v.v.) và hệ số cường độ cú pháp (chữ viết hoa CAPS, dấu cảm thán `!`, dấu hỏi `?`).
  - Điểm chuẩn hóa trong đoạn $[0.0, 1.0]$, phân cấp 4 mức ưu tiên (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) kèm trường giải trình minh bạch `explanation` (Auditable).
- **Hàng đợi ưu tiên & Quản lý trạng thái:**
  - Cấu trúc hàng đợi ưu tiên in-memory bằng `heapq` (ưu tiên điểm cao nhất lên đầu; xử lý đồng điểm theo thời gian tiếp nhận FIFO).
  - Quản lý vòng đời 4 trạng thái ticket: Mới tiếp nhận (`new`) → Đã phân công (`assigned`) → Đang xử lý (`in_progress`) → Đã giải quyết (`resolved`).
- **Lưu trữ dữ liệu:**
  - Bảng chính `tickets`: Lưu trữ nội dung, ngôn ngữ, điểm ưu tiên, cấp độ, khía cạnh nổi bật, trạng thái, nhân sự phân công.
  - Bảng phụ `ticket_aspects`: Lưu trữ chi tiết từng khía cạnh, cảm xúc và điểm tin cậy tương ứng cho mỗi ticket.
- **Giao diện điều phối:**
  - FastAPI cung cấp các RESTful endpoints: `POST /tickets`, `GET /tickets`, `GET /tickets/{id}`, `PATCH /tickets/{id}/status`.
  - Dashboard: Hộp thư ưu tiên (Inbox sắp xếp theo Priority Score giảm dần, phân màu trực quan), Khung mô phỏng kiểm thử thời gian thực (Live Tester), Trang thống kê phân bố khía cạnh và cảm xúc bằng biểu đồ Plotly.

### 5.2. Ngoài phạm vi triển khai (Out-of-Scope Boundaries)

- Xử lý đa ngôn ngữ ngoài tiếng Anh (không xây dựng hay tích hợp module dịch máy tiếng Việt `opus-mt-vi-en` hay huấn luyện mô hình tiếng Việt riêng).
- Áp dụng học máy (ML/DL) hộp đen để trực tiếp dự đoán Priority Score (duy trì rule-based tuyệt đối nhằm đảm bảo khả năng giải trình nghiệp vụ).
- Hệ thống quản lý tài khoản và phân quyền người dùng phức tạp (RBAC) với cơ sở hạ tầng phân tán (Kafka, Celery, Redis).
- Tích hợp 2 chiều với các nền tảng thương mại bên thứ ba (Zendesk, Jira, Salesforce API).

---

## 6. DANH SÁCH & MA TRẬN CÁC BÊN LIÊN QUAN (STAKEHOLDER REGISTER)

| Bên liên quan | Vai trò trong dự án | Quyền lực | Mức quan tâm | Chiến lược tương tác |
| :--- | :--- | :---: | :---: | :--- |
| **Giảng viên hướng dẫn** | Cố vấn học thuật & Người phê duyệt (Academic Supervisor) | Cao | Cao | **Quản lý chặt chẽ**: Báo cáo tiến độ định kỳ theo mốc (M1–M10), bảo vệ đồ án theo rubric môn học. |
| **Nhóm dự án (5 thành viên)** | Thực thi kỹ thuật, thiết kế, kiểm thử, tích hợp | Cao | Cao | **Phối hợp hằng ngày**: Trao đổi trên GitHub, review PR chéo, họp sprint sync hằng tuần. |
| **Nhân viên CSKH (persona giả định)** | Người dùng cuối tham chiếu (End-user reference) | Thấp | Cao | **Giữ liên lạc**: Căn cứ thiết kế luồng thao tác trên Dashboard và các trường giải thích độ ưu tiên. |
| **Cộng đồng nguồn mở (HuggingFace, SemEval)** | Tham chiếu mô hình & dữ liệu chuẩn | Thấp | Thấp | **Theo dõi**: Khai thác mô hình NLI công khai và bộ dữ liệu benchmark uy tín. |

---

## 7. CÔNG CỤ QUẢN LÝ DỰ ÁN & HỆ SINH THÁI KỸ THUẬT

| Hạng mục | Công cụ | Quy chuẩn triển khai |
| :--- | :--- | :--- |
| **Quản lý mã nguồn** | **GitHub Repository** | Nhánh chính `main` và nhánh phát triển `dev`, tiền tố commit theo Conventional Commits. |
| **Quản trị tiến độ** | **GitHub Projects & Issues** | Bảng Kanban Agile: To do → In Progress → In Review → Done; gắn story points và Milestones. |
| **Đảm bảo chất lượng mã** | **GitHub Actions (CI)** | Tự động chạy flake8/black và unit tests (pytest) trên mỗi Pull Request. |
| **Mô hình ABSA & NLI** | **PyTorch & HuggingFace** | Tinh chỉnh mô hình NLI Zero-shot (`transformers`, `peft`) trên Google Colab / Kaggle T4. |
| **Cơ sở dữ liệu & Backend**| **SQLite, FastAPI** | Thiết kế quan hệ ORM chuẩn hóa, RESTful endpoints phục vụ pipeline tích hợp. |
| **Giao diện người dùng** | **Streamlit & Plotly** | Dashboard tương tác trực quan hiển thị kết quả phân tích và điều phối hàng đợi. |

---

## 8. CÁC MỐC THỜI GIAN CHÍNH (HIGH-LEVEL MILESTONES)

| Mốc | Tuần | Deliverable chính | Trách nhiệm |
| :---: | :---: | :--- | :--- |
| **M1** | Tuần 2 | Project Charter & WBS v3.0 được duyệt, khởi tạo GitHub Project Board & CI | Project Lead & Cả nhóm |
| **M2** | Tuần 4 | Thiết kế Kiến trúc 2 bài toán, Schema SQLite/SQLAlchemy và Contract API FastAPI | Tech Lead |
| **M3** | Tuần 6 | Tiền xử lý văn bản tiếng Anh + Priority Engine rule-based & Hàng đợi `heapq` chạy trên dữ liệu mock | Dev & QA |
| **M4** | Tuần 7 | Cập nhật Risk Register #1 & Báo cáo sơ kết Sprint Iteration 1 | QA/QC Engineer |
| **M5** | Tuần 9 | **Đóng băng Bài toán 1:** Pipeline mô hình ABSA Zero-shot NLI fine-tuned trên dữ liệu CSKH tiếng Anh | Dev & DA (Lê Duy) |
| **M6** | Tuần 11 | **Đóng băng Bài toán 2:** Tích hợp Priority Engine với ABSA output, đạt độ đồng thuận ≥ 80% trên testset | Dev & DA (Viết Pháp) |
| **M7** | Tuần 12 | Hoàn thiện Dashboard & Pipeline tích hợp FastAPI end-to-end cho 2 bài toán | Cả nhóm |
| **M8** | Tuần 13 | Đóng băng toàn bộ hệ thống (Code Freeze); Báo cáo kiểm thử biên; Scope Change Control Log | Project Lead & Tech Lead |
| **M9** | Tuần 14 | Hoàn thiện Evidence Package và kịch bản thuyết minh bảo vệ đồ án | Cả nhóm |
| **M10**| Tuần 15 | Bảo vệ đồ án tốt nghiệp & Demo trực tiếp trước Hội đồng chuyên môn | Cả nhóm |

---

## 9. PHƯƠNG PHÁP PHÁT TRIỂN & PHÂN CÔNG VAI TRÒ

### 9.1. Phương pháp phát triển
Áp dụng mô hình **Phát triển lặp & tăng trưởng (Iterative & Incremental)** theo chu kỳ Sprint 2 tuần, phát triển song song 2 bài toán độc lập:
- *Bài toán 1 (ABSA Engine)* và *Bài toán 2 (Priority & Queue)* được thiết kế với giao diện dữ liệu (Contract) rõ ràng, cho phép Bài toán 2 triển khai và kiểm thử hoàn chỉnh với mock data ngay cả trước khi mô hình AI hoàn tất fine-tune.

### 9.2. Phân công vai trò

| # | Họ và tên | MSSV | GitHub | Vai trò dự án | Trách nhiệm chính |
| :-: | :--- | :---: | :---: | :--- | :--- |
| 1 | *Võ Tấn Đức* | *23IT.EB024* | `@Ducinviciable` | **Project Lead / PM** | Lập kế hoạch, quản lý tiến độ, duy trì GitHub Projects, theo dõi rủi ro và thay đổi phạm vi, báo cáo GVHD. |
| 2 | *Nguyễn Phương Thảo* | *23IT.EB098* | `@phuongthaonee` | **QA/QC Engineer** | Xây dựng testset 150–200 ticket CSKH tiếng Anh gán nhãn thủ công; kiểm thử mô hình ABSA; kiểm thử độ đồng thuận Priority Engine; kiểm thử tích hợp E2E. |
| 3 | *Lê Công Quốc Mỹ* | *23IT.EB060* | `@lupinname` | **Technical Lead** | Thiết kế kiến trúc tổng thể 2 bài toán, lược đồ SQLite, thiết kế API FastAPI, review Pull Requests, chuẩn hóa luồng CI/CD. |
| 4 | *Nguyễn Văn Lê Duy* | *23IT.EB026* | `@conangamo` | **Lead Dev - Bài toán 1 (ABSA Subsystem)** | Xây dựng và tinh chỉnh pipeline mô hình ABSA Zero-shot NLI, tối ưu hóa suy luận khía cạnh và cảm xúc CSKH tiếng Anh. |
| 5 | *Nguyễn Viết Pháp* | *23IT.EB070* | `@vietphap035` | **Lead Dev - Bài toán 2 (Priority & UI)** | Xây dựng Priority Engine rule-based, hàng đợi `heapq`, CRUD SQLite, giao diện Dashboard và các biểu đồ phân tích thống kê Plotly. |

---

## 10. RÀNG BUỘC & RỦI RO CHÍNH

### 10.1. Ràng buộc kỹ thuật
- Chi phí hạ tầng $0: Sử dụng tài nguyên GPU miễn phí (Colab/Kaggle T4), CSDL SQLite cục bộ.
- Ngôn ngữ: Chỉ xử lý văn bản tiếng Anh; gắn cờ kiểm tra thủ công cho các ngôn ngữ khác.
- Thuật toán ưu tiên: Tuyệt đối tuân thủ nguyên tắc Rule-based có giải thích (`explanation`), không dùng ML cho priority.

### 10.2. Ma trận rủi ro ban đầu

| Rủi ro kỹ thuật / vận hành | Xác suất | Mức ảnh hưởng | Biện pháp phòng ngừa & giảm thiểu |
| :--- | :---: | :---: | :--- |
| **1. Độ trễ suy luận của mô hình NLI Zero-shot** | Trung bình | Cao | Áp dụng cơ chế lọc từ khóa trước (Keyword Pre-filtering), chỉ suy luận NLI trên các khía cạnh tiềm năng; tối ưu hóa batch inference. |
| **2. Giới hạn phiên GPU Colab khi fine-tune NLI** | Trung bình | Trung bình | Sử dụng kỹ thuật fine-tuning nhẹ (LoRA/PEFT), lưu định kỳ checkpoints lên Google Drive. |
| **3. Không có nhãn priority thực tế từ doanh nghiệp** | Trung bình | Trung bình | Sử dụng dữ liệu CSKH mô phỏng; thiết lập rule-based minh bạch; đo độ đồng thuận giữa thuật toán và nhãn thủ công (cam kết ≥ 80%). |
| **4. Sai lệch trong việc ánh xạ khía cạnh CSKH** | Thấp | Trung bình | Thống nhất danh mục khía cạnh CSKH chuẩn (Customer Service, Shipping, Quality, Payment...), đo lường độ đồng thuận giữa các thành viên. |

---

## 11. TIÊU CHÍ THÀNH CÔNG & ĐỊNH NGHĨA HOÀN THÀNH (DEFINITION OF DONE)

### 11.1. Tiêu chí thành công của dự án
1. Cả 2 bài toán (ABSA Subsystem và Priority Queue Subsystem) tích hợp thông suốt end-to-end từ tiếp nhận văn bản tiếng Anh đến hiển thị trên Dashboard.
2. Mô hình ABSA Zero-shot NLI đạt F1-macro per-aspect ≥ 0.78; Priority Engine đạt độ đồng thuận ≥ 80% với đánh giá thủ công của nhóm.
3. Hồ sơ minh chứng quản lý dự án (Evidence Package) đầy đủ: Commit history, PR reviews, Burndown chart, Báo cáo kỹ thuật.

### 11.2. Definition of Done (DoD) cho mỗi gói công việc
- [ ] Mã nguồn sạch, không lỗi lint, có unit test kiểm thử các ca bình thường và ca biên.
- [ ] Pull Request liên kết trực tiếp với GitHub Issue tương ứng (`Fixes #...`).
- [ ] Có ít nhất 1 phê duyệt (approval) từ Tech Lead hoặc thành viên chuyên trách trước khi merge.
- [ ] Luồng CI (GitHub Actions) chạy pass 100%.
- [ ] Kết quả chức năng được nghiệm thu và xác nhận bởi QA/QC.
- [ ] Issue được đóng và thẻ công việc chuyển sang cột `Done` trên GitHub Project Board.

---

## 12. PHÊ DUYỆT CHÍNH THỨC (FORMAL APPROVAL)

| Đại diện nhóm / Project Lead | Giảng viên hướng dẫn |
| :---: | :---: |
| *(Ký tên)* | *(Ký tên)* |
| <br><br> | <br><br> |
| **Võ Tấn Đức** | **Nguyễn Thanh Tuấn** |
| Ngày: 19 / 10 / 2026 | Ngày: __ / __ / 2026 |
