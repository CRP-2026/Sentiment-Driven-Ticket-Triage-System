# WORK BREAKDOWN STRUCTURE (WBS)
## Dự án: Hệ thống phân loại & định tuyến phản hồi khách hàng theo cảm xúc (*Sentiment-Driven Ticket Triage System*)
### Mã dự án: `TICKET-TRIAGE-01` | Học phần: Quản trị dự án phần mềm
### Nhóm thực hiện: *DogTowFaces* | Giảng viên hướng dẫn: *Nguyễn Thanh Tuấn*
### Phiên bản: Version 3.0 | Ngày lập: 19/10/2026 (Cập nhật: English-only, ABSA Zero-shot NLI, Tách 2 bài toán)

---

## 1. TỔNG QUAN & NGUYÊN TẮC PHÂN RÃ WBS

### 1.1. Mục đích tài liệu
Tài liệu này xác lập cấu trúc phân rã công việc chính thức (Work Breakdown Structure - WBS) cho dự án `TICKET-TRIAGE-01` theo phiên bản kiến trúc mới nhất (Version 3.0). WBS đóng vai trò là đường cơ sở phạm vi (Scope Baseline), làm nền tảng cho việc lập kế hoạch tiến độ, ước lượng nỗ lực (Effort Estimation), phân bổ nhân sự (RACI), theo dõi trên GitHub Project Board và kiểm soát chất lượng bàn giao.

### 1.2. Các nguyên tắc phân rã chuẩn mực tuân thủ
Tài liệu được xây dựng chặt chẽ theo hướng dẫn thực hành của Viện Quản lý Dự án Quốc tế (PMI Practice Standard for WBS):
1. **Nguyên tắc hướng sản phẩm bàn giao (Deliverable-Oriented Breakdown):** Toàn bộ các gói công việc (Work Packages) được đặt tên bằng danh từ hoặc cụm danh từ chỉ sản phẩm, thành phần kỹ thuật cụ thể.
2. **Quy tắc 100% (The 100% Rule):** WBS bao trùm 100% toàn bộ công việc cần thực hiện trong phạm vi dự án đã được phê duyệt trong Project Charter Version 3.0.
3. **Phân tách 2 bài toán kỹ thuật độc lập (Two Subsystem Architecture):**
   - **Bài toán 1 — Hệ thống phân tích khía cạnh (ABSA Subsystem):** Ứng dụng mô hình học sâu dạng Zero-shot Classification & Natural Language Inference (NLI) để phát hiện khía cạnh và cảm xúc đa chiều trên dữ liệu ticket CSKH tiếng Anh.
   - **Bài toán 2 — Hệ thống hàng đợi & Chấm điểm ưu tiên (Priority Triage & Queue Subsystem):** Áp dụng công thức tính điểm ưu tiên Rule-based toán học minh bạch (*worst-aspect-wins*), kết hợp hàng đợi `heapq`, cơ sở dữ liệu SQLite, backend FastAPI và giao diện Streamlit Dashboard.
4. **Phạm vi ngôn ngữ duy nhất (English-only Boundary):** Toàn bộ hệ thống tập trung xử lý tiếng Anh. Loại bỏ các module dịch máy và các bộ dữ liệu tiếng Việt để đảm bảo độ chính xác ngữ nghĩa và tối ưu hóa hiệu năng vận hành.

---

## 2. CÂY CẤU TRÚC PHÂN RÃ CÔNG VIỆC (WBS HIERARCHY TREE)

```text
1.0 Hệ thống phân loại & định tuyến phản hồi khách hàng theo cảm xúc (TICKET-TRIAGE-01)
├── 1.1 Quản trị dự án & Hồ sơ học phần (Project Management & Compliance)
│   ├── 1.1.1 Bộ hồ sơ khởi tạo dự án (Project Charter & Stakeholder Register v3.0)
│   ├── 1.1.2 Bản kế hoạch phạm vi & Từ điển WBS (Scope Baseline & WBS Dictionary v3.0)
│   ├── 1.1.3 Hệ thống theo dõi tiến độ Agile & Bảng Kanban (GitHub Projects & Issues)
│   ├── 1.1.4 Sổ theo dõi rủi ro & Nhật ký thay đổi phạm vi (Risk & Change Log)
│   └── 1.1.5 Bộ hồ sơ minh chứng hoàn tất & Báo cáo đồ án (Evidence Package)
│
├── 1.2 Hạ tầng kỹ thuật, Môi trường & Dữ liệu (Infrastructure & Data Foundation)
│   ├── 1.2.1 Kho lưu trữ mã nguồn & Luồng kiểm thử tự động (GitHub Repo & CI Actions)
│   ├── 1.2.2 Môi trường huấn luyện GPU & Tệp cấu hình thư viện (Colab/Kaggle & requirements.txt)
│   ├── 1.2.3 Bộ dữ liệu phản hồi CSKH tiếng Anh chuẩn hóa (Amazon Reviews CSKH Subset)
│   ├── 1.2.4 Tập dữ liệu kiểm thử 150–200 ticket CSKH tiếng Anh gán nhãn thủ công (Human Labeled Testset)
│   ├── 1.2.5 Bộ template giả thuyết NLI & Cấu hình danh mục khía cạnh CSKH (NLI Hypothesis & Aspect Config)
│   ├── 1.2.6 Bộ dữ liệu khía cạnh chuẩn hóa benchmark (SemEval Laptop / CSKH Benchmark)
│   └── 1.2.7 Bảng ánh xạ khía cạnh CSKH & Báo cáo độ đồng thuận (Aspect Category Mapping)
│
├── 1.3 Module 1 — Tiền xử lý văn bản tiếng Anh & Lọc trước khía cạnh (Preprocessing & Pre-filter)
│   ├── 1.3.1 Bộ chuẩn hóa văn bản tiếng Anh (English Text Normalizer & Cleaner)
│   ├── 1.3.2 Bộ xác thực ngôn ngữ tiếng Anh & Gắn cờ ngoại lệ (English Language Validator)
│   ├── 1.3.3 Bộ lọc trước từ khóa khía cạnh (Keyword Pre-filter for Aspects)
│   └── 1.3.4 Giao diện hàm tiền xử lý tích hợp & Bộ kiểm thử biên (Preprocessing Suite)
│
├── 1.4 Module 2 — Bài toán 1: Hệ thống phân tích khía cạnh ABSA Zero-shot NLI (ABSA Subsystem)
│   ├── 1.4.1 Pipeline Zero-shot NLI Baseline (NLI Baseline Pipeline)
│   ├── 1.4.2 Bộ quản lý khía cạnh nghiệp vụ CSKH (Aspect Manager & Config)
│   ├── 1.4.3 Mô hình ABSA Zero-shot NLI fine-tuned trên dữ liệu CSKH tiếng Anh (Fine-tuned ABSA Model)
│   ├── 1.4.4 Bộ đánh giá hiệu năng & Ma trận nhầm lẫn mô hình ABSA (Model Evaluation Package)
│   └── 1.4.5 Giao diện API suy luận phân tích khía cạnh (ABSA Inference Service)
│
├── 1.5 Module 3 — Bài toán 2: Bộ tính điểm ưu tiên nghiệp vụ (Rule-Based Priority Engine)
│   ├── 1.5.1 Bộ từ điển từ khóa khẩn cấp tiếng Anh & Trọng số khía cạnh (Priority Rules Config)
│   ├── 1.5.2 Bộ trích xuất cường độ cảm xúc & Cú pháp câu tiếng Anh (Intensity Extractor)
│   ├── 1.5.3 Hàm tính toán điểm ưu tiên theo khía cạnh nghiêm trọng nhất (Worst-Aspect Priority Engine)
│   └── 1.5.4 Bộ kiểm thử tự động & Báo cáo đồng thuận nghiệp vụ (80% Agreement Validation Report)
│
├── 1.6 Module 4 — Bài toán 2: Hệ thống hàng đợi & Lưu trữ dữ liệu (Queue & Storage Subsystem)
│   ├── 1.6.1 Lược đồ CSDL vé hỗ trợ và khía cạnh & Đối tượng ORM (SQLite Tickets & Aspects Schema)
│   ├── 1.6.2 Bộ thao tác dữ liệu vé hỗ trợ và khía cạnh (Ticket & Aspect CRUD Data Access Layer)
│   ├── 1.6.3 Cấu trúc hàng đợi ưu tiên nội bộ theo điểm số và thời gian (heapq Priority Queue)
│   └── 1.6.4 Bộ quản lý vòng đời 4 trạng thái vé hỗ trợ (Ticket State Lifecycle Manager)
│
├── 1.7 Module 5 — Giao diện điều phối & Trực quan hóa dữ liệu (Dashboard Subsystem)
│   ├── 1.7.1 Giao diện hộp thư ưu tiên & Bảng danh sách vé hỗ trợ (Triage Inbox View)
│   ├── 1.7.2 Bảng điều khiển phân tích thống kê khía cạnh cảm xúc (Aspect Analytics View)
│   ├── 1.7.3 Khung tiếp nhận & Kiểm thử phân loại vé thời gian thực (Live Tester Simulator)
│   └── 1.7.4 Giao diện thao tác cập nhật trạng thái & Phân công xử lý (Action Component)
│
└── 1.8 Tích hợp toàn hệ thống, Kiểm thử & Đóng gói bàn giao (Integration & Deployment)
    ├── 1.8.1 Giao diện lập trình ứng dụng điều phối tập trung (FastAPI Core Pipeline API)
    ├── 1.8.2 Bộ kiểm thử tích hợp luồng xử lý toàn trình 2 bài toán (End-to-End Test Suite)
    ├── 1.8.3 Bộ kịch bản kiểm thử tình huống biên & Ngoại lệ (Edge Case Test Cases)
    ├── 1.8.4 Bộ dữ liệu demo giả lập tích hợp sẵn (Pre-seeded Demo Dataset 50–100 Tickets)
    └── 1.8.5 Bản phát hành đóng gói ứng dụng hoàn chỉnh (Packaged Release & Deployment)
```

