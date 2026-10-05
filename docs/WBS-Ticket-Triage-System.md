# WORK BREAKDOWN STRUCTURE (WBS)
## Dự án: Hệ thống phân loại & định tuyến phản hồi khách hàng theo cảm xúc (*Sentiment-Driven Ticket Triage System*)
### Mã dự án: `TICKET-TRIAGE-01` | Học phần: Quản trị dự án phần mềm
### Nhóm thực hiện: *DogTowFaces* | Giảng viên hướng dẫn: *Nguyễn Thanh Tuấn*
### Phiên bản: Version 2.0 | Ngày lập: 05/10/2026

---

## 1. TỔNG QUAN & NGUYÊN TẮC PHÂN RÃ WBS

### 1.1. Mục đích tài liệu
Tài liệu này xác lập cấu trúc phân rã công việc chính thức (Work Breakdown Structure - WBS) cho dự án `TICKET-TRIAGE-01`. WBS đóng vai trò là đường cơ sở phạm vi (Scope Baseline), làm nền tảng cho việc lập kế hoạch tiến độ, ước lượng nỗ lực (Effort Estimation), phân bổ nhân sự (RACI), theo dõi trên GitHub Project Board và kiểm soát chất lượng bàn giao.

### 1.2. Các nguyên tắc phân rã chuẩn mực tuân thủ
Tài liệu được xây dựng chặt chẽ theo hướng dẫn thực hành của Viện Quản lý Dự án Quốc tế (PMI Practice Standard for WBS) và các yêu cầu học thuật của môn học:
1. **Nguyên tắc hướng sản phẩm bàn giao (Deliverable-Oriented Breakdown):** Các nút lá (leaf nodes) và các nút tổng hợp trong WBS đều được đặt tên bằng **danh từ / cụm danh từ chỉ sản phẩm, thành phần cụ thể** (ví dụ: *"Bộ tiền xử lý văn bản"*, *"Mô hình phân loại BERT"*), tuyệt đối không dùng động từ chỉ hành động (như "lập trình", "kiểm thử").
2. **Quy tắc 100% (The 100% Rule):** WBS bao trùm 100% toàn bộ công việc cần thực hiện trong phạm vi dự án (cả sản phẩm kỹ thuật lẫn hồ sơ quản lý dự án), không bỏ sót bất kỳ hạng mục nào và không chứa bất kỳ công việc nào nằm ngoài phạm vi được phê duyệt trong Project Charter.
3. **Độ sâu phân rã & Tính độc lập (Depth Heuristic):** Mỗi gói công việc (Work Package) ở cấp thấp nhất có quy mô tương ứng khoảng 1–2 tuần làm việc của 1–2 thành viên (phù hợp chu kỳ sprint), có tiêu chí nghiệm thu độc lập và có thể gán cho một chủ sở hữu duy nhất.
4. **Phân tầng phạm vi MoSCoW (MoSCoW Scope Hierarchy):**
   - **Tầng Bắt buộc (MUST-HAVE):** Hệ thống độc lập, hoàn chỉnh end-to-end xử lý phân loại cảm xúc cấp câu (Sentence-level) bằng mô hình họ **BERT**, tích hợp Priority Engine rule-based, hàng đợi `heapq`, cơ sở dữ liệu SQLite và Dashboard Streamlit. Tầng này bảo đảm 100% khả năng nghiệm thu đồ án độc lập.
   - **Tầng Mở rộng (SHOULD-HAVE):** Phân tích cảm xúc dựa trên khía cạnh (Aspect-Based Sentiment Analysis - ABSA) gồm phân loại cảm xúc theo nhóm khía cạnh (ACSA) và trích xuất thực thể khía cạnh (ABTE) bằng mô hình họ **BERT**, cùng tab phân tích chuyên sâu trên dashboard. Tầng này chỉ kích hoạt sau khi tầng Must-have đã hoàn tất và đóng băng tại mốc M5.

---

## 2. CÂY CẤU TRÚC PHÂN RÃ CÔNG VIỆC (WBS HIERARCHY TREE)

```text
1.0 Hệ thống phân loại & định tuyến phản hồi khách hàng theo cảm xúc (TICKET-TRIAGE-01)
├── 1.1 Quản trị dự án & Hồ sơ học phần (Project Management & Compliance)
│   ├── 1.1.1 Bộ hồ sơ khởi tạo dự án (Project Charter & Stakeholder Register) [MUST]
│   ├── 1.1.2 Bản kế hoạch phạm vi & Từ điển WBS (Scope Baseline & WBS Dictionary) [MUST]
│   ├── 1.1.3 Hệ thống theo dõi tiến độ Agile & Bảng Kanban (GitHub Projects & Issues) [MUST]
│   ├── 1.1.4 Sổ theo dõi rủi ro & Nhật ký thay đổi phạm vi (Risk & Change Log) [MUST]
│   └── 1.1.5 Bộ hồ sơ minh chứng hoàn tất & Báo cáo đồ án (Evidence Package) [MUST]
│
├── 1.2 Hạ tầng kỹ thuật, Môi trường & Dữ liệu (Infrastructure & Data Foundation)
│   ├── 1.2.1 Kho lưu trữ mã nguồn & Luồng kiểm thử tự động (GitHub Repo & CI Actions) [MUST]
│   ├── 1.2.2 Môi trường huấn luyện GPU & Tệp cấu hình thư viện (Colab/Kaggle & Config) [MUST]
│   ├── 1.2.3 Bộ dữ liệu phân loại câu tiếng Anh chuẩn hóa (Amazon Polarity Subset) [MUST]
│   ├── 1.2.4 Tập dữ liệu kiểm thử song ngữ mô phỏng gán nhãn thủ công (EN–VI Ticket Testset) [MUST]
│   ├── 1.2.5 Bộ dữ liệu kiểm chứng phân loại tiếng Việt (AIVIVN 2019 / UIT-VSFC) [MUST]
│   ├── 1.2.6 Bộ dữ liệu khía cạnh chuẩn hóa SemEval-2014 Laptop (ACSA & ABTE Parsed) [SHOULD]
│   └── 1.2.7 Bảng đối chiếu ánh xạ khía cạnh & Báo cáo độ đồng thuận (Aspect Mapping) [SHOULD]
│
├── 1.3 Module 1 — Bộ tiền xử lý & Cổng điều phối ngôn ngữ (Preprocessing & Language Gateway)
│   ├── 1.3.1 Bộ chuẩn hóa văn bản & Rút gọn ký tự lặp (Text Normalizer) [MUST]
│   ├── 1.3.2 Bộ phát hiện ngôn ngữ & Phân luồng tiếp nhận (Language Detector) [MUST]
│   ├── 1.3.3 Bộ dịch thuật máy tiếng Việt sang tiếng Anh (opus-mt-vi-en Gateway) [MUST]
│   ├── 1.3.4 Giao diện hàm tiền xử lý tích hợp & Bộ kiểm thử biên (Preprocessing Suite) [MUST]
│   └── 1.3.5 Bộ tiền xử lý bảo toàn chỉ số ký tự cho trích xuất khía cạnh (ABTE Text Suite) [SHOULD]
│
├── 1.4 Module 2 — Hệ thống mô hình phân loại cảm xúc & Khía cạnh (Model Subsystem)
│   ├── 1.4.1 Mô hình cảm xúc cơ sở (TF-IDF + LinearSVC / Naive Bayes Baseline) [MUST]
│   ├── 1.4.2 Bộ dữ liệu huấn luyện & Tokenizer mô hình BERT (BERT Data Pipeline) [MUST]
│   ├── 1.4.3 Mô hình học sâu BERT fine-tuned phân loại câu (BERT Sentence Classifier) [MUST]
│   ├── 1.4.4 Bộ đánh giá hiệu năng & Ma trận nhầm lẫn mô hình BERT (Model Eval Package) [MUST]
│   ├── 1.4.5 Giao diện API suy luận phân loại câu (Inference Service Module 2A) [MUST]
│   ├── 1.4.6 Mô hình họ BERT phân loại cảm xúc theo nhóm khía cạnh (BERT ACSA Classifier) [SHOULD]
│   ├── 1.4.7 Mô hình họ BERT trích xuất thực thể khía cạnh (BERT ABTE Token Classifier) [SHOULD]
│   └── 1.4.8 Giao diện API suy luận phân tích khía cạnh kép (Inference Service Module 2B) [SHOULD]
│
├── 1.5 Module 3 — Bộ tính điểm ưu tiên nghiệp vụ (Rule-Based Priority Engine)
│   ├── 1.5.1 Bộ từ điển từ khóa khẩn cấp & Quy tắc trọng số nghiệp vụ (Rule Config) [MUST]
│   ├── 1.5.2 Bộ trích xuất cường độ cảm xúc & Cú pháp câu (Intensity Extractor) [MUST]
│   ├── 1.5.3 Hàm tính toán điểm ưu tiên giải thích được (Explainable Priority Engine) [MUST]
│   ├── 1.5.4 Bộ kiểm thử tự động & Báo cáo đồng thuận nghiệp vụ (80% Agreement Test) [MUST]
│   └── 1.5.5 Bộ mở rộng ưu tiên theo khía cạnh nghiêm trọng nhất & Sự cố mới (ABSA Priority) [SHOULD]
│
├── 1.6 Module 4 — Hệ thống hàng đợi & Lưu trữ dữ liệu (Queue & Storage Subsystem)
│   ├── 1.6.1 Lược đồ cơ sở dữ liệu vé hỗ trợ & Đối tượng ánh xạ ORM (SQLite Ticket Schema) [MUST]
│   ├── 1.6.2 Bộ thao tác dữ liệu vé hỗ trợ (Ticket CRUD Data Access Layer) [MUST]
│   ├── 1.6.3 Cấu trúc hàng đợi ưu tiên nội bộ xử lý theo điểm số và thời gian (heapq Queue) [MUST]
│   ├── 1.6.4 Bộ quản lý vòng đời 4 trạng thái vé hỗ trợ (Ticket State Lifecycle Manager) [MUST]
│   └── 1.6.5 Lược đồ mở rộng bảng khía cạnh quan hệ khóa ngoại (ACSA & ABTE Schema) [SHOULD]
│
├── 1.7 Module 5 — Giao diện điều phối & Trực quan hóa dữ liệu (Dashboard Subsystem)
│   ├── 1.7.1 Giao diện hộp thư ưu tiên & Bảng danh sách vé hỗ trợ (Inbox View Component) [MUST]
│   ├── 1.7.2 Bảng điều khiển phân tích thống kê cảm xúc & Ngôn ngữ (Analytics View) [MUST]
│   ├── 1.7.3 Khung tiếp nhận & Kiểm thử phân loại vé hỗ trợ thời gian thực (Live Test Panel) [MUST]
│   ├── 1.7.4 Giao diện thao tác cập nhật trạng thái & Phân công xử lý (Action Component) [MUST]
│   ├── 1.7.5 Thẻ giao diện phân tích khía cạnh chuyên sâu (ABSA Breakdown & Heatmap Tab) [SHOULD]
│   └── 1.7.6 Bộ hiển thị nổi bật thực thể khía cạnh trong văn bản (Aspect Term Highlighting) [SHOULD]
│
└── 1.8 Tích hợp toàn hệ thống, Kiểm thử & Đóng gói bàn giao (Integration & Deployment)
    ├── 1.8.1 Giao diện lập trình ứng dụng điều phối tập trung (FastAPI Core Pipeline API) [MUST]
    ├── 1.8.2 Bộ kiểm thử tích hợp luồng xử lý toàn trình Must-have (End-to-End Test Suite) [MUST]
    ├── 1.8.3 Bộ kịch bản kiểm thử tình huống biên & Ngoại lệ (Edge Case Test Cases) [MUST]
    ├── 1.8.4 Bộ dữ liệu demo giả lập tích hợp sẵn (Pre-seeded Demo Dataset) [MUST]
    ├── 1.8.5 Bộ kiểm thử tích hợp tầng mở rộng khía cạnh (ABSA Integration Test Suite) [SHOULD]
    └── 1.8.6 Bản phát hành đóng gói ứng dụng hoàn chỉnh (Packaged Release & Deployment) [MUST]
```