---

## 3. BẢNG DANH MỤC PHÂN RÃ WBS TỔNG HỢP

| Mã WBS | Tên gói công việc / Deliverable | Bài toán phụ trách | Thành phần bàn giao chính | Người phụ trách | Milestone |
| :---: | :--- | :---: | :--- | :---: | :---: |
| **1.1.1** | Hồ sơ khởi tạo dự án v3.0 | Quản lý DA | `Project-Charter-Ticket-Triage-System.md`, Stakeholder Register | Võ Tấn Đức | M1 (T2) |
| **1.1.2** | Bản kế hoạch phạm vi & Từ điển WBS v3.0 | Quản lý DA | `WBS-Ticket-Triage-System.md`, Scope Baseline | Võ Tấn Đức | M1 (T2) |
| **1.1.3** | Bảng theo dõi tiến độ Agile & Kanban | Quản lý DA | GitHub Projects Board, Issues template, Milestones | Võ Tấn Đức | M1 (T2) |
| **1.1.4** | Sổ theo dõi rủi ro & Thay đổi phạm vi | Quản lý DA | Risk Register, Scope Change Control Log | Võ Tấn Đức | M4, M8 |
| **1.1.5** | Hồ sơ minh chứng & Báo cáo đồ án | Quản lý DA | Evidence Package, Báo cáo kỹ thuật tổng kết, Slide | Cả nhóm | M9, M10 |
| **1.2.1** | Kho mã nguồn & CI Actions | Hạ tầng | GitHub Repo (`main`/`dev`), flake8/black, pytest workflow | Lê Công Quốc Mỹ | M1 (T2) |
| **1.2.2** | Môi trường GPU & Cấu hình thư viện | Hạ tầng | Google Colab/Kaggle notebook mẫu, `requirements.txt` | Nguyễn Văn Lê Duy | M2 (T4) |
| **1.2.3** | Bộ dữ liệu phản hồi CSKH tiếng Anh | Dữ liệu | Tập train/val/test CSKH tiếng Anh trích từ Amazon Reviews | Nguyễn Văn Lê Duy | M2 (T4) |
| **1.2.4** | Tập kiểm thử 150–200 ticket CSKH gán nhãn | Dữ liệu | File `testset_human_labeled.json` (150–200 ticket EN có nhãn) | Nguyễn Phương Thảo | M3 (T6) |
| **1.2.5** | Bộ template giả thuyết NLI & Cấu hình khía cạnh | Dữ liệu | File cấu hình `aspect_hypothesis_config.yaml` cho NLI | Nguyễn Văn Lê Duy | M3 (T6) |
| **1.2.6** | Bộ dữ liệu khía cạnh chuẩn hóa benchmark | Dữ liệu | Tập dữ liệu SemEval Laptop / CSKH benchmark | Nguyễn Văn Lê Duy | M5 (T9) |
| **1.2.7** | Bảng ánh xạ khía cạnh CSKH & Độ đồng thuận | Dữ liệu | Bảng ánh xạ aspect CSKH, điểm Cohen's Kappa ≥ 0.70 | Nguyễn Phương Thảo | M5 (T9) |
| **1.3.1** | Bộ chuẩn hóa văn bản tiếng Anh | Module 1 | Module `clean_text()`, Unicode NFC, strip HTML/URLs | Lê Công Quốc Mỹ | M3 (T6) |
| **1.3.2** | Bộ xác thực ngôn ngữ & Gắn cờ ngoại lệ | Module 1 | Module `validate_english()`, cờ `needs_manual_review` | Lê Công Quốc Mỹ | M3 (T6) |
| **1.3.3** | Bộ lọc trước từ khóa khía cạnh | Module 1 | Module `aspect_keyword_filter.py` lọc trước khía cạnh | Nguyễn Văn Lê Duy | M3 (T6) |
| **1.3.4** | Giao diện tiền xử lý tích hợp & Test suite | Module 1 | Module `preprocess_pipeline.py` + bộ 10 unit test cases | Lê Công Quốc Mỹ | M3 (T6) |
| **1.4.1** | Pipeline Zero-shot NLI Baseline | Bài toán 1 | Script nạp `distilbart-mnli` / `deberta-v3-base-zeroshot` | Nguyễn Văn Lê Duy | M3 (T6) |
| **1.4.2** | Bộ quản lý khía cạnh nghiệp vụ CSKH | Bài toán 1 | Module `AspectManager` cấu hình danh mục khía cạnh CSKH | Nguyễn Văn Lê Duy | M5 (T9) |
| **1.4.3** | Mô hình ABSA Zero-shot NLI fine-tuned | Bài toán 1 | Checkpoint mô hình NLI fine-tuned trên domain CSKH | Nguyễn Văn Lê Duy | M5 (T9) |
| **1.4.4** | Báo cáo đánh giá hiệu năng mô hình ABSA | Bài toán 1 | Báo cáo F1-macro per-aspect, Confusion Matrix, Accuracy | Nguyễn Phương Thảo | M5 (T9) |
| **1.4.5** | Giao diện API suy luận phân tích khía cạnh | Bài toán 1 | Module `predict_aspects(text)` trả về list aspect, sentiment, conf | Nguyễn Văn Lê Duy | M5 (T9) |
| **1.5.1** | Từ điển từ khóa khẩn cấp & Trọng số khía cạnh | Bài toán 2 | File `configs/priority_rules.yaml` danh mục khẩn cấp & trọng số | Nguyễn Viết Pháp | M4 (T7) |
| **1.5.2** | Bộ trích xuất cường độ cảm xúc câu | Bài toán 2 | Module trích xuất CAPS LOCK, dấu cảm thán, dấu hỏi | Nguyễn Viết Pháp | M4 (T7) |
| **1.5.3** | Hàm tính điểm ưu tiên khía cạnh nghiêm trọng nhất | Bài toán 2 | Module `calculate_priority()` xuất điểm [0–1] & explanation | Nguyễn Viết Pháp | M6 (T11) |
| **1.5.4** | Báo cáo kiểm thử đồng thuận nghiệp vụ | Bài toán 2 | Báo cáo đo độ đồng thuận ≥ 80% trên 150–200 ticket testset | Nguyễn Phương Thảo | M6 (T11) |
| **1.6.1** | Lược đồ CSDL vé hỗ trợ và khía cạnh & ORM | Bài toán 2 | SQLAlchemy models (`Ticket`, `TicketAspect`), SQLite `tickets.db` | Lê Công Quốc Mỹ | M2 (T4) |
| **1.6.2** | Bộ thao tác dữ liệu vé hỗ trợ (DAL CRUD) | Bài toán 2 | Module `src/database/repository.py` thao tác dữ liệu vé | Nguyễn Viết Pháp | M4 (T7) |
| **1.6.3** | Cấu trúc hàng đợi ưu tiên nội bộ `heapq` | Bài toán 2 | Class `TicketPriorityQueue` hỗ trợ push, pop theo priority và time | Nguyễn Viết Pháp | M6 (T11) |
| **1.6.4** | Quản lý vòng đời 4 trạng thái vé | Bài toán 2 | State manager: `new` -> `assigned` -> `in_progress` -> `resolved` | Nguyễn Viết Pháp | M6 (T11) |
| **1.7.1** | Giao diện hộp thư ưu tiên | Giao diện | Dashboard Inbox sắp xếp priority giảm dần, phân màu | Nguyễn Viết Pháp | M7 (T12) |
| **1.7.2** | Bảng điều khiển phân tích thống kê khía cạnh | Giao diện | Biểu đồ Plotly phân bố khía cạnh, cảm xúc, cấp độ ưu tiên | Nguyễn Viết Pháp | M7 (T12) |
| **1.7.3** | Khung tiếp nhận & Kiểm thử thời gian thực | Giao diện | Form nhập ticket tiếng Anh, chạy toàn trình hiển thị ABSA & Queue | Nguyễn Viết Pháp | M7 (T12) |
| **1.7.4** | Giao diện cập nhật trạng thái & Phân công | Giao diện | Component thao tác cập nhật trạng thái, phân công nhân sự | Nguyễn Viết Pháp | M7 (T12) |
| **1.8.1** | API điều phối tập trung (FastAPI) | Tích hợp | Endpoints `/tickets`, `/status`, tích hợp 2 bài toán | Lê Công Quốc Mỹ | M7 (T12) |
| **1.8.2** | Bộ kiểm thử tích hợp luồng 2 bài toán | Tích hợp | Test script E2E từ text tiếng Anh thô -> ABSA -> Priority -> DB | Nguyễn Phương Thảo | M8 (T13) |
| **1.8.3** | Bộ kịch bản kiểm thử tình huống biên | Tích hợp | Kịch bản văn bản dài, không khía cạnh, ngoại ngữ gắn cờ | Nguyễn Phương Thảo | M8 (T13) |
| **1.8.4** | Bộ dữ liệu demo giả lập tích hợp sẵn | Tích hợp | Script tự động nạp 50–100 ticket CSKH tiếng Anh mẫu | Nguyễn Viết Pháp | M8 (T13) |
| **1.8.5** | Bản phát hành đóng gói hoàn chỉnh | Tích hợp | Release v3.0 trên GitHub, script chạy 1 dòng `run_app.bat` | Cả nhóm | M8 (T13) |