---

## 3. BẢNG DANH MỤC PHÂN RÃ WBS TỔNG HỢP

| Mã WBS | Tên gói công việc / Deliverable | Tầng MoSCoW | Thành phần bàn giao chính | Người phụ trách | Milestone |
| :---: | :--- | :---: | :--- | :---: | :---: |
| **1.1.1** | Hồ sơ khởi tạo dự án | **MUST** | `Project-Charter.md`, Stakeholder Register | Võ Tấn Đức | M1 (T2) |
| **1.1.2** | Bản kế hoạch phạm vi & Từ điển WBS | **MUST** | `WBS.md`, WBS Dictionary, Scope Baseline | Võ Tấn Đức | M1 (T2) |
| **1.1.3** | Bảng theo dõi tiến độ Agile | **MUST** | GitHub Projects Board, Issues template, Milestones | Võ Tấn Đức | M1 (T2) |
| **1.1.4** | Sổ theo dõi rủi ro & Thay đổi phạm vi | **MUST** | Risk Register, Scope Change Log | Võ Tấn Đức | M4, M8 |
| **1.1.5** | Hồ sơ minh chứng & Báo cáo đồ án | **MUST** | Evidence Package, Báo cáo kỹ thuật, Slide | Cả nhóm | M9, M10 |
| **1.2.1** | Kho mã nguồn & CI Actions | **MUST** | GitHub Repo, nhánh `main`/`dev`, flake8/pytest CI | Lê Công Quốc Mỹ | M1 (T2) |
| **1.2.2** | Môi trường GPU & Cấu hình thư viện | **MUST** | Google Colab/Kaggle notebook mẫu, `requirements.txt` | Nguyễn Văn Lê Duy | M2 (T4) |
| **1.2.3** | Bộ dữ liệu phân loại câu tiếng Anh | **MUST** | Tập train/val/test (~30k) trích từ Amazon Polarity | Nguyễn Văn Lê Duy | M2 (T4) |
| **1.2.4** | Tập kiểm thử ticket mô phỏng song ngữ | **MUST** | Tập 150–200 ticket CSKH (EN & VI) gán nhãn thủ công | Nguyễn Phương Thảo | M3 (T6) |
| **1.2.5** | Dữ liệu kiểm chứng phân loại tiếng Việt | **MUST** | Tập dữ liệu AIVIVN 2019 / UIT-VSFC chuẩn hóa | Nguyễn Văn Lê Duy | M3 (T6) |
| **1.2.6** | Bộ dữ liệu khía cạnh SemEval-2014 Laptop | **SHOULD** | File XML đã parse ra format ACSA và BIO ABTE | Nguyễn Văn Lê Duy | M6 (T11) |
| **1.2.7** | Bảng ánh xạ khía cạnh & Báo cáo đồng thuận | **SHOULD** | Bảng map 7 aspect CSKH, điểm Cohen's Kappa ≥ 0.7 | Nguyễn Phương Thảo | M6 (T11) |
| **1.3.1** | Bộ chuẩn hóa văn bản | **MUST** | Module `normalize_text()`, Unicode NFC, regex clean | Lê Công Quốc Mỹ | M3 (T6) |
| **1.3.2** | Bộ phát hiện ngôn ngữ & Phân luồng | **MUST** | Module `detect_language()` (langdetect), cờ `needs_manual` | Lê Công Quốc Mỹ | M3 (T6) |
| **1.3.3** | Bộ dịch thuật máy VI -> EN | **MUST** | Module `translate_vi_to_en()` dùng `opus-mt-vi-en` | Nguyễn Văn Lê Duy | M3 (T6) |
| **1.3.4** | Giao diện hàm tiền xử lý & Test suite | **MUST** | Module `preprocess()` hoàn chỉnh + 10 unit test cases | Lê Công Quốc Mỹ | M3 (T6) |
| **1.3.5** | Bộ tiền xử lý bảo toàn chỉ số ABTE | **SHOULD** | Module `preprocess_for_abte()` giữ nguyên character offset | Lê Công Quốc Mỹ | M7 (T12) |
| **1.4.1** | Mô hình cảm xúc cơ sở Baseline | **MUST** | Pipeline TF-IDF + LinearSVC, F1-macro ≥ 0.75 | Nguyễn Văn Lê Duy | M3 (T6) |
| **1.4.2** | Pipeline nạp dữ liệu cho mô hình BERT | **MUST** | Script tokenize, batch collator, DataLoader PyTorch | Nguyễn Văn Lê Duy | M5 (T9) |
| **1.4.3** | Mô hình học sâu BERT fine-tuned (câu) | **MUST** | Model BERT fine-tuned 3 lớp, checkpoint, trọng số | Nguyễn Văn Lê Duy | M5 (T9) |
| **1.4.4** | Báo cáo đánh giá hiệu năng mô hình BERT | **MUST** | F1-macro ≥ 0.85, Precision/Recall, Confusion Matrix | Nguyễn Phương Thảo | M5 (T9) |
| **1.4.5** | Giao diện suy luận phân loại câu (2A) | **MUST** | Module `predict_sentiment(text)` trả về nhãn + confidence | Nguyễn Văn Lê Duy | M5 (T9) |
| **1.4.6** | Mô hình họ BERT phân loại khía cạnh ACSA | **SHOULD** | Model họ BERT fine-tuned đa nhãn cho 7 category CSKH | Nguyễn Văn Lê Duy | M6 (T11) |
| **1.4.7** | Mô hình họ BERT trích xuất thực thể ABTE | **SHOULD** | Model họ BERT Token Classification (BIO tagging) | Nguyễn Văn Lê Duy | M7 (T12) |
| **1.4.8** | Giao diện suy luận khía cạnh kép (2B) | **SHOULD** | Module `predict_aspects_acsa()`, `predict_aspects_abte()` | Nguyễn Văn Lê Duy | M7 (T12) |
| **1.5.1** | Bộ từ điển từ khóa khẩn cấp & Trọng số | **MUST** | File cấu hình JSON/YAML danh mục khẩn cấp EN–VI | Nguyễn Viết Pháp | M4 (T7) |
| **1.5.2** | Bộ trích xuất cường độ cảm xúc câu | **MUST** | Module nhận diện chữ hoa (CAPS), dấu cảm thán, dấu hỏi | Nguyễn Viết Pháp | M4 (T7) |
| **1.5.3** | Hàm tính toán điểm ưu tiên giải thích được | **MUST** | Module `calculate_priority()` xuất điểm [0–1] & explanation | Nguyễn Viết Pháp | M6 (T11) |
| **1.5.4** | Báo cáo kiểm thử đồng thuận nghiệp vụ | **MUST** | Báo cáo kiểm nghiệm mức đồng thuận ≥ 80% trên 150 ticket | Nguyễn Phương Thảo | M6 (T11) |
| **1.5.5** | Bộ mở rộng ưu tiên theo khía cạnh & Sự cố mới | **SHOULD** | Logic worst-aspect + bonus khía cạnh + novel issue flag | Nguyễn Viết Pháp | M7 (T12) |
| **1.6.1** | Lược đồ CSDL vé hỗ trợ & ORM | **MUST** | SQLAlchemy model `Ticket`, tệp CSDL SQLite `tickets.db` | Lê Công Quốc Mỹ | M2 (T4) |
| **1.6.2** | Bộ thao tác dữ liệu vé hỗ trợ (CRUD) | **MUST** | Module data access (thêm, cập nhật trạng thái, truy vấn) | Nguyễn Viết Pháp | M4 (T7) |
| **1.6.3** | Cấu trúc hàng đợi ưu tiên `heapq` | **MUST** | Lớp `TicketQueue` hỗ trợ heapify, push, pop theo priority | Nguyễn Viết Pháp | M6 (T11) |
| **1.6.4** | Bộ quản lý vòng đời 4 trạng thái vé | **MUST** | State manager: `new` -> `assigned` -> `in_progress` -> `resolved` | Nguyễn Viết Pháp | M6 (T11) |
| **1.6.5** | Lược đồ mở rộng bảng khía cạnh quan hệ | **SHOULD** | Model `TicketAspectACSA` và `TicketAspectABTE` | Lê Công Quốc Mỹ | M7 (T12) |
| **1.7.1** | Giao diện hộp thư ưu tiên | **MUST** | Trang danh sách vé sắp xếp priority giảm dần, phân màu | Nguyễn Viết Pháp | M7 (T12) |
| **1.7.2** | Bảng điều khiển phân tích thống kê | **MUST** | Biểu đồ Plotly phân bố độ ưu tiên, cảm xúc, ngôn ngữ | Nguyễn Viết Pháp | M7 (T12) |
| **1.7.3** | Khung tiếp nhận & Kiểm thử thời gian thực | **MUST** | Form nhập text trực tiếp, hiển thị kết quả phân loại | Nguyễn Viết Pháp | M7 (T12) |
| **1.7.4** | Giao diện cập nhật trạng thái & Phân công | **MUST** | Thao tác chuyển đổi trạng thái và gán nhân sự xử lý | Nguyễn Viết Pháp | M7 (T12) |
| **1.7.5** | Thẻ giao diện phân tích khía cạnh chuyên sâu | **SHOULD** | Tab Dashboard trực quan hóa phân bố cảm xúc theo khía cạnh | Nguyễn Viết Pháp | M8 (T13) |
| **1.7.6** | Bộ hiển thị nổi bật thực thể khía cạnh | **SHOULD** | Component highlight vị trí từ khóa khía cạnh trong văn bản | Nguyễn Viết Pháp | M8 (T13) |
| **1.8.1** | API điều phối tập trung (FastAPI) | **MUST** | Endpoints `/tickets`, `/status`, pipeline tích hợp | Lê Công Quốc Mỹ | M7 (T12) |
| **1.8.2** | Bộ kiểm thử tích hợp luồng Must-have | **MUST** | Test script end-to-end từ text thô -> DB -> Dashboard | Nguyễn Phương Thảo | M8 (T13) |
| **1.8.3** | Bộ kịch bản kiểm thử tình huống biên | **MUST** | Kịch bản chuỗi rỗng, văn bản dài, teencode, ngoại ngữ | Nguyễn Phương Thảo | M8 (T13) |
| **1.8.4** | Bộ dữ liệu demo giả lập tích hợp sẵn | **MUST** | Script nạp tự động 50–100 ticket đa dạng phục vụ demo | Nguyễn Viết Pháp | M8 (T13) |
| **1.8.5** | Bộ kiểm thử tích hợp tầng mở rộng ABSA | **SHOULD** | Test script luồng phân tích khía cạnh kép end-to-end | Nguyễn Phương Thảo | M8 (T13) |
| **1.8.6** | Bản phát hành đóng gói hoàn chỉnh | **MUST** | Release v1.0 / v2.0 trên GitHub, Docker/Script chạy 1 dòng | Cả nhóm | M8 (T13) |