---

## 4. TỪ ĐIỂN WBS CHI TIẾT (WBS DICTIONARY)

### Nhóm 1.1: Quản trị dự án & Hồ sơ học phần (Project Management)

#### WBS 1.1.1: Bộ hồ sơ khởi tạo dự án v3.0
- **Phạm vi:** Soạn thảo, chuẩn hóa và bảo vệ Project Charter cùng bảng đăng ký các bên liên quan (Stakeholder Register) Version 3.0; định hình rõ ranh giới chuyên biệt tiếng Anh, tích hợp mô hình ABSA Zero-shot NLI và phân tách thành 2 bài toán độc lập.
- **Sản phẩm bàn giao:** File `Project-Charter-Ticket-Triage-System.md` Version 3.0.
- **Tiêu chí nghiệm thu:** Mục tiêu SMART rõ ràng, phân ranh giới phạm vi mạch lạc, đầy đủ chữ ký phê duyệt.
- **Chủ sở hữu:** Võ Tấn Đức (PM) | **Milestone:** M1 (Tuần 2).

#### WBS 1.1.2: Bản kế hoạch phạm vi & Từ điển WBS v3.0
- **Phạm vi:** Phân rã toàn bộ phạm vi sản phẩm và công việc thành cây WBS có mã số phân cấp theo chuẩn PMI; xây dựng từ điển WBS cho từng gói công việc bám sát 2 bài toán kỹ thuật.
- **Sản phẩm bàn giao:** File `WBS-Ticket-Triage-System.md` Version 3.0 hoàn chỉnh.
- **Tiêu chí nghiệm thu:** Tuân thủ quy tắc 100%, 100% leaf node là danh từ/cụm danh từ bàn giao, đầy đủ acceptance criteria.
- **Chủ sở hữu:** Võ Tấn Đức (PM) | **Milestone:** M1 (Tuần 2).

#### WBS 1.1.3: Hệ thống theo dõi tiến độ Agile & Bảng Kanban
- **Phạm vi:** Khởi tạo GitHub Projects Board theo mô hình Kanban (To do → In Progress → In Review → Done); tạo các Issue Templates; chuyển đổi toàn bộ công việc WBS thành GitHub Issues có gán nhãn story points và liên kết Milestones.
- **Sản phẩm bàn giao:** Bảng GitHub Projects Board hoạt động trực tiếp.
- **Tiêu chí nghiệm thu:** 100% gói công việc WBS có Issue tương ứng; quy trình chuyển cột mượt mà.
- **Chủ sở hữu:** Võ Tấn Đức (PM) | **Milestone:** M1 (Tuần 2).

#### WBS 1.1.4: Sổ theo dõi rủi ro & Nhật ký thay đổi phạm vi
- **Phạm vi:** Khởi tạo và cập nhật định kỳ Risk Register (tập trung rủi ro về độ trễ NLI, tài nguyên GPU Colab); duy trì Scope Change Control Log ghi nhận lịch sử chuyển giao từ v2.0 sang v3.0.
- **Sản phẩm bàn giao:** Risk Register v1/v2 và Scope Change Control Log.
- **Tiêu chí nghiệm thu:** Rủi ro được lượng hóa cụ thể; thay đổi phạm vi có lý do và phân tích tác động đầy đủ.
- **Chủ sở hữu:** Võ Tấn Đức (PM) | **Milestone:** M4 (Tuần 7), M8 (Tuần 13).

#### WBS 1.1.5: Bộ hồ sơ minh chứng hoàn tất & Báo cáo đồ án
- **Phạm vi:** Thu thập, đóng gói toàn bộ minh chứng quy trình (commit history, PR review, issue tracking, biên bản họp sprint); hoàn thiện báo cáo kỹ thuật tổng kết và slide thuyết trình.
- **Sản phẩm bàn giao:** Thư mục Evidence Package, Báo cáo kỹ thuật tổng kết, Slide bảo vệ.
- **Tiêu chí nghiệm thu:** Đầy đủ minh chứng theo rubric môn học; phản ánh trung thực kết quả thực nghiệm.
- **Chủ sở hữu:** Cả nhóm (Đức điều phối chính) | **Milestone:** M9 (Tuần 14), M10 (Tuần 15).

---

### Nhóm 1.2: Hạ tầng kỹ thuật, Môi trường & Dữ liệu (Infrastructure & Data)

#### WBS 1.2.1: Kho lưu trữ mã nguồn & Luồng kiểm thử tự động
- **Phạm vi:** Thiết lập GitHub Repository với quy tắc bảo vệ nhánh cho `main` và `dev`; cài đặt cấu trúc thư mục (`src/`, `tests/`, `configs/`, `data/`); cấu hình workflow GitHub Actions tự động kiểm tra flake8, black và pytest khi tạo PR.
- **Sản phẩm bàn giao:** Repository GitHub có bảo vệ nhánh; workflow `.github/workflows/ci.yml`.
- **Tiêu chí nghiệm thu:** Không thể merge trực tiếp vào `main` khi chưa qua review và CI pass.
- **Chủ sở hữu:** Lê Công Quốc Mỹ (Tech Lead) | **Milestone:** M1 (Tuần 2).