---

## 4. TỪ ĐIỂN WBS CHI TIẾT (WBS DICTIONARY)

### Nhóm 1.1: Quản trị dự án & Hồ sơ học phần (Project Management)

#### WBS 1.1.1: Bộ hồ sơ khởi tạo dự án
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Soạn thảo, chuẩn hóa và bảo vệ Project Charter cùng bảng đăng ký các bên liên quan (Stakeholder Register) theo mẫu quy định của môn học; xác định rõ ràng bài toán nghiệp vụ, mục tiêu SMART, ranh giới phạm vi và nguyên tắc minh bạch về nguồn dữ liệu.
- **Sản phẩm bàn giao:** File `Project-Charter-Ticket-Triage-System.md` (Version 2.0 đã duyệt) và bảng ma trận quyền lực/mức quan tâm.
- **Tiêu chí nghiệm thu (Acceptance Criteria):** Có chữ ký phê duyệt của Giảng viên hướng dẫn; mục tiêu SMART cụ thể; phân định rõ ranh giới phạm vi; đầy đủ 13 phần theo chuẩn học phần.
- **Công nghệ / Tài nguyên:** Markdown, GitHub Documentation.
- **Chủ sở hữu (Owner):** Võ Tấn Đức (PM) | **Milestone:** M1 (Tuần 2).

#### WBS 1.1.2: Bản kế hoạch phạm vi & Từ điển WBS
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Phân rã toàn bộ phạm vi sản phẩm và công việc của dự án thành cây WBS có mã số phân cấp theo chuẩn PMBOK; xây dựng từ điển WBS mô tả chi tiết cho từng gói công việc bao gồm mô tả, tiêu chí nghiệm thu và phân công; áp dụng triệt để nguyên tắc 100% và phân tầng MoSCoW.
- **Sản phẩm bàn giao:** File `WBS-Ticket-Triage-System.md` hoàn chỉnh.
- **Tiêu chí nghiệm thu:** Tuân thủ quy tắc 100%; toàn bộ leaf node là deliverable (danh từ); đầy đủ acceptance criteria; được giảng viên hướng dẫn chấp thuận.
- **Chủ sở hữu:** Võ Tấn Đức (PM) | **Milestone:** M1 (Tuần 2).

#### WBS 1.1.3: Hệ thống theo dõi tiến độ Agile & Bảng Kanban
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Khởi tạo GitHub Projects Board theo mô hình Kanban (To do → In Progress → In Review → Done); tạo các Issue Templates cho Feature và Bug; chuyển đổi toàn bộ gói công việc WBS thành GitHub Issues có nhãn ước lượng effort (story points) và liên kết với GitHub Milestones (M1–M10).
- **Sản phẩm bàn giao:** Bảng GitHub Project Board hoạt động trực tiếp, hệ thống nhãn và issues liên kết đầy đủ.
- **Tiêu chí nghiệm thu:** 100% công việc WBS có Issue tương ứng; các cột trạng thái vận hành mượt mà; hiển thị trực quan tiến độ theo milestone.
- **Chủ sở hữu:** Võ Tấn Đức (PM) | **Milestone:** M1 (Tuần 2).

#### WBS 1.1.4: Sổ theo dõi rủi ro & Nhật ký thay đổi phạm vi
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Khởi tạo và cập nhật định kỳ Sổ theo dõi rủi ro (Risk Register) với xác suất, mức ảnh hưởng và giải pháp ứng phó; duy trì nhật ký kiểm soát thay đổi phạm vi (Scope Change Control Log) ghi nhận lịch sử điều chỉnh từ kế hoạch gốc sang kiến trúc mới.
- **Sản phẩm bàn giao:** Risk Register v1 (Tuần 7) và v2 (Tuần 13); Scope Change Control Log.
- **Tiêu chí nghiệm thu:** Rủi ro được nhận diện và xếp loại định lượng; có kế hoạch phòng ngừa cụ thể; mọi thay đổi phạm vi đều được ghi chép lý do và tác động rõ ràng.
- **Chủ sở hữu:** Võ Tấn Đức (PM) | **Milestone:** M4 (Tuần 7), M8 (Tuần 13).

#### WBS 1.1.5: Bộ hồ sơ minh chứng hoàn tất & Báo cáo đồ án
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Thu thập, đóng gói toàn bộ bằng chứng vận hành quy trình quản lý dự án (Evidence Package: lịch sử commit, PR review, issue burn-down, biên bản họp sprint); hoàn thiện tài liệu thuyết minh đồ án và slide báo cáo cuối kỳ.
- **Sản phẩm bàn giao:** Thư mục Evidence Package đầy đủ minh chứng, Báo cáo kỹ thuật tổng kết và Slide thuyết trình.
- **Tiêu chí nghiệm thu:** Đầy đủ minh chứng theo rubric môn học; báo cáo phản ánh trung thực kết quả đạt được; bảo vệ thành công trước hội đồng.
- **Chủ sở hữu:** Cả nhóm (Đức điều phối chính) | **Milestone:** M9 (Tuần 14), M10 (Tuần 15).

---

### Nhóm 1.2: Hạ tầng kỹ thuật, Môi trường & Dữ liệu (Infrastructure & Data Foundation)

#### WBS 1.2.1: Kho lưu trữ mã nguồn & Luồng kiểm thử tự động
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Thiết lập GitHub Repository chính thức với các quy tắc bảo vệ nhánh (Branch Protection) cho `main` và `dev`; thiết lập cấu trúc thư mục module chuẩn (`src/`, `tests/`, `configs/`, `data/`); cài đặt GitHub Actions tự động kiểm tra định dạng code (flake8/black) và chạy unit tests khi mở PR.
- **Sản phẩm bàn giao:** Repository GitHub có bảo vệ nhánh; tệp workflow `.github/workflows/ci.yml`.
- **Tiêu chí nghiệm thu:** Không thể merge trực tiếp vào `main` khi chưa có PR approval; workflow CI chạy tự động và thông báo trạng thái pass/fail chính xác.
- **Chủ sở hữu:** Lê Công Quốc Mỹ (Tech Lead) | **Milestone:** M1 (Tuần 2).

#### WBS 1.2.2: Môi trường huấn luyện GPU & Tệp cấu hình thư viện
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Cấu hình môi trường Google Colab / Kaggle Notebooks có GPU T4 miễn phí phục vụ huấn luyện; kiểm tra tính tương thích của CUDA và PyTorch; xây dựng tệp `requirements.txt` chuẩn hóa các thư viện (transformers, datasets, peft, accelerate, sqlalchemy, streamlit, fastapi).
- **Sản phẩm bàn giao:** Notebook mẫu huấn luyện kết nối GPU; tệp `requirements.txt` được khóa phiên bản.
- **Tiêu chí nghiệm thu:** Cài đặt môi trường thành công không bị xung đột dependency; chạy được test tensor trên GPU T4.
- **Chủ sở hữu:** Nguyễn Văn Lê Duy | **Milestone:** M2 (Tuần 4).