#### WBS 1.2.2: Môi trường huấn luyện GPU & Tệp cấu hình thư viện
- **Phạm vi:** Cấu hình môi trường Google Colab / Kaggle Notebooks có GPU T4 miễn phí; kiểm tra PyTorch và CUDA; xây dựng tệp `requirements.txt` chuẩn hóa các thư viện (`transformers`, `datasets`, `peft`, `accelerate`, `sqlalchemy`, `streamlit`, `fastapi`).
- **Sản phẩm bàn giao:** Notebook mẫu huấn luyện kết nối GPU; tệp `requirements.txt` chuẩn hóa.
- **Tiêu chí nghiệm thu:** Cài đặt thành công không lỗi dependency; chạy được test tensor trên GPU T4.
- **Chủ sở hữu:** Nguyễn Văn Lê Duy | **Milestone:** M2 (Tuần 4).

#### WBS 1.2.3: Bộ dữ liệu phản hồi CSKH tiếng Anh chuẩn hóa
- **Phạm vi:** Thu thập tập dữ liệu phản hồi thương mại công khai tiếng Anh (trích xuất tập con từ Amazon Reviews hoặc các tập ticket CSKH tiếng Anh công khai); thực hiện phân tích khám phá dữ liệu (EDA), phân chia train/val/test theo tỷ lệ 80/10/10.
- **Sản phẩm bàn giao:** Thư mục dữ liệu đã làm sạch (`data/processed/`) kèm báo cáo thống kê EDA.
- **Tiêu chí nghiệm thu:** Dữ liệu sạch, không trùng lặp, định dạng chuẩn JSONL/CSV nạp được vào HuggingFace Datasets.
- **Chủ sở hữu:** Nguyễn Văn Lê Duy | **Milestone:** M2 (Tuần 4).

#### WBS 1.2.4: Tập dữ liệu kiểm thử 150–200 ticket CSKH gán nhãn thủ công
- **Phạm vi:** Biên soạn bộ 150–200 ticket CSKH tiếng Anh mô phỏng thực tế; tiến hành gán nhãn thủ công độc lập bởi ít nhất 2 thành viên về: các khía cạnh đề cập, cảm xúc từng khía cạnh, mức độ ưu tiên dự kiến [0–1] và cấp độ ưu tiên; đo lường độ đồng thuận inter-annotator agreement.
- **Sản phẩm bàn giao:** Tệp `testset_human_labeled.json` (150–200 ticket tiếng Anh có nhãn đầy đủ).
- **Tiêu chí nghiệm thu:** Mức độ đồng thuận nội bộ nhóm đạt Cohen's Kappa ≥ 0.80; dữ liệu bao phủ đủ các tình huống khẩn cấp, phàn nàn và hỏi đáp.
- **Chủ sở hữu:** Nguyễn Phương Thảo (QA) | **Milestone:** M3 (Tuần 6).

#### WBS 1.2.5: Bộ template giả thuyết NLI & Cấu hình danh mục khía cạnh CSKH
- **Phạm vi:** Xây dựng danh mục các khía cạnh nghiệp vụ CSKH chính (`CUSTOMER_SERVICE`, `SHIPPING`, `PRODUCT_QUALITY`, `REFUND_PAYMENT`, `GENERAL`) cùng các mẫu câu giả thuyết (Hypothesis Templates) chuẩn hóa cho suy luận NLI (ví dụ: *"This text is about {aspect}"* và *"The customer feels {sentiment} about {aspect}"*).
- **Sản phẩm bàn giao:** Tệp cấu hình `configs/aspect_hypotheses.yaml`.
- **Tiêu chí nghiệm thu:** Mẫu câu giả thuyết rõ nghĩa, tối ưu cho mô hình NLI nhận diện sắc thái cảm xúc.
- **Chủ sở hữu:** Nguyễn Văn Lê Duy | **Milestone:** M3 (Tuần 6).

#### WBS 1.2.6: Bộ dữ liệu khía cạnh chuẩn hóa benchmark
- **Phạm vi:** Chuẩn bị tập dữ liệu khía cạnh đối chuẩn (SemEval Laptop domain hoặc Customer Support Aspect dataset) đã chuẩn hóa sang định dạng cặp khía cạnh - cảm xúc phục vụ đánh giá so sánh mô hình.
- **Sản phẩm bàn giao:** Thư mục dữ liệu benchmark (`data/benchmark/`).
- **Tiêu chí nghiệm thu:** 100% mẫu có nhãn chuẩn; script nạp dữ liệu đánh giá chạy tự động.
- **Chủ sở hữu:** Nguyễn Văn Lê Duy | **Milestone:** M5 (Tuần 9).

#### WBS 1.2.7: Bảng ánh xạ khía cạnh CSKH & Báo cáo độ đồng thuận
- **Phạm vi:** Xây dựng bảng quy chuẩn ánh xạ các nhãn khía cạnh từ dữ liệu gốc sang các nhóm khía cạnh nghiệp vụ CSKH của dự án; thẩm định độc lập bởi 2 thành viên và đo lường độ tin cậy.
- **Sản phẩm bàn giao:** Tệp ánh xạ `configs/aspect_mapping.json` và Báo cáo đo lường chỉ số Cohen's Kappa.
- **Tiêu chí nghiệm thu:** Độ đồng thuận ánh xạ đạt Cohen's Kappa ≥ 0.70; các quy tắc phân nhóm không bị chồng chéo.
- **Chủ sở hữu:** Nguyễn Phương Thảo (QA) | **Milestone:** M5 (Tuần 9).

---

### Nhóm 1.3: Module 1 — Tiền xử lý văn bản tiếng Anh & Lọc trước khía cạnh

#### WBS 1.3.1: Bộ chuẩn hóa văn bản tiếng Anh
- **Phạm vi:** Xây dựng module làm sạch dữ liệu văn bản tiếng Anh: chuẩn hóa Unicode NFC, xử lý rút gọn chuỗi ký tự lặp (ví dụ: `terribleeee!!!!` → `terrible!`), loại bỏ mã HTML, URLs và địa chỉ email gây nhiễu mô hình.
- **Sản phẩm bàn giao:** Module `src/preprocessing/normalizer.py`.
- **Tiêu chí nghiệm thu:** Chạy đúng trên 100% test cases mẫu; bảo toàn các dấu câu biểu đạt cảm xúc và từ viết hoa thể hiện mức độ bức xúc.
- **Chủ sở hữu:** Lê Công Quốc Mỹ (Tech Lead) | **Milestone:** M3 (Tuần 6).

#### WBS 1.3.2: Bộ xác thực ngôn ngữ & Gắn cờ ngoại lệ
- **Phạm vi:** Xây dựng bộ xác thực ngôn ngữ sử dụng `langdetect`: kiểm tra văn bản đầu vào; nếu là tiếng Anh (`en`) -> tiếp tục chuyển vào pipeline; nếu phát hiện ngôn ngữ khác -> gắn cờ `needs_manual_review = True` và chuyển thẳng về hàng đợi chờ xem xét thủ công.
- **Sản phẩm bàn giao:** Module `src/preprocessing/lang_validator.py`.
- **Tiêu chí nghiệm thu:** Nhận diện và cho qua chính xác văn bản tiếng Anh ≥ 98%; gắn cờ an toàn các ngoại ngữ khác.
- **Chủ sở hữu:** Lê Công Quốc Mỹ (Tech Lead) | **Milestone:** M3 (Tuần 6).

#### WBS 1.3.3: Bộ lọc trước từ khóa khía cạnh
- **Phạm vi:** Tích hợp cơ chế lọc từ khóa trước (Keyword Pre-filtering): quét sự xuất hiện của các từ khóa đặc trưng cho từng khía cạnh trước khi chạy mô hình NLI để chỉ kích hoạt suy luận trên những khía cạnh có liên quan, giúp giảm 2x-3x thời gian xử lý mỗi ticket.
- **Sản phẩm bàn giao:** Module `src/preprocessing/keyword_prefilter.py`.
- **Tiêu chí nghiệm thu:** Không bỏ sót các khía cạnh cốt lõi có tín hiệu rõ ràng; tăng tốc độ xử lý rõ rệt so với chạy NLI brute-force toàn bộ khía cạnh.
- **Chủ sở hữu:** Nguyễn Văn Lê Duy | **Milestone:** M3 (Tuần 6).

#### WBS 1.3.4: Giao diện tiền xử lý tích hợp & Test suite
- **Phạm vi:** Tích hợp các bước làm sạch, xác thực và lọc trước thành hàm `preprocess_ticket(text)`; xuất ra dictionary cấu trúc chuẩn (`clean_text`, `is_english`, `detected_aspect_candidates`, `needs_manual_review`); viết bộ unit tests kiểm thử các trường hợp chuỗi rỗng, icon emoji, văn bản quá dài.
- **Sản phẩm bàn giao:** Module `src/preprocessing/pipeline.py` và tệp test `tests/test_preprocessing.py`.
- **Tiêu chí nghiệm thu:** 100% unit tests pass trên CI; xử lý an toàn không gây crash với mọi chuỗi đầu vào bất thường.
- **Chủ sở hữu:** Lê Công Quốc Mỹ (Tech Lead) | **Milestone:** M3 (Tuần 6).

---

### Nhóm 1.4: Module 2 — Bài toán 1: Hệ thống mô hình phân tích khía cạnh ABSA Zero-shot NLI

#### WBS 1.4.1: Pipeline Zero-shot NLI Baseline (NLI Baseline Pipeline)
- **Phạm vi:** Xây dựng thành phần phân tích suy luận giả thuyết phục vụ bài toán ABSA; nạp mô hình pretrained NLI (`valhalla/distilbart-mnli-12-3` hoặc `MoritzLaurer/deberta-v3-base-zeroshot-v1.1-all-33`); xây dựng luồng suy luận baseline kiểm tra độ chính xác trên dữ liệu CSKH tiếng Anh.
- **Sản phẩm bàn giao:** Module `src/absa/nli_baseline.py`.
- **Tiêu chí nghiệm thu:** Chạy được suy luận zero-shot NLI trên GPU Colab/CPU; xuất ra xác suất entailment/contradiction cho từng cặp giả thuyết.
- **Chủ sở hữu:** Nguyễn Văn Lê Duy | **Milestone:** M3 (Tuần 6).

#### WBS 1.4.2: Bộ quản lý khía cạnh nghiệp vụ CSKH
- **Phạm vi:** Xây dựng lớp `AspectManager` cấu hình danh mục khía cạnh CSKH linh hoạt qua tệp YAML (`config/aspects.yaml`); hỗ trợ phân cấp khía cạnh cốt lõi (Tier 1: Customer Service, Shipping, Product Quality, Refund) và khía cạnh mở rộng (Tier 2); hỗ trợ cập nhật danh mục khía cạnh mà không cần sửa mã nguồn.
- **Sản phẩm bàn giao:** Module `src/absa/aspect_manager.py` và tệp `config/aspects.yaml`.
- **Tiêu chí nghiệm thu:** Nạp và truy vấn khía cạnh linh hoạt; liên kết mượt mà với bộ lọc từ khóa và pipeline NLI.
- **Chủ sở hữu:** Nguyễn Văn Lê Duy | **Milestone:** M5 (Tuần 9).

#### WBS 1.4.3: Mô hình ABSA Zero-shot NLI fine-tuned trên dữ liệu CSKH tiếng Anh
- **Phạm vi:** Tinh chỉnh mô hình Zero-shot NLI trên tập dữ liệu phản hồi CSKH tiếng Anh đã chuẩn bị (áp dụng LoRA qua thư viện `peft` để tối ưu tài nguyên trên Colab T4); tối ưu hóa phân loại cảm xúc theo 3 trạng thái (Positive, Negative, Neutral) cho từng khía cạnh; lưu checkpoint tốt nhất.
- **Sản phẩm bàn giao:** Checkpoint mô hình fine-tuned và script huấn luyện `src/absa/train_nli.py`.
- **Tiêu chí nghiệm thu:** Huấn luyện hội tụ ổn định; cải thiện độ chính xác và khả năng phân biệt sắc thái tiêu cực trong ngữ cảnh CSKH so với zero-shot nguyên bản.
- **Chủ sở hữu:** Nguyễn Văn Lê Duy | **Milestone:** M5 (Tuần 9).

#### WBS 1.4.4: Bộ đánh giá hiệu năng & Ma trận nhầm lẫn mô hình ABSA
- **Phạm vi:** Đánh giá độc lập mô hình ABSA trên tập dữ liệu kiểm thử; tính toán các chỉ số F1-macro trên từng khía cạnh, Accuracy, ma trận nhầm lẫn cho từng khía cạnh CSKH; đối chiếu với baseline Zero-shot ban đầu.
- **Sản phẩm bàn giao:** Báo cáo đánh giá hiệu năng mô hình `reports/absa_evaluation_report.md`.
- **Tiêu chí nghiệm thu:** Đạt chỉ số cam kết **F1-macro per-aspect ≥ 0.78** trên tập kiểm thử; được QA phê duyệt đóng băng mô hình.
- **Chủ sở hữu:** Nguyễn Phương Thảo (QA) | **Milestone:** M5 (Tuần 9).

#### WBS 1.4.5: Giao diện API suy luận phân tích khía cạnh (ABSA Subsystem Output)
- **Phạm vi:** Xây dựng hàm suy luận `predict_aspects(text)` tích hợp đầy đủ bộ lọc từ khóa và mô hình NLI đã đóng băng; trả về danh sách có cấu trúc chuẩn gồm các khía cạnh phát hiện được, cảm xúc tương ứng và độ tin cậy `confidence` [0.0 - 1.0].
- **Sản phẩm bàn giao:** Module `src/absa/predictor.py`.
- **Tiêu chí nghiệm thu:** Thời gian suy luận trung bình < 300ms/ticket trên GPU; trả về JSON có cấu trúc chuẩn hóa sẵn sàng kết nối sang Bài toán 2 (Priority Engine).
- **Chủ sở hữu:** Nguyễn Văn Lê Duy | **Milestone:** M5 (Tuần 9).

---

### Nhóm 1.5: Module 3 — Bài toán 2: Bộ tính điểm ưu tiên nghiệp vụ (Rule-Based Priority Engine)

#### WBS 1.5.1: Bộ từ điển từ khóa khẩn cấp tiếng Anh & Trọng số khía cạnh
- **Phạm vi:** Xây dựng danh mục các từ khóa khẩn cấp tiếng Anh trong CSKH (`urgent`, `asap`, `immediately`, `lawsuit`, `fraud`, `scam`, `cancel`, `refund`, `broken`, `stolen`, `chargeback`, v.v.); thiết lập bảng trọng số nghiệp vụ cho các khía cạnh (`CUSTOMER_SERVICE`: 1.0, `REFUND_PAYMENT`: 1.0, `PRODUCT_QUALITY`: 0.8, `SHIPPING`: 0.7, `GENERAL`: 0.5); lưu trong tệp cấu hình độc lập `configs/priority_rules.yaml`.
- **Sản phẩm bàn giao:** Tệp cấu hình `configs/priority_rules.yaml`.
- **Tiêu chí nghiệm thu:** Cấu hình có thể điều chỉnh trọng số linh hoạt mà không cần sửa đổi mã nguồn.
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M4 (Tuần 7).

#### WBS 1.5.2: Bộ trích xuất cường độ cảm xúc & Cú pháp câu tiếng Anh
- **Phạm vi:** Xây dựng module phân tích các yếu tố ngữ cảnh thể hiện sự bức xúc cực độ: tỷ lệ từ viết hoa toàn bộ (CAPS LOCK), số lượng dấu chấm than liên tiếp (`!`, `!!`), dấu chấm hỏi dồn dập (`???`); tính toán hệ số tăng cường (Intensity Multiplier) để cộng dồn vào điểm ưu tiên.
- **Sản phẩm bàn giao:** Module `src/priority/intensity_extractor.py`.
- **Tiêu chí nghiệm thu:** Nhận diện chính xác các cú pháp bức xúc; không gây hiện tượng cộng dồn vượt ngưỡng quy định.
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M4 (Tuần 7).