#### WBS 1.2.3: Bộ dữ liệu phân loại câu tiếng Anh chuẩn hóa
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Thu thập tập dữ liệu phản hồi thương mại công khai tiếng Anh (trích xuất tập con cân bằng ~30.000 mẫu từ `amazon_polarity` hoặc tập phản hồi CSKH tương đương); bổ sung lớp Trung tính (Neutral); thực hiện phân tích khám phá dữ liệu (EDA), phân chia tập train/val/test theo tỷ lệ 80/10/10.
- **Sản phẩm bàn giao:** Thư mục dữ liệu đã làm sạch (`data/sentence/`) kèm báo cáo thống kê EDA (phân bố nhãn, độ dài văn bản).
- **Tiêu chí nghiệm thu:** Dữ liệu không chứa mẫu rỗng; tỷ lệ nhãn cân bằng; định dạng chuẩn JSONL/CSV nạp được vào HuggingFace Datasets.
- **Chủ sở hữu:** Nguyễn Văn Lê Duy | **Milestone:** M2 (Tuần 4).

#### WBS 1.2.4: Tập dữ liệu kiểm thử song ngữ mô phỏng gán nhãn thủ công
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Thu thập và biên soạn bộ 150–200 ticket CSKH mô phỏng phản ánh đúng nghiệp vụ thực tế (gồm cả tiếng Anh và tiếng Việt); tiến hành gán nhãn thủ công độc lập bởi ít nhất 2 thành viên về: nhãn cảm xúc, mức độ ưu tiên dự kiến [0–1] và cấp ưu tiên; đo lường độ đồng thuận giữa 2 người gán nhãn.
- **Sản phẩm bàn giao:** Tệp `testset_human_labeled.json` (150–200 ticket có metadata đầy đủ).
- **Tiêu chí nghiệm thu:** Mức độ đồng thuận nội bộ nhóm (Inter-annotator Agreement) đạt Cohen's Kappa ≥ 0.8; dữ liệu bao phủ đủ các tình huống khẩn cấp, phàn nàn và hỏi đáp thông thường.
- **Chủ sở hữu:** Nguyễn Phương Thảo (QA) | **Milestone:** M3 (Tuần 6).

#### WBS 1.2.5: Bộ dữ liệu kiểm chứng phân loại tiếng Việt
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Chuẩn bị tập dữ liệu đánh giá tiếng Việt công khai (AIVIVN 2019 / UIT-VSFC); lọc và chuẩn hóa dữ liệu để làm tập đối chuẩn (benchmark) kiểm tra chất lượng của luồng Translate-then-Classify.
- **Sản phẩm bàn giao:** Tập dữ liệu tiếng Việt chuẩn hóa (`data/benchmark_vi/`).
- **Tiêu chí nghiệm thu:** Tệp dữ liệu có nhãn ground-truth rõ ràng; script nạp tự động chạy mượt mà.
- **Chủ sở hữu:** Nguyễn Văn Lê Duy | **Milestone:** M3 (Tuần 6).

#### WBS 1.2.6: Bộ dữ liệu khía cạnh chuẩn hóa SemEval-2014 Laptop
- **Phân tầng:** SHOULD-HAVE
- **Mô tả phạm vi:** Tải bộ dữ liệu SemEval-2014 Task 4 (Laptop domain); viết script parse đồng thời cả 2 dạng nhãn: (1) Khía cạnh & cảm xúc cho ACSA, (2) Từ khóa khía cạnh & vị trí offset cho ABTE từ cùng một tệp nguồn XML; chuyển đổi nhãn sang định dạng BIO sequence tagging.
- **Sản phẩm bàn giao:** Thư mục dữ liệu khía cạnh chuẩn hóa (`data/absa/` gồm train/val/test).
- **Tiêu chí nghiệm thu:** 100% mẫu được trích xuất chính xác cặp nhãn; kiểm tra đối soát thủ công ngẫu nhiên 50 câu không có lỗi lệch offset (token-offset misalignment).
- **Chủ sở hữu:** Nguyễn Văn Lê Duy | **Milestone:** M6 (Tuần 11).

#### WBS 1.2.7: Bảng đối chiếu ánh xạ khía cạnh & Báo cáo độ đồng thuận
- **Phân tầng:** SHOULD-HAVE
- **Mô tả phạm vi:** Xây dựng bảng quy chuẩn ánh xạ các nhãn khía cạnh từ SemEval sang 7 nhóm nghiệp vụ chăm sóc khách hàng của dự án (`CUSTOMER_SERVICE`, `PRODUCT_QUALITY`, `REFUND_PAYMENT`, `SHIPPING`, `PRODUCT_AVAILABILITY`, `PACKAGING`, `GENERAL`); thực hiện mapping độc lập bởi 2 thành viên và đo lường độ tin cậy.
- **Sản phẩm bàn giao:** File tài liệu ánh xạ `aspect_category_mapping.json` và Báo cáo đo lường chỉ số Cohen's Kappa.
- **Tiêu chí nghiệm thu:** Điểm độ đồng thuận ánh xạ đạt Cohen's Kappa ≥ 0.70; các quy tắc phân nhóm không có sự chồng chéo mâu thuẫn.
- **Chủ sở hữu:** Nguyễn Phương Thảo (QA) | **Milestone:** M6 (Tuần 11).

---

### Nhóm 1.3: Module 1 — Bộ tiền xử lý & Cổng điều phối ngôn ngữ (Preprocessing & Language Gateway)

#### WBS 1.3.1: Bộ chuẩn hóa văn bản & Rút gọn ký tự lặp
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Xây dựng module làm sạch dữ liệu văn bản thô: chuẩn hóa Unicode về định dạng chuẩn NFC, xử lý rút gọn chuỗi ký tự lặp quá mức (ví dụ: `quá tệeeeee!!!!!` → `quá tệe!`), loại bỏ mã HTML, thẻ XML, liên kết URLs và địa chỉ email gây nhiễu mô hình.
- **Sản phẩm bàn giao:** Module Python `src/preprocessing/normalizer.py`.
- **Tiêu chí nghiệm thu:** Chạy đúng trên 100% test cases mẫu; văn bản đầu ra sạch ký tự rác nhưng không làm mất ý nghĩa ngữ cảnh và các dấu câu biểu đạt cảm xúc quan trọng.
- **Chủ sở hữu:** Lê Công Quốc Mỹ (Tech Lead) | **Milestone:** M3 (Tuần 6).

#### WBS 1.3.2: Bộ phát hiện ngôn ngữ & Phân luồng tiếp nhận
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Xây dựng thành phần nhận diện ngôn ngữ sử dụng thư viện `langdetect`; thiết lập cơ chế phân luồng logic: nếu là Tiếng Anh (`en`) -> chuyển thẳng; nếu là Tiếng Việt (`vi`) -> chuyển qua bộ dịch; nếu là ngôn ngữ khác -> gắn cờ `needs_manual_review = True` và route về hàng đợi xử lý thủ công.
- **Sản phẩm bàn giao:** Module Python `src/preprocessing/lang_detector.py`.
- **Tiêu chí nghiệm thu:** Nhận diện chính xác ≥ 95% trên tập test song ngữ; gắn cờ chính xác cho các ngôn ngữ ngoài phạm vi; có cơ chế xử lý ngoại lệ cho câu quá ngắn (< 20 ký tự).
- **Chủ sở hữu:** Lê Công Quốc Mỹ (Tech Lead) | **Milestone:** M3 (Tuần 6).

#### WBS 1.3.3: Bộ dịch thuật máy tiếng Việt sang tiếng Anh
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Tích hợp mô hình dịch máy cục bộ mã nguồn mở `Helsinki-NLP/opus-mt-vi-en` thông qua thư viện HuggingFace Transformers; xây dựng cơ chế dịch văn bản tiếng Việt sang tiếng Anh tự động để đưa vào mô hình phân loại cảm xúc cốt lõi; bổ sung cơ chế lưu bộ đệm (cache) cho các văn bản trùng lặp để tối ưu tốc độ.
- **Sản phẩm bàn giao:** Module Python `src/preprocessing/translator.py`.
- **Tiêu chí nghiệm thu:** Dịch thuật thông suốt trên GPU/CPU cục bộ; thời gian dịch trung bình < 1 giây/ticket trên Colab; bảo toàn được các sắc thái tiêu cực trong câu sau khi dịch.
- **Chủ sở hữu:** Nguyễn Văn Lê Duy | **Milestone:** M3 (Tuần 6).

#### WBS 1.3.4: Giao diện hàm tiền xử lý tích hợp & Bộ kiểm thử biên
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Tích hợp các thành phần con thành hàm `preprocess(text)` thống nhất; trả về cấu trúc dictionary chuẩn (`clean_text`, `detected_lang`, `translated_text`, `needs_manual`, `processing_text`); viết bộ unit test kiểm thử các ca biên ngoại lệ (chuỗi rỗng, văn bản toàn khoảng trắng, icon emoji, teencode, văn bản cực dài).
- **Sản phẩm bàn giao:** Module `src/preprocessing/pipeline.py` và tệp test `tests/test_preprocessing.py`.
- **Tiêu chí nghiệm thu:** 100% unit tests pass trên CI; xử lý an toàn không gây crash hệ thống với mọi chuỗi đầu vào bất thường.
- **Chủ sở hữu:** Lê Công Quốc Mỹ (Tech Lead) | **Milestone:** M3 (Tuần 6).

#### WBS 1.3.5: Bộ tiền xử lý bảo toàn chỉ số ký tự cho trích xuất khía cạnh
- **Phân tầng:** SHOULD-HAVE
- **Mô tả phạm vi:** Xây dựng biến thể tiền xử lý chuyên biệt `preprocess_for_abte(text)` dành riêng cho bài toán ABTE; đảm bảo không làm thay đổi vị trí chỉ mục (character offset start_idx, end_idx) của từ trong câu gốc để phục vụ việc trích xuất và hiển thị highlight chính xác trên giao diện.
- **Sản phẩm bàn giao:** Hàm `preprocess_for_abte()` trong `src/preprocessing/abte_preprocessor.py`.
- **Tiêu chí nghiệm thu:** Độ lệch vị trí ký tự bằng 0 trên toàn bộ tập kiểm thử SemEval ABTE.
- **Chủ sở hữu:** Lê Công Quốc Mỹ (Tech Lead) | **Milestone:** M7 (Tuần 12).

---

### Nhóm 1.4: Module 2 — Hệ thống mô hình phân loại cảm xúc & Khía cạnh (Model Subsystem)

#### WBS 1.4.1: Mô hình cảm xúc cơ sở Baseline
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Xây dựng mô hình học máy truyền thống làm chuẩn so sánh cơ sở (Baseline): Trích xuất đặc trưng TF-IDF (n-gram 1–2, tối đa 10.000 features) kết hợp với thuật toán LinearSVC hoặc Multinomial Naive Bayes; đánh giá F1-macro trên tập kiểm thử để làm mốc đối chứng kỹ thuật.
- **Sản phẩm bàn giao:** Script huấn luyện `src/models/baseline_train.py` và tệp mô hình đã lưu `baseline_model.joblib`.
- **Tiêu chí nghiệm thu:** Đạt chỉ số F1-macro ≥ 0.75 trên tập kiểm thử; thời gian huấn luyện và suy luận nhanh làm căn cứ đánh giá độ vượt trội của mô hình học sâu.
- **Chủ sở hữu:** Nguyễn Văn Lê Duy | **Milestone:** M3 (Tuần 6).

#### WBS 1.4.2: Bộ dữ liệu huấn luyện & Tokenizer mô hình BERT
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Thiết lập pipeline tiền xử lý dữ liệu cho mô hình họ **BERT**: tải Pretrained Tokenizer tương ứng, xây dựng hàm mã hóa văn bản (tokenization, padding, truncation theo `max_length = 128/256`), tạo Custom PyTorch Dataset và DataLoader tối ưu hóa bộ nhớ cho GPU.
- **Sản phẩm bàn giao:** Module `src/models/dataset_loader.py`.
- **Tiêu chí nghiệm thu:** Chuyển đổi dữ liệu chính xác sang định dạng PyTorch tensors; DataLoader hỗ trợ batching hiệu quả không gây tràn bộ nhớ GPU (OOM).
- **Chủ sở hữu:** Nguyễn Văn Lê Duy | **Milestone:** M5 (Tuần 9).

#### WBS 1.4.3: Mô hình học sâu BERT fine-tuned phân loại câu
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Tinh chỉnh mô hình học sâu dựa trên kiến trúc **BERT** (sử dụng thư viện HuggingFace `AutoModelForSequenceClassification`) cho bài toán phân loại 3 lớp cảm xúc (Negative, Neutral, Positive); thiết lập các siêu tham số huấn luyện (learning rate, weight decay, warmup steps, early stopping); lưu checkpoint tốt nhất.
- **Sản phẩm bàn giao:** Checkpoint mô hình fine-tuned hoàn chỉnh và mã nguồn huấn luyện `src/models/train_bert_sentence.py`.
- **Tiêu chí nghiệm thu:** Huấn luyện hội tụ ổn định; không bị hiện tượng quá khớp (overfitting); lưu trữ an toàn mô hình và tokenizer sẵn sàng phục vụ suy luận.
- **Chủ sở hữu:** Nguyễn Văn Lê Duy | **Milestone:** M5 (Tuần 9).

#### WBS 1.4.4: Bộ đánh giá hiệu năng & Ma trận nhầm lẫn mô hình BERT
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Đánh giá độc lập mô hình **BERT** đã huấn luyện trên tập kiểm thử độc lập; tính toán chi tiết các thước đo hiệu năng (F1-macro, F1-weighted, Precision, Recall cho từng lớp); vẽ biểu đồ ma trận nhầm lẫn (Confusion Matrix); đối chiếu trực tiếp với kết quả của mô hình Baseline.
- **Sản phẩm bàn giao:** Báo cáo đánh giá hiệu năng mô hình `reports/model_evaluation_report.md` kèm biểu đồ Confusion Matrix.
- **Tiêu chí nghiệm thu:** Đạt chỉ số cam kết **F1-macro ≥ 0.85** trên tập kiểm thử; chứng minh sự cải thiện rõ rệt so với Baseline (≥ +0.07 F1-macro); được QA phê duyệt đóng băng mô hình.
- **Chủ sở hữu:** Nguyễn Phương Thảo (QA) | **Milestone:** M5 (Tuần 9).

#### WBS 1.4.5: Giao diện API suy luận phân loại câu (Module 2A)
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Xây dựng hàm suy luận nhẹ `predict_sentiment(text)` nạp mô hình BERT đã đóng băng; tối ưu hóa suy luận (chuyển sang eval mode, torch.no_grad, softmax); trả về kết quả cấu trúc chuẩn gồm: nhãn cảm xúc dự đoán (`sentiment`) và điểm xác suất độ tin cậy (`confidence` từ 0.0 đến 1.0).
- **Sản phẩm bàn giao:** Module `src/models/predictor_sentence.py` kèm bộ kiểm thử suy luận nhanh.
- **Tiêu chí nghiệm thu:** Thời gian suy luận < 100ms trên GPU hoặc < 300ms trên CPU; cấu trúc output chuẩn hóa kết nối thông suốt với Module 3.
- **Chủ sở hữu:** Nguyễn Văn Lê Duy | **Milestone:** M5 (Tuần 9).

#### WBS 1.4.6: Mô hình họ BERT phân loại cảm xúc theo nhóm khía cạnh (ACSA)
- **Phân tầng:** SHOULD-HAVE
- **Mô tả phạm vi:** Xây dựng mô hình học sâu họ **BERT** cho bài toán phân loại đa nhãn cảm xúc theo 7 nhóm khía cạnh nghiệp vụ CSKH (Multi-label Classification); áp dụng kỹ thuật fine-tuning nhẹ (như LoRA qua thư viện `peft` nếu cần tiết kiệm tài nguyên); huấn luyện trên tập SemEval Laptop đã ánh xạ.
- **Sản phẩm bàn giao:** Mã nguồn huấn luyện `src/models/train_acsa.py` và checkpoint mô hình ACSA.
- **Tiêu chí nghiệm thu:** Đạt F1-macro trên từng khía cạnh (per-aspect) ≥ 0.75; xuất ra danh sách các khía cạnh phát hiện kèm cảm xúc và confidence.
- **Chủ sở hữu:** Nguyễn Văn Lê Duy | **Milestone:** M6 (Tuần 11).

#### WBS 1.4.7: Mô hình họ BERT trích xuất thực thể khía cạnh (ABTE)
- **Phân tầng:** SHOULD-HAVE
- **Mô tả phạm vi:** Xây dựng mô hình họ **BERT** với đầu phân loại cấp độ token (Token Classification head) phục vụ trích xuất thực thể khía cạnh theo định dạng nhãn BIO; huấn luyện nhận diện chính xác cụm từ chỉ khía cạnh trong văn bản; đánh giá bằng thư viện `seqeval`.
- **Sản phẩm bàn giao:** Mã nguồn huấn luyện `src/models/train_abte.py` và checkpoint mô hình ABTE.
- **Tiêu chí nghiệm thu:** Đạt F1 cấp độ thực thể (entity-level F1) ≥ 0.65 trên tập kiểm thử; trích xuất được vị trí bắt đầu và kết thúc của cụm từ trong văn bản.
- **Chủ sở hữu:** Nguyễn Văn Lê Duy | **Milestone:** M7 (Tuần 12).

#### WBS 1.4.8: Giao diện API suy luận phân tích khía cạnh kép (Module 2B)
- **Phân tầng:** SHOULD-HAVE
- **Mô tả phạm vi:** Xây dựng các hàm wrapper suy luận `predict_aspects_acsa(text)` và `predict_aspects_abte(text)`; tích hợp cơ chế cờ tính năng (Feature Flag) `ACSA_MODEL_AVAILABLE` và `ABTE_MODEL_AVAILABLE` để hệ thống tự động nhận diện và kích hoạt khi mô hình sẵn sàng mà không ảnh hưởng luồng Must-have.
- **Sản phẩm bàn giao:** Module `src/models/predictor_absa.py`.
- **Tiêu chí nghiệm thu:** Chạy song song độc lập; trả về cấu trúc mảng JSON chuẩn; nếu mô hình tắt, hệ thống vẫn hoạt động bình thường với luồng câu.
- **Chủ sở hữu:** Nguyễn Văn Lê Duy | **Milestone:** M7 (Tuần 12).

---

### Nhóm 1.5: Module 3 — Bộ tính điểm ưu tiên nghiệp vụ (Rule-Based Priority Engine)

#### WBS 1.5.1: Bộ từ điển từ khóa khẩn cấp & Trọng số nghiệp vụ
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Nghiên cứu và xây dựng bộ từ điển danh mục các từ khóa khẩn cấp và nhạy cảm trong dịch vụ khách hàng (tố cáo, khiếu nại, lừa đảo, hủy dịch vụ, khẩn cấp, scam, refund, sue, chargeback...); phân cấp mức độ nghiêm trọng thành các trọng số định lượng minh bạch; lưu trữ trong file cấu hình độc lập (`configs/priority_rules.yaml`).
- **Sản phẩm bàn giao:** Tệp cấu hình quy tắc và danh sách từ khóa `configs/priority_rules.yaml`.
- **Tiêu chí nghiệm thu:** Bao quát đầy đủ các thuật ngữ nghiệp vụ song ngữ EN–VI phổ biến; cấu hình có thể cập nhật mà không cần sửa đổi mã nguồn.
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M4 (Tuần 7).

#### WBS 1.5.2: Bộ trích xuất cường độ cảm xúc & Cú pháp câu
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Xây dựng module phân tích các yếu tố ngữ cảnh thể hiện sự bức xúc cực độ: tỷ lệ từ viết hoa toàn bộ (CAPS LOCK), số lượng dấu chấm than liên tiếp (`!`, `!!`), dấu chấm hỏi nghi vấn dồn dập (`???`); tính toán hệ số tăng cường (Intensity Multiplier) để cộng dồn vào điểm ưu tiên.
- **Sản phẩm bàn giao:** Module Python `src/priority/intensity_extractor.py`.
- **Tiêu chí nghiệm thu:** Nhận diện chính xác các mẫu cú pháp biểu cảm bức xúc; không gây hiện tượng cộng dồn vượt ngưỡng quy định [0.0 – 1.0].
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M4 (Tuần 7).