#### WBS 1.5.3: Hàm tính toán điểm ưu tiên theo khía cạnh nghiêm trọng nhất (Worst-Aspect Priority)
- **Phạm vi:** Cài đặt hàm tính điểm ưu tiên cốt lõi `calculate_priority(aspects, text)` áp dụng công thức rule-based toán học:
  1. *Điểm nền (Base score):* Xác định khía cạnh tiêu cực có trọng số cao nhất (*worst-aspect-wins*), kết hợp độ tin cậy của mô hình;
  2. *Điểm phạt cộng dồn:* Phạt thêm nếu ticket chứa nhiều khía cạnh cùng tiêu cực;
  3. *Điểm bổ sung:* Trọng số từ khóa khẩn cấp và hệ số cường độ cú pháp;
  4. *Chuẩn hóa & Phân cấp:* Giới hạn trong $[0.0, 1.0]$, phân cấp 4 mức (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`);
  5. *Giải trình:* Sinh trường giải thích minh bạch `explanation` (Auditable).
- **Sản phẩm bàn giao:** Module `src/priority/priority_engine.py`.
- **Tiêu chí nghiệm thu:** 100% quyết định có `explanation` rõ ràng; điểm số chuẩn xác; tuyệt đối không dùng mô hình hộp đen để dự đoán priority.
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M6 (Tuần 11).

#### WBS 1.5.4: Bộ kiểm thử tự động & Báo cáo đồng thuận nghiệp vụ
- **Phạm vi:** Chạy kiểm thử tự động toàn bộ 150–200 ticket CSKH tiếng Anh thuộc tập testset gán nhãn thủ công (WBS 1.2.4) qua Priority Engine; so sánh mức độ trùng khớp giữa thứ tự ưu tiên của thuật toán và đánh giá của con người; phân tích ma trận đối soát và tính tỷ lệ đồng thuận.
- **Sản phẩm bàn giao:** Script kiểm thử `tests/test_priority_engine.py` và Báo cáo kiểm nghiệm độ đồng thuận `reports/priority_validation_report.md`.
- **Tiêu chí nghiệm thu:** Đạt chỉ số cam kết **mức độ đồng thuận ≥ 80%** giữa hệ thống và nhãn thủ công.
- **Chủ sở hữu:** Nguyễn Phương Thảo (QA) | **Milestone:** M6 (Tuần 11).

---

### Nhóm 1.6: Module 4 — Bài toán 2: Hệ thống hàng đợi & Lưu trữ dữ liệu (Queue & Storage)

#### WBS 1.6.1: Lược đồ CSDL vé hỗ trợ và khía cạnh & Đối tượng ORM
- **Phạm vi:** Thiết kế lược đồ CSDL quan hệ bằng SQLAlchemy ORM và SQLite gồm 2 bảng:
  - Bảng chính `tickets`: `id`, `raw_text`, `detected_lang`, `priority_score`, `priority_level`, `priority_explanation`, `dominant_aspect`, `status`, `assigned_to`, `needs_manual_review`, `created_at`, `updated_at`.
  - Bảng phụ `ticket_aspects`: `id`, `ticket_id` (Foreign Key cascade delete), `aspect_category`, `sentiment`, `confidence`.
- **Sản phẩm bàn giao:** Module `src/database/models.py` và script tạo database `src/database/init_db.py`.
- **Tiêu chí nghiệm thu:** Lược đồ CSDL chuẩn hóa, quan hệ 1-N toàn vẹn, khởi tạo CSDL SQLite thành công không lỗi.
- **Chủ sở hữu:** Lê Công Quốc Mỹ (Tech Lead) | **Milestone:** M2 (Tuần 4).

#### WBS 1.6.2: Bộ thao tác dữ liệu vé hỗ trợ và khía cạnh (DAL CRUD)
- **Phạm vi:** Xây dựng lớp truy cập dữ liệu (Data Access Layer - DAL): các hàm tạo mới vé kèm danh sách khía cạnh (`create_ticket_with_aspects`), đọc danh sách vé sắp xếp theo priority giảm dần (`get_tickets`), lấy chi tiết kèm khía cạnh (`get_ticket_by_id`), cập nhật trạng thái và người phụ trách (`update_ticket_status`).
- **Sản phẩm bàn giao:** Module `src/database/repository.py`.
- **Tiêu chí nghiệm thu:** Thực thi đúng transaction an toàn, tự động rollback khi phát sinh lỗi, truy vấn nạp kèm bảng con (joined load) tối ưu.
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M4 (Tuần 7).

#### WBS 1.6.3: Cấu trúc hàng đợi ưu tiên nội bộ (`heapq`)
- **Phạm vi:** Xây dựng lớp cấu trúc dữ liệu hàng đợi ưu tiên trong bộ nhớ (In-memory Priority Queue) sử dụng module `heapq`: hỗ trợ `push`, `pop` vé ưu tiên cao nhất; xử lý xung đột đồng điểm theo thứ tự thời gian tiếp nhận FIFO (vé đến trước được phục vụ trước); tự động đồng bộ nạp lại hàng đợi từ CSDL khi khởi động lại ứng dụng.
- **Sản phẩm bàn giao:** Module `src/queue/priority_queue.py`.
- **Tiêu chí nghiệm thu:** Trả về vé có `priority_score` cao nhất với độ phức tạp $O(1)$ khi xem và $O(\log n)$ khi thêm/bớt; xử lý chuẩn xác trường hợp đồng điểm.
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M6 (Tuần 11).

#### WBS 1.6.4: Bộ quản lý vòng đời 4 trạng thái vé hỗ trợ
- **Phạm vi:** Cài đặt máy trạng thái (State Machine) quản trị luồng xử lý của vé qua 4 trạng thái: Mới tiếp nhận (`new`) → Đã phân công (`assigned`) → Đang xử lý (`in_progress`) → Đã giải quyết (`resolved`); kiểm soát chặt chẽ các bước chuyển trạng thái hợp lệ.
- **Sản phẩm bàn giao:** Module `src/queue/state_manager.py`.
- **Tiêu chí nghiệm thu:** Chặn thành công các bước nhảy trạng thái sai quy trình; tự động ghi nhận thời gian cập nhật `updated_at`.
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M6 (Tuần 11).

---

### Nhóm 1.7: Module 5 — Giao diện điều phối & Trực quan hóa dữ liệu (Dashboard Subsystem)

#### WBS 1.7.1: Giao diện hộp thư ưu tiên & Bảng danh sách vé hỗ trợ
- **Phạm vi:** Xây dựng giao diện hòm thư thông minh (Triage Inbox) trên Streamlit: danh sách vé hỗ trợ tiếng Anh được sắp xếp tự động theo thứ tự ưu tiên giảm dần; hiển thị huy hiệu màu sắc trực quan (Đỏ: CRITICAL, Cam: HIGH, Vàng: MEDIUM, Xanh: LOW); hiển thị khía cạnh nổi bật và các bộ lọc tìm kiếm.
- **Sản phẩm bàn giao:** Module giao diện `src/dashboard/views/inbox_view.py`.
- **Tiêu chí nghiệm thu:** Giao diện tải nhanh, hiển thị thông tin trực quan, tự động cập nhật vị trí danh sách khi có vé mới.
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M7 (Tuần 12).

#### WBS 1.7.2: Bảng điều khiển phân tích thống kê khía cạnh cảm xúc
- **Phạm vi:** Xây dựng trang tổng quan thống kê (Analytics Dashboard) sử dụng thư viện Plotly: trực quan hóa phân bố các khía cạnh phàn nàn nhiều nhất (Aspect Distribution), biểu đồ cảm xúc theo từng khía cạnh, biểu đồ phân bố mức độ ưu tiên, và tiến độ xử lý trạng thái vé.
- **Sản phẩm bàn giao:** Module giao diện `src/dashboard/views/analytics_view.py`.
- **Tiêu chí nghiệm thu:** Các biểu đồ hiển thị tương tác mượt mà, tự động cập nhật số liệu từ CSDL SQLite.
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M7 (Tuần 12).

#### WBS 1.7.3: Khung tiếp nhận & Kiểm thử phân loại vé thời gian thực
- **Phạm vi:** Xây dựng khung mô phỏng trực tiếp (Live Simulator Panel): cho phép nhập bất kỳ đoạn văn bản ticket tiếng Anh nào; nhấn nút phân tích để kích hoạt pipeline 2 bài toán chạy ngầm và hiển thị ngay lập tức: các khía cạnh trích xuất kèm cảm xúc, điểm ưu tiên, căn cứ giải thích `explanation` và vị trí trong hàng đợi.
- **Sản phẩm bàn giao:** Component `src/dashboard/components/simulator.py`.
- **Tiêu chí nghiệm thu:** Phản hồi kết quả trực quan trong vòng 1–2 giây; hiển thị minh bạch từng bước xử lý của pipeline.
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M7 (Tuần 12).

#### WBS 1.7.4: Giao diện thao tác cập nhật trạng thái & Phân công xử lý
- **Phạm vi:** Xây dựng các thành phần tương tác trên giao diện cho phép nhân viên CSKH click xem chi tiết vé và danh sách khía cạnh, gán nhân sự phụ trách, chọn cập nhật trạng thái tiến độ (`in_progress`, `resolved`); dữ liệu được lưu tức thì vào SQLite và làm mới trạng thái trên giao diện.
- **Sản phẩm bàn giao:** Component `src/dashboard/components/ticket_actions.py`.
- **Tiêu chí nghiệm thu:** Thao tác cập nhật tức thì, có thông báo toast thành công; đồng bộ trạng thái ngay lập tức vào CSDL.
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M7 (Tuần 12).

---

### Nhóm 1.8: Tích hợp toàn hệ thống, Kiểm thử & Đóng gói bàn giao

#### WBS 1.8.1: Giao diện lập trình ứng dụng điều phối tập trung (FastAPI Core Pipeline API)
- **Phạm vi:** Xây dựng hàm điều phối toàn trình `process_ticket_pipeline(raw_text)` kết nối tuần tự Bài toán 1 (ABSA Subsystem) sang Bài toán 2 (Priority & Queue Subsystem); đóng gói thành RESTful API sử dụng FastAPI: `POST /tickets` (tiếp nhận vé mới, chạy pipeline và lưu trữ), `GET /tickets` (lấy danh sách theo thứ tự ưu tiên), `GET /tickets/{id}` (chi tiết vé), `PATCH /tickets/{id}/status` (cập nhật trạng thái).
- **Sản phẩm bàn giao:** Ứng dụng FastAPI hoàn chỉnh `src/api/main.py`.
- **Tiêu chí nghiệm thu:** 100% endpoints trả về mã HTTP status chuẩn, có Swagger UI tự động tại `/docs`; tích hợp thông suốt 2 bài toán.
- **Chủ sở hữu:** Lê Công Quốc Mỹ (Tech Lead) | **Milestone:** M7 (Tuần 12).

#### WBS 1.8.2: Bộ kiểm thử tích hợp luồng xử lý toàn trình 2 bài toán
- **Phạm vi:** Xây dựng kịch bản kiểm thử tích hợp tự động (End-to-End Test Suite): kiểm tra chu trình hoàn chỉnh từ lúc nhập một vé tiếng Anh thô, qua tiền xử lý, mô hình ABSA NLI, tính điểm ưu tiên, đẩy vào hàng đợi `heapq`, lưu vào CSDL SQLite và hiển thị chính xác trên Dashboard Streamlit.
- **Sản phẩm bàn giao:** Tệp kiểm thử tích hợp `tests/test_end_to_end_pipeline.py`.
- **Tiêu chí nghiệm thu:** Toàn bộ chu trình vận hành thông suốt không lỗi ngoại lệ; dữ liệu đồng bộ nhất quán giữa API, CSDL và giao diện.
- **Chủ sở hữu:** Nguyễn Phương Thảo (QA) | **Milestone:** M8 (Tuần 13).

#### WBS 1.8.3: Bộ kịch bản kiểm thử tình huống biên & Ngoại lệ
- **Phạm vi:** Xây dựng và thực thi bộ kiểm thử các trường hợp dữ liệu xấu và tình huống ngoại lệ: chuỗi rỗng, văn bản dài hơn 2000 từ, văn bản chứa toàn ký tự đặc biệt, văn bản không phải tiếng Anh (bị gắn cờ xem xét thủ công), vé không chứa bất kỳ khía cạnh nào được nhận diện; xác minh hệ thống luôn xử lý an toàn có log ghi nhận.
- **Sản phẩm bàn giao:** Báo cáo kiểm thử biên `reports/edge_cases_test_report.md`.
- **Tiêu chí nghiệm thu:** Hệ thống không bao giờ bị crash hoặc trả về lỗi 500 không kiểm soát; các trường hợp lỗi đều được xử lý an toàn.
- **Chủ sở hữu:** Nguyễn Phương Thảo (QA) | **Milestone:** M8 (Tuần 13).

#### WBS 1.8.4: Bộ dữ liệu demo giả lập tích hợp sẵn
- **Phạm vi:** Xây dựng script tự động nạp (seed) bộ 50–100 ticket CSKH tiếng Anh mẫu đa dạng tình huống vào CSDL SQLite khi khởi động ứng dụng lần đầu; bao gồm đầy đủ các mức độ khẩn cấp, các trạng thái xử lý để phục vụ buổi thuyết trình demo trực tiếp trước hội đồng.
- **Sản phẩm bàn giao:** Script tạo dữ liệu mẫu `scripts/seed_demo_data.py`.
- **Tiêu chí nghiệm thu:** Chạy lệnh 1 dòng là có ngay cơ sở dữ liệu mẫu sinh động, sẵn sàng cho demo.
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M8 (Tuần 13).

#### WBS 1.8.5: Bản phát hành đóng gói hoàn chỉnh
- **Phạm vi:** Đóng gói toàn bộ mã nguồn, tài liệu và môi trường thành bản phát hành hoàn chỉnh trên GitHub Release; viết hướng dẫn cài đặt và triển khai chi tiết từng bước trong file `README.md`; cung cấp script khởi chạy 1 lệnh (`run_app.bat` / `run_app.sh`).
- **Sản phẩm bàn giao:** Bản phát hành chính thức trên GitHub, file `README.md` và script khởi chạy ứng dụng.
- **Tiêu chí nghiệm thu:** Người dùng mới có thể clone repository và khởi chạy toàn bộ hệ thống cục bộ trong vòng 5 phút theo tài liệu hướng dẫn.
- **Chủ sở hữu:** Cả nhóm (Lê Công Quốc Mỹ phụ trách kỹ thuật) | **Milestone:** M8 (Tuần 13).

---

## 5. MA TRẬN PHÂN CÔNG TRÁCH NHIỆM (RACI MATRIX)

> **Quy ước ký hiệu RACI:**
> - **R (Responsible):** Người trực tiếp thực hiện công việc chính và hoàn thành sản phẩm bàn giao.
> - **A (Accountable):** Người chịu trách nhiệm giải trình cuối cùng về tính đúng đắn và phê duyệt kết quả (duy nhất 1 người/gói công việc).
> - **C (Consulted):** Người được tham vấn chuyên môn, đóng góp ý kiến kỹ thuật hai chiều.
> - **I (Informed):** Người được thông báo kết quả tiến độ sau khi hoàn thành.

| Mã WBS | Gói công việc bàn giao | Võ Tấn Đức (PM) | Lê Công Quốc Mỹ (Tech Lead) | Nguyễn Văn Lê Duy (Lead Dev ABSA) | Nguyễn Viết Pháp (Lead Dev Priority/UI) | Nguyễn Phương Thảo (QA/QC) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **1.1** | **Quản trị dự án & Hồ sơ học phần** | **A / R** | C | I | I | C |
| 1.1.1 | Bộ hồ sơ khởi tạo dự án v3.0 | **A / R** | C | I | I | C |
| 1.1.2 | Bản kế hoạch phạm vi & Từ điển WBS v3.0 | **A / R** | C | I | I | C |
| 1.1.3 | Hệ thống theo dõi tiến độ Agile & Board | **A / R** | C | I | I | C |
| 1.1.4 | Sổ theo dõi rủi ro & Thay đổi phạm vi | **A / R** | C | I | I | C |
| 1.1.5 | Bộ hồ sơ minh chứng & Báo cáo đồ án | **A / R** | C | C | C | C |
| **1.2** | **Hạ tầng, Môi trường & Dữ liệu** | I | C | **A / R** | C | C |
| 1.2.1 | Kho lưu trữ mã nguồn & CI Actions | I | **A / R** | C | C | C |
| 1.2.2 | Môi trường GPU & Cấu hình thư viện | I | C | **A / R** | C | I |
| 1.2.3 | Bộ dữ liệu phản hồi CSKH tiếng Anh | I | C | **A / R** | I | C |
| 1.2.4 | Tập kiểm thử 150–200 ticket CSKH gán nhãn | I | C | C | C | **A / R** |
| 1.2.5 | Template giả thuyết NLI & Cấu hình khía cạnh | I | C | **A / R** | I | C |
| 1.2.6 | Bộ dữ liệu khía cạnh chuẩn hóa benchmark | I | C | **A / R** | I | C |
| 1.2.7 | Bảng ánh xạ khía cạnh CSKH & Độ đồng thuận | I | C | C | I | **A / R** |
| **1.3** | **Module 1 — Tiền xử lý & Lọc khía cạnh** | I | **A / R** | C | I | C |
| 1.3.1 | Bộ chuẩn hóa văn bản tiếng Anh | I | **A / R** | C | I | C |
| 1.3.2 | Bộ xác thực ngôn ngữ & Gắn cờ ngoại lệ | I | **A / R** | C | I | C |
| 1.3.3 | Bộ lọc trước từ khóa khía cạnh | I | C | **A / R** | I | C |
| 1.3.4 | Giao diện tiền xử lý tích hợp & Test suite | I | **A / R** | C | I | C |
| **1.4** | **Module 2 — Bài toán 1: ABSA Subsystem** | I | C | **A / R** | I | C |
| 1.4.1 | Pipeline Zero-shot NLI Baseline | I | C | **A / R** | I | C |
| 1.4.2 | Bộ quản lý khía cạnh nghiệp vụ CSKH | I | C | **A / R** | I | C |
| 1.4.3 | Mô hình ABSA Zero-shot NLI fine-tuned | I | C | **A / R** | I | C |
| 1.4.4 | Báo cáo đánh giá hiệu năng mô hình ABSA | I | C | C | I | **A / R** |
| 1.4.5 | Giao diện API suy luận phân tích khía cạnh | I | C | **A / R** | C | C |
| **1.5** | **Module 3 — Bài toán 2: Priority Engine** | I | C | I | **A / R** | C |
| 1.5.1 | Từ điển từ khóa khẩn cấp & Trọng số khía cạnh | I | C | I | **A / R** | C |
| 1.5.2 | Bộ trích xuất cường độ cảm xúc câu | I | C | I | **A / R** | C |
| 1.5.3 | Hàm tính điểm ưu tiên khía cạnh nghiêm trọng nhất | I | C | I | **A / R** | C |
| 1.5.4 | Báo cáo kiểm thử đồng thuận nghiệp vụ | I | C | I | C | **A / R** |
| **1.6** | **Module 4 — Bài toán 2: Queue & Storage** | I | C | I | **A / R** | C |
| 1.6.1 | Lược đồ CSDL vé hỗ trợ và khía cạnh & ORM | I | **A / R** | I | C | C |
| 1.6.2 | Bộ thao tác dữ liệu vé hỗ trợ (DAL CRUD) | I | C | I | **A / R** | C |
| 1.6.3 | Cấu trúc hàng đợi ưu tiên nội bộ `heapq` | I | C | I | **A / R** | C |
| 1.6.4 | Quản lý vòng đời 4 trạng thái vé | I | C | I | **A / R** | C |
| **1.7** | **Module 5 — Giao diện Dashboard** | I | C | I | **A / R** | C |
| 1.7.1 | Giao diện hộp thư ưu tiên | I | C | I | **A / R** | C |
| 1.7.2 | Bảng điều khiển phân tích thống kê khía cạnh | I | C | I | **A / R** | C |
| 1.7.3 | Khung tiếp nhận & Kiểm thử realtime | I | C | I | **A / R** | C |
| 1.7.4 | Giao diện cập nhật trạng thái & Phân công | I | C | I | **A / R** | C |
| **1.8** | **Tích hợp, Kiểm thử & Đóng gói** | **A** | C | C | C | C |
| 1.8.1 | API điều phối tập trung (FastAPI) | I | **A / R** | C | C | C |
| 1.8.2 | Kiểm thử tích hợp luồng 2 bài toán | I | C | C | C | **A / R** |
| 1.8.3 | Kịch bản kiểm thử tình huống biên | I | C | C | C | **A / R** |
| 1.8.4 | Bộ dữ liệu demo giả lập tích hợp sẵn | I | C | I | **A / R** | C |
| 1.8.5 | Bản phát hành đóng gói hoàn chỉnh | C | **A / R** | C | C | C |

---

## 6. KẾ HOẠCH BÀN GIAO THEO MILESTONES & KIỂM SOÁT THAY ĐỔI

### 6.1. Tiến độ tích hợp các gói WBS theo Milestones

```text
[Tuần 1-2] M1: Khởi tạo & Lập kế hoạch ──► WBS 1.1.1, 1.1.2, 1.1.3, 1.2.1
   │
[Tuần 3-4] M2: Thiết kế Kiến trúc & CSDL ──► WBS 1.2.2, 1.2.3, 1.6.1
   │
[Tuần 5-6] M3: Tiền xử lý & NLI Baseline ──► WBS 1.2.4, 1.2.5, 1.3.1, 1.3.2, 1.3.3, 1.3.4, 1.4.1
   │
[Tuần 7]   M4: Sơ kết Sprint 1 & Priority Config ──► WBS 1.1.4, 1.5.1, 1.5.2, 1.6.2
   │
[Tuần 8-9] M5: Fine-tune ABSA NLI Model ──► WBS 1.2.6, 1.2.7, 1.4.2, 1.4.3, 1.4.4, 1.4.5 ──► [ĐÓNG BĂNG BÀI TOÁN 1]
   │
[Tuần 10-11] M6: Priority Engine & Queue ──► WBS 1.5.3, 1.5.4, 1.6.3, 1.6.4 ──► [ĐÓNG BĂNG BÀI TOÁN 2]
   │
[Tuần 12]  M7: Dashboard & Tích hợp API ──► WBS 1.7.1, 1.7.2, 1.7.3, 1.7.4, 1.8.1
   │
[Tuần 13]  M8: Đóng băng toàn hệ thống ──► WBS 1.8.2, 1.8.3, 1.8.4, 1.8.5 ──► [CODE FREEZE TOÀN BỘ]
   │
[Tuần 14]  M9: Hồ sơ minh chứng hoàn tất ──► WBS 1.1.5 (Evidence Package, Báo cáo kỹ thuật)
   │
[Tuần 15]  M10: Bảo vệ đồ án tốt nghiệp ──► Thuyết trình & Demo trực tiếp trước Hội đồng
```

### 6.2. Quy tắc kiểm soát thay đổi phạm vi (Scope Baseline Control)
1. **Nguyên tắc "Hợp đồng giao tiếp giữa 2 bài toán (API Contract)":** Đầu ra của Bài toán 1 (`predict_aspects`) và đầu vào của Bài toán 2 (`calculate_priority`) được đóng băng định dạng JSON ngay từ M2. Điều này đảm bảo 2 nhánh phát triển (Lê Duy phụ trách ABSA, Viết Pháp phụ trách Priority/Queue/UI) có thể phát triển và kiểm thử độc lập mà không bị phụ thuộc chặn tiến độ.
2. **Quy tắc an toàn tiến độ:** Tại cột mốc M5 (Tuần 9), mô hình ABSA NLI phải được đóng băng kỹ thuật. Nếu việc fine-tune gặp trở ngại về tài nguyên GPU, nhóm có quyền kích hoạt phương án dự phòng sử dụng trực tiếp mô hình Zero-shot NLI Pretrained đã tối ưu hóa bộ lọc từ khóa từ repo `conangamo/review_analysis` để đảm bảo thời gian cho Bài toán 2 và giao diện Dashboard.
3. **Quy trình thay đổi (Change Request Process):** Mọi thay đổi phát sinh sau khi WBS v3.0 được duyệt phải tạo GitHub Issue gắn nhãn `change-request`, được PM (Võ Tấn Đức) và Tech Lead (Lê Công Quốc Mỹ) đánh giá tác động trước khi thực hiện.