#### WBS 1.5.3: Hàm tính toán điểm ưu tiên giải thích được
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Cài đặt hàm tính điểm cốt lõi `calculate_priority()` áp dụng công thức rule-based toán học: kết hợp điểm nền theo nhãn cảm xúc, độ tin cậy mô hình BERT, điểm cộng dồn từ khóa và cường độ; chuẩn hóa điểm số về khoảng [0.0 – 1.0]; phân cấp 4 mức ưu tiên (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`); sinh trường diễn giải nguyên nhân minh bạch (`explanation`).
- **Sản phẩm bàn giao:** Module `src/priority/priority_engine.py`.
- **Tiêu chí nghiệm thu:** Điểm số luôn nằm trong [0.0 – 1.0]; 100% quyết định đều có trường `explanation` giải trình rõ căn cứ tính điểm (auditable); không dùng bất kỳ mô hình hộp đen nào để dự đoán điểm.
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M6 (Tuần 11).

#### WBS 1.5.4: Bộ kiểm thử tự động & Báo cáo đồng thuận nghiệp vụ
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Chạy kiểm thử tự động toàn bộ 150–200 ticket thuộc tập dữ liệu kiểm thử gán nhãn thủ công (WBS 1.2.4) qua Priority Engine; so sánh mức độ trùng khớp giữa thứ tự ưu tiên của thuật toán và đánh giá của con người; xuất ma trận đối soát và tính tỷ lệ đồng thuận.
- **Sản phẩm bàn giao:** Script kiểm thử `tests/test_priority_engine.py` và Báo cáo nghiệm thu độ đồng thuận nghiệp vụ `reports/priority_validation_report.md`.
- **Tiêu chí nghiệm thu:** Đạt chỉ số cam kết **mức độ đồng thuận ≥ 80%** giữa hệ thống và nhãn thủ công; toàn bộ các ca sai lệch lớn đều được phân tích nguyên nhân và tinh chỉnh trọng số hợp lý.
- **Chủ sở hữu:** Nguyễn Phương Thảo (QA) | **Milestone:** M6 (Tuần 11).

#### WBS 1.5.5: Bộ mở rộng ưu tiên theo khía cạnh nghiêm trọng nhất & Sự cố mới
- **Phân tầng:** SHOULD-HAVE
- **Mô tả phạm vi:** Mở rộng hàm tính điểm ưu tiên khi có kết quả ABSA: áp dụng nguyên tắc khía cạnh tiêu cực nghiêm trọng nhất quyết định mức độ ưu tiên (worst-aspect-wins); tính điểm phạt cộng dồn nếu ticket có nhiều khía cạnh tiêu cực; nhận diện và gắn cờ sự cố mới (`novel_issue_flag = 1`) nếu xuất hiện từ khóa khía cạnh chưa từng có trong danh mục định sẵn.
- **Sản phẩm bàn giao:** Module mở rộng `src/priority/absa_priority_extension.py`.
- **Tiêu chí nghiệm thu:** Tự động nâng mức ưu tiên hợp lý khi khách hàng phàn nàn nhiều khía cạnh cùng lúc; cờ novel issue hoạt động chính xác theo từ khóa mới.
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M7 (Tuần 12).

---

### Nhóm 1.6: Module 4 — Hệ thống hàng đợi & Lưu trữ dữ liệu (Queue & Storage Subsystem)

#### WBS 1.6.1: Lược đồ cơ sở dữ liệu vé hỗ trợ & Đối tượng ánh xạ ORM
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Thiết kế lược đồ cơ sở dữ liệu quan hệ cho bảng `tickets` bằng thư viện SQLAlchemy ORM và hệ quản trị SQLite; định nghĩa đầy đủ các trường: `id`, `raw_text`, `detected_lang`, `translated_text`, `sentiment`, `sentiment_confidence`, `priority_score`, `priority_level`, `priority_explanation`, `status`, `assigned_to`, `needs_manual_review`, `created_at`, `updated_at`.
- **Sản phẩm bàn giao:** Module `src/database/models.py` và script khởi tạo database `src/database/init_db.py`.
- **Tiêu chí nghiệm thu:** Lược đồ CSDL chuẩn hóa, khóa chính, kiểu dữ liệu phù hợp, khởi tạo CSDL SQLite thành công không lỗi.
- **Chủ sở hữu:** Lê Công Quốc Mỹ (Tech Lead) | **Milestone:** M2 (Tuần 4).

#### WBS 1.6.2: Bộ thao tác dữ liệu vé hỗ trợ (CRUD)
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Xây dựng lớp truy cập dữ liệu (Data Access Layer - DAL): các hàm tạo mới vé hỗ trợ (`create_ticket`), đọc danh sách vé sắp xếp theo độ ưu tiên giảm dần (`get_tickets`), lấy chi tiết theo ID (`get_ticket_by_id`), cập nhật trạng thái xử lý và người phụ trách (`update_ticket_status`).
- **Sản phẩm bàn giao:** Module `src/database/repository.py`.
- **Tiêu chí nghiệm thu:** Các hàm thực thi đúng logic giao dịch (transactions), tự động đóng session và rollback an toàn khi phát sinh lỗi.
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M4 (Tuần 7).

#### WBS 1.6.3: Cấu trúc hàng đợi ưu tiên nội bộ (`heapq`)
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Xây dựng lớp cấu trúc dữ liệu hàng đợi ưu tiên trong bộ nhớ (In-memory Priority Queue) sử dụng module chuẩn `heapq` của Python; hỗ trợ đẩy phần tử (`push`), lấy phần tử ưu tiên cao nhất (`pop`); thiết lập cơ chế giải quyết xung đột khi đồng điểm: vé nào đến trước (timestamp cũ hơn) sẽ được ưu tiên phục vụ trước (FIFO tie-breaking); tự động đồng bộ nạp lại hàng đợi từ CSDL khi khởi động lại ứng dụng.
- **Sản phẩm bàn giao:** Module `src/queue/priority_queue.py`.
- **Tiêu chí nghiệm thu:** Trả về vé có priority_score cao nhất với độ phức tạp $O(1)$ khi xem và $O(\log n)$ khi thêm/bớt; xử lý chuẩn xác trường hợp đồng điểm.
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M6 (Tuần 11).

#### WBS 1.6.4: Bộ quản lý vòng đời 4 trạng thái vé hỗ trợ
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Cài đặt máy trạng thái (State Machine) quản trị luồng xử lý của vé hỗ trợ qua 4 trạng thái: Mới tiếp nhận (`new`) → Đã phân công (`assigned`) → Đang xử lý (`in_progress`) → Đã giải quyết (`resolved`); kiểm soát chặt chẽ các bước chuyển trạng thái hợp lệ, ngăn chặn thao tác sai quy trình.
- **Sản phẩm bàn giao:** Module `src/queue/state_manager.py`.
- **Tiêu chí nghiệm thu:** Chặn thành công các bước nhảy trạng thái phi lý (ví dụ: từ `new` nhảy trực tiếp lên `resolved` mà chưa phân công); tự động ghi nhận thời gian `updated_at`.
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M6 (Tuần 11).

#### WBS 1.6.5: Lược đồ mở rộng bảng khía cạnh quan hệ khóa ngoại
- **Phân tầng:** SHOULD-HAVE
- **Mô tả phạm vi:** Thiết kế bổ sung 2 bảng phụ trong CSDL: `ticket_aspects_acsa` (lưu trữ danh mục khía cạnh, cảm xúc, độ tin cậy) và `ticket_aspects_abte` (lưu trữ từ khóa khía cạnh trích xuất, vị trí ký tự, cờ novel issue); thiết lập khóa ngoại liên kết với bảng `tickets` có quan hệ 1-N và cơ chế xóa theo tầng (cascade delete); đảm bảo không làm thay đổi hay phá vỡ cấu trúc bảng `tickets` ban đầu.
- **Sản phẩm bàn giao:** Script migration và khai báo model bổ sung trong `src/database/models.py`.
- **Tiêu chí nghiệm thu:** Khóa ngoại liên kết toàn vẹn dữ liệu; truy vấn nạp kèm bảng con (joined load) hoạt động tối ưu.
- **Chủ sở hữu:** Lê Công Quốc Mỹ (Tech Lead) | **Milestone:** M7 (Tuần 12).

---

### Nhóm 1.7: Module 5 — Giao diện điều phối & Trực quan hóa dữ liệu (Dashboard Subsystem)

#### WBS 1.7.1: Giao diện hộp thư ưu tiên & Bảng danh sách vé hỗ trợ
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Xây dựng giao diện hòm thư thông minh (Triage Inbox) trên nền tảng Streamlit: danh sách vé hỗ trợ được sắp xếp tự động theo thứ tự ưu tiên giảm dần; hiển thị huy hiệu màu sắc trực quan theo cấp độ (Đỏ: CRITICAL, Cam: HIGH, Vàng: MEDIUM, Xanh: LOW); cung cấp các bộ lọc tìm kiếm theo trạng thái và mức độ ưu tiên.
- **Sản phẩm bàn giao:** Module giao diện `src/dashboard/views/inbox_view.py`.
- **Tiêu chí nghiệm thu:** Giao diện tải nhanh, hiển thị rõ ràng thông tin tóm tắt của vé; cập nhật vị trí danh sách ngay khi có vé mới có độ ưu tiên cao hơn.
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M7 (Tuần 12).

#### WBS 1.7.2: Bảng điều khiển phân tích thống kê cảm xúc & Ngôn ngữ
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Xây dựng trang tổng quan thống kê (Analytics Dashboard) sử dụng thư viện Plotly: trực quan hóa phân bố tỷ lệ cảm xúc (Tích cực / Tiêu cực / Trung tính), biểu đồ phân bố mức độ ưu tiên, biểu đồ tròn cơ cấu ngôn ngữ tiếp nhận (Tiếng Anh, Tiếng Việt, Khác), và thống kê số lượng vé theo từng trạng thái xử lý.
- **Sản phẩm bàn giao:** Module giao diện `src/dashboard/views/analytics_view.py`.
- **Tiêu chí nghiệm thu:** Các biểu đồ hiển thị tương tác mượt mà (hover hiển thị chi tiết số liệu); tự động cập nhật dữ liệu từ SQLite.
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M7 (Tuần 12).

#### WBS 1.7.3: Khung tiếp nhận & Kiểm thử phân loại vé thời gian thực
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Xây dựng khung giao diện tương tác trực tiếp (Live Simulator Panel): cho phép người dùng nhập bất kỳ đoạn văn bản phản hồi nào (cả tiếng Anh lẫn tiếng Việt); nhấn nút phân tích để kích hoạt toàn bộ pipeline 5 module chạy ngầm và hiển thị ngay lập tức kết quả: ngôn ngữ phát hiện, bản dịch (nếu là tiếng Việt), cảm xúc dự đoán, điểm ưu tiên, căn cứ giải thích và vị trí trong hàng đợi.
- **Sản phẩm bàn giao:** Thành phần giao diện `src/dashboard/components/simulator.py`.
- **Tiêu chí nghiệm thu:** Phản hồi kết quả trực quan trong vòng 1–2 giây; hiển thị minh bạch từng bước xử lý của pipeline.
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M7 (Tuần 12).

#### WBS 1.7.4: Giao diện thao tác cập nhật trạng thái & Phân công xử lý
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Xây dựng các thành phần tương tác trên giao diện cho phép nhân viên CSKH click xem chi tiết vé, nhập tên nhân sự xử lý, chọn cập nhật trạng thái tiến độ (`in_progress`, `resolved`); dữ liệu được lưu tức thì vào SQLite và làm mới trạng thái trên giao diện.
- **Sản phẩm bàn giao:** Thành phần giao diện `src/dashboard/components/ticket_actions.py`.
- **Tiêu chí nghiệm thu:** Thao tác cập nhật tức thì (instant update), có thông báo thành công (toast message); cập nhật đồng bộ trạng thái trong cơ sở dữ liệu.
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M7 (Tuần 12).

#### WBS 1.7.5: Thẻ giao diện phân tích khía cạnh chuyên sâu (ABSA Tab)
- **Phân tầng:** SHOULD-HAVE
- **Mô tả phạm vi:** Bổ sung tab chuyên biệt "Phân tích khía cạnh" trên Dashboard: hiển thị biểu đồ nhiệt (Heatmap) cảm xúc theo từng nhóm khía cạnh nghiệp vụ; biểu đồ cột phân bố các vấn đề khách hàng phàn nàn nhiều nhất; danh sách các vé có cảnh báo sự cố mới phát sinh (`novel issues`).
- **Sản phẩm bàn giao:** Module giao diện `src/dashboard/views/aspect_analytics_view.py`.
- **Tiêu chí nghiệm thu:** Hiển thị trực quan bức tranh toàn cảnh về sản phẩm/dịch vụ; chỉ kích hoạt khi cờ tính năng ABSA được bật.
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M8 (Tuần 13).

#### WBS 1.7.6: Bộ hiển thị nổi bật thực thể khía cạnh trong văn bản
- **Phân tầng:** SHOULD-HAVE
- **Mô tả phạm vi:** Xây dựng component giao diện hiển thị văn bản chi tiết có tính năng highlight màu trực tiếp vào các từ khóa khía cạnh trích xuất được từ mô hình ABTE (ví dụ: bôi đỏ chữ *"giao hàng chậm"*, bôi xanh *"nhân viên nhiệt tình"*); hover vào từ khóa để xem nhãn khía cạnh và mức độ tự tin.
- **Sản phẩm bàn giao:** Component `src/dashboard/components/text_highlighter.py`.
- **Tiêu chí nghiệm thu:** Highlight chính xác vị trí từ trong văn bản không bị lệch ký tự; giao diện trực quan, chuyên nghiệp.
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M8 (Tuần 13).

---

### Nhóm 1.8: Tích hợp toàn hệ thống, Kiểm thử & Đóng gói bàn giao (Integration & Deployment)

#### WBS 1.8.1: Giao diện lập trình ứng dụng điều phối tập trung (FastAPI Pipeline API)
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Xây dựng hàm nhạc trưởng điều phối toàn trình `process_ticket_pipeline(raw_text)` liên kết tuần tự cả 5 module; đóng gói thành dịch vụ backend sử dụng FastAPI cung cấp các RESTful API endpoints: `POST /tickets` (tiếp nhận vé mới, chạy pipeline và lưu trữ), `GET /tickets` (lấy danh sách theo thứ tự ưu tiên), `GET /tickets/{id}` (chi tiết vé), `PATCH /tickets/{id}/status` (cập nhật trạng thái).
- **Sản phẩm bàn giao:** Ứng dụng FastAPI hoàn chỉnh `src/api/main.py`.
- **Tiêu chí nghiệm thu:** 100% endpoints trả về mã HTTP status chuẩn, có tài liệu Swagger UI tự động tại `/docs`; tích hợp thông suốt toàn bộ 5 module.
- **Chủ sở hữu:** Lê Công Quốc Mỹ (Tech Lead) | **Milestone:** M7 (Tuần 12).

#### WBS 1.8.2: Bộ kiểm thử tích hợp luồng xử lý toàn trình Must-have
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Xây dựng kịch bản kiểm thử tích hợp tự động (End-to-End Test Suite): kiểm tra chu trình hoàn chỉnh từ lúc nhập một vé tiếng Anh/tiếng Việt thô, qua tiền xử lý, mô hình BERT, tính điểm ưu tiên, đẩy vào hàng đợi `heapq`, lưu vào CSDL SQLite và hiển thị chính xác trên Dashboard Streamlit.
- **Sản phẩm bàn giao:** Tệp kiểm thử tích hợp `tests/test_end_to_end_pipeline.py`.
- **Tiêu chí nghiệm thu:** Toàn bộ chu trình vận hành thông suốt không có lỗi ngoại lệ; dữ liệu đồng bộ nhất quán giữa API, CSDL và giao diện.
- **Chủ sở hữu:** Nguyễn Phương Thảo (QA) | **Milestone:** M8 (Tuần 13).

#### WBS 1.8.3: Bộ kịch bản kiểm thử tình huống biên & Ngoại lệ
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Xây dựng và thực thi bộ kiểm thử các trường hợp dữ liệu xấu và tình huống ngoại lệ thực tế: chuỗi văn bản rỗng, văn bản dài hơn 2000 từ, văn bản chứa toàn ký tự đặc biệt, văn bản tiếng nước ngoài (tiếng Pháp, tiếng Nhật), vé có cảm xúc mâu thuẫn giữa câu đầu và câu cuối; xác minh hệ thống luôn xử lý an toàn có log cảnh báo.
- **Sản phẩm bàn giao:** Báo cáo kiểm thử biên `reports/edge_cases_test_report.md`.
- **Tiêu chí nghiệm thu:** Hệ thống không bao giờ bị sập (crash) hoặc trả về lỗi 500 không kiểm soát; các trường hợp lỗi đều được gắn cờ xem xét thủ công hoặc ghi nhận rõ ràng.
- **Chủ sở hữu:** Nguyễn Phương Thảo (QA) | **Milestone:** M8 (Tuần 13).

#### WBS 1.8.4: Bộ dữ liệu demo giả lập tích hợp sẵn
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Xây dựng script tự động nạp (seed) bộ 50–100 ticket CSKH mẫu đa dạng tình huống vào CSDL SQLite khi khởi động ứng dụng lần đầu; bao gồm đầy đủ các mức độ khẩn cấp, các trạng thái xử lý, các thứ tiếng khác nhau để phục vụ buổi thuyết trình demo trực tiếp trước hội đồng mà không cần tạo vé thủ công từ đầu.
- **Sản phẩm bàn giao:** Script tạo dữ liệu mẫu `scripts/seed_demo_data.py`.
- **Tiêu chí nghiệm thu:** Chạy lệnh 1 dòng là có ngay cơ sở dữ liệu mẫu sinh động, trực quan sẵn sàng cho demo.
- **Chủ sở hữu:** Nguyễn Viết Pháp | **Milestone:** M8 (Tuần 13).

#### WBS 1.8.5: Bộ kiểm thử tích hợp tầng mở rộng khía cạnh
- **Phân tầng:** SHOULD-HAVE
- **Mô tả phạm vi:** Xây dựng kịch bản kiểm thử tích hợp khi kích hoạt cờ tính năng ABSA: kiểm tra luồng phân tích khía cạnh kép (ACSA + ABTE), tính toán điểm ưu tiên theo khía cạnh nghiêm trọng nhất và hiển thị biểu đồ nhiệt trên dashboard; kiểm tra các trường hợp biên đặc thù của ABSA (không phát hiện khía cạnh nào, mâu thuẫn cảm xúc giữa 2 khía cạnh).
- **Sản phẩm bàn giao:** Tệp kiểm thử `tests/test_absa_integration.py`.
- **Tiêu chí nghiệm thu:** Tầng mở rộng hoạt động ổn định; không làm chậm hoặc gây lỗi cho luồng Must-have đang vận hành.
- **Chủ sở hữu:** Nguyễn Phương Thảo (QA) | **Milestone:** M8 (Tuần 13).

#### WBS 1.8.6: Bản phát hành đóng gói hoàn chỉnh
- **Phân tầng:** MUST-HAVE
- **Mô tả phạm vi:** Đóng gói toàn bộ mã nguồn, tài liệu và môi trường thành bản phát hành hoàn chỉnh trên GitHub Release; viết hướng dẫn cài đặt và triển khai chi tiết từng bước trong file `README.md`; cung cấp script khởi chạy 1 lệnh (`run_app.bat` / `run_app.sh`).
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

| Mã WBS | Gói công việc bàn giao | Võ Tấn Đức (PM) | Lê Công Quốc Mỹ (Tech Lead) | Nguyễn Văn Lê Duy (Dev/DA) | Nguyễn Viết Pháp (Dev/DA) | Nguyễn Phương Thảo (QA) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **1.1** | **Quản trị dự án & Hồ sơ học phần** | **A / R** | C | I | I | C |
| 1.1.1 | Bộ hồ sơ khởi tạo dự án | **A / R** | C | I | I | C |
| 1.1.2 | Bản kế hoạch phạm vi & Từ điển WBS | **A / R** | C | I | I | C |
| 1.1.3 | Hệ thống theo dõi tiến độ Agile & Board | **A / R** | C | I | I | C |
| 1.1.4 | Sổ theo dõi rủi ro & Thay đổi phạm vi | **A / R** | C | I | I | C |
| 1.1.5 | Bộ hồ sơ minh chứng & Báo cáo đồ án | **A / R** | C | C | C | C |
| **1.2** | **Hạ tầng, Môi trường & Dữ liệu** | I | C | **A / R** | C | C |
| 1.2.1 | Kho lưu trữ mã nguồn & CI Actions | I | **A / R** | C | C | C |
| 1.2.2 | Môi trường GPU & Cấu hình thư viện | I | C | **A / R** | C | I |
| 1.2.3 | Bộ dữ liệu phân loại câu tiếng Anh | I | C | **A / R** | I | C |
| 1.2.4 | Tập kiểm thử ticket song ngữ mô phỏng | I | C | C | C | **A / R** |
| 1.2.5 | Dữ liệu kiểm chứng tiếng Việt | I | C | **A / R** | I | C |
| 1.2.6 | Dữ liệu khía cạnh SemEval Laptop | I | C | **A / R** | I | C |
| 1.2.7 | Bảng ánh xạ khía cạnh & Độ đồng thuận | I | C | C | I | **A / R** |
| **1.3** | **Module 1 — Tiền xử lý & Cổng ngôn ngữ** | I | **A / R** | C | I | C |
| 1.3.1 | Bộ chuẩn hóa văn bản | I | **A / R** | C | I | C |
| 1.3.2 | Bộ phát hiện ngôn ngữ & Phân luồng | I | **A / R** | C | I | C |
| 1.3.3 | Bộ dịch thuật máy VI -> EN | I | C | **A / R** | I | C |
| 1.3.4 | Giao diện hàm tiền xử lý & Test suite | I | **A / R** | C | I | C |
| 1.3.5 | Bộ tiền xử lý bảo toàn chỉ số ABTE | I | **A / R** | C | I | C |
| **1.4** | **Module 2 — Mô hình cảm xúc & Khía cạnh** | I | C | **A / R** | I | C |
| 1.4.1 | Mô hình cảm xúc cơ sở Baseline | I | C | **A / R** | I | C |
| 1.4.2 | Pipeline nạp dữ liệu mô hình BERT | I | C | **A / R** | I | C |
| 1.4.3 | Mô hình học sâu BERT fine-tuned (câu) | I | C | **A / R** | I | C |
| 1.4.4 | Báo cáo đánh giá hiệu năng mô hình | I | C | C | I | **A / R** |
| 1.4.5 | Giao diện API suy luận phân loại câu (2A) | I | C | **A / R** | C | C |
| 1.4.6 | Mô hình họ BERT phân loại khía cạnh ACSA | I | C | **A / R** | I | C |
| 1.4.7 | Mô hình họ BERT trích xuất thực thể ABTE | I | C | **A / R** | I | C |
| 1.4.8 | Giao diện API suy luận khía cạnh kép (2B) | I | C | **A / R** | C | C |
| **1.5** | **Module 3 — Bộ tính điểm ưu tiên nghiệp vụ** | I | C | I | **A / R** | C |
| 1.5.1 | Bộ từ điển từ khóa khẩn cấp & Trọng số | I | C | I | **A / R** | C |
| 1.5.2 | Bộ trích xuất cường độ cảm xúc câu | I | C | I | **A / R** | C |
| 1.5.3 | Hàm tính toán điểm ưu tiên giải thích được | I | C | I | **A / R** | C |
| 1.5.4 | Báo cáo kiểm thử đồng thuận nghiệp vụ | I | C | I | C | **A / R** |
| 1.5.5 | Bộ mở rộng ưu tiên theo khía cạnh | I | C | I | **A / R** | C |
| **1.6** | **Module 4 — Hàng đợi & Lưu trữ dữ liệu** | I | C | I | **A / R** | C |
| 1.6.1 | Lược đồ CSDL vé hỗ trợ & ORM | I | **A / R** | I | C | C |
| 1.6.2 | Bộ thao tác dữ liệu vé hỗ trợ (CRUD) | I | C | I | **A / R** | C |
| 1.6.3 | Cấu trúc hàng đợi ưu tiên `heapq` | I | C | I | **A / R** | C |
| 1.6.4 | Quản lý vòng đời 4 trạng thái vé | I | C | I | **A / R** | C |
| 1.6.5 | Lược đồ mở rộng bảng khía cạnh | I | **A / R** | I | C | C |
| **1.7** | **Module 5 — Giao diện Dashboard** | I | C | I | **A / R** | C |
| 1.7.1 | Giao diện hộp thư ưu tiên | I | C | I | **A / R** | C |
| 1.7.2 | Bảng điều khiển phân tích thống kê | I | C | I | **A / R** | C |
| 1.7.3 | Khung tiếp nhận & Kiểm thử realtime | I | C | I | **A / R** | C |
| 1.7.4 | Giao diện cập nhật trạng thái & Phân công | I | C | I | **A / R** | C |
| 1.7.5 | Thẻ giao diện phân tích khía cạnh (ABSA) | I | C | I | **A / R** | C |
| 1.7.6 | Bộ hiển thị nổi bật thực thể khía cạnh | I | C | I | **A / R** | C |
| **1.8** | **Tích hợp, Kiểm thử & Đóng gói** | **A** | C | C | C | C |
| 1.8.1 | API điều phối tập trung (FastAPI) | I | **A / R** | C | C | C |
| 1.8.2 | Kiểm thử tích hợp luồng Must-have | I | C | C | C | **A / R** |
| 1.8.3 | Kịch bản kiểm thử tình huống biên | I | C | C | C | **A / R** |
| 1.8.4 | Bộ dữ liệu demo giả lập tích hợp sẵn | I | C | I | **A / R** | C |
| 1.8.5 | Kiểm thử tích hợp tầng mở rộng ABSA | I | C | C | C | **A / R** |
| 1.8.6 | Bản phát hành đóng gói hoàn chỉnh | C | **A / R** | C | C | C |

---

## 6. KẾ HOẠCH BÀN GIAO THEO MILESTONES & KIỂM SOÁT THAY ĐỔI

### 6.1. Tiến độ tích hợp các gói WBS theo Milestones

```text
[Tuần 1-2] M1: Khởi tạo & Lập kế hoạch ──► WBS 1.1.1, 1.1.2, 1.1.3, 1.2.1
   │
[Tuần 3-4] M2: Thiết kế Kiến trúc & CSDL ──► WBS 1.2.2, 1.2.3, 1.6.1
   │
[Tuần 5-6] M3: Tiền xử lý & Baseline ML ──► WBS 1.2.4, 1.2.5, 1.3.1, 1.3.2, 1.3.3, 1.3.4, 1.4.1
   │
[Tuần 7]   M4: Sơ kết Sprint 1 & Rủi ro ──► WBS 1.1.4, 1.5.1, 1.5.2, 1.6.2
   │
[Tuần 8-9] M5: Huấn luyện BERT Sentence ──► WBS 1.4.2, 1.4.3, 1.4.4, 1.4.5 ──► [ĐÓNG BĂNG MUST-HAVE MODEL]
   │
[Tuần 10-11] M6: Priority Engine & Queue ──► WBS 1.5.3, 1.5.4, 1.6.3, 1.6.4 │ [Mở rộng]: WBS 1.2.6, 1.2.7, 1.4.6
   │
[Tuần 12]  M7: Dashboard & Tích hợp Must ──► WBS 1.7.1, 1.7.2, 1.7.3, 1.7.4, 1.8.1 │ [Mở rộng]: WBS 1.3.5, 1.4.7, 1.4.8, 1.5.5, 1.6.5
   │
[Tuần 13]  M8: Đóng băng toàn hệ thống ──► WBS 1.8.2, 1.8.3, 1.8.4, 1.8.6 │ [Mở rộng]: WBS 1.7.5, 1.7.6, 1.8.5
   │
[Tuần 14]  M9: Hồ sơ minh chứng hoàn tất ──► WBS 1.1.5 (Evidence Package, Báo cáo kỹ thuật)
   │
[Tuần 15]  M10: Bảo vệ đồ án tốt nghiệp ──► Thuyết trình & Demo trực tiếp trước Hội đồng
```

### 6.2. Quy tắc kiểm soát thay đổi phạm vi (Scope Baseline Control)
1. **Nguyên tắc "Đóng băng Must-have":** Tại cột mốc M5 (Tuần 9), toàn bộ mô hình và pipeline phân loại câu cấp độ Must-have phải được đóng băng kỹ thuật (code freeze). Mọi phát sinh hay tối ưu hóa sâu hơn đều phải chuyển sang nhánh `feature/absa` của tầng Should-have.
2. **Quy tắc an toàn tốt nghiệp:** Nếu tại mốc M6 hoặc M7 phát sinh chậm tiến độ hoặc rủi ro hạ tầng vượt mức kiểm soát, Project Lead có quyền quyết định dừng ngay lập tức việc phát triển các gói Should-have (WBS 1.4.6, 1.4.7, 1.7.5...) để tập trung 100% nguồn lực bảo đảm hệ thống Must-have đạt độ hoàn thiện cao nhất để bảo vệ đồ án.
3. **Quy trình thay đổi (Change Request Process):** Bất kỳ đề xuất thêm tính năng nào nằm ngoài danh mục WBS này đều phải tạo Issue với nhãn `change-request`, đánh giá tác động tới timeline 15 tuần và chỉ được triển khai khi có sự đồng thuận của Tech Lead và Project Lead.
