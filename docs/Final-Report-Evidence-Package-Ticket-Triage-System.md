# BÁO CÁO TỔNG KẾT ĐỒ ÁN & GÓI BẰNG CHỨNG KIỂM TOÁN (FINAL REPORT & WEEK 14 EVIDENCE PACKAGE)
## Dự án: Hệ thống phân loại & định tuyến phản hồi khách hàng theo cảm xúc (*Sentiment-Driven Ticket Triage System*)

**Mã dự án:** `TICKET-TRIAGE-01` | **Học phần:** Quản trị dự án phần mềm  
**Giảng viên hướng dẫn:** *Nguyễn Thanh Tuấn*  
**Nhóm thực hiện:** *DogTowFaces* (Võ Tấn Đức, Lê Công Quốc Mỹ, Nguyễn Văn Lê Duy, Nguyễn Viết Pháp, Nguyễn Phương Thảo)  
**Hạn nộp & rà soát (Due):** Cuối **tuần 14 (Week 14 — Report Finalization & Evidence Audit)** — *Ngày: 15/11/2026*  
**Mục tiêu kiểm toán (Goal):** Tập hợp và đối soát toàn bộ chuỗi bằng chứng thực thi xuyên suốt học kỳ (Weeks 1–14) trước buổi bảo vệ đồ án tuần 15 (*Week 15 Capstone Defense*). Toàn bộ báo cáo dưới đây ghi nhận **lịch sử đã thực thi trên thực tế (Historical Execution Record)**, không phải bản kế hoạch tương lai.

---

## I. DANH SÁCH KIỂM TRA GÓI BẰNG CHỨNG TUẦN 14 (THE WEEK 14 EVIDENCE CHECKLIST)

Bảng kiểm tra dưới đây đối chiếu trực tiếp từng hạng mục yêu cầu của học phần với các hiện vật (artifacts), lịch sử commit và hồ sơ quản lý thực tế của nhóm **DogTowFaces**:

- [x] **1. Báo cáo tổng kết học kỳ (`Final report` — synthesizes the semester, doesn't repeat every weekly slide):**
  - Đã tổng hợp toàn trình từ khởi tạo (Tuần 1–2), lập kế hoạch WBS (Tuần 3–4), thực thi các Sprint phát triển song song 2 bài toán (Tuần 5–12), quản trị rủi ro & thay đổi phạm vi (Tuần 6 & 11) đến đóng dự án & bài học kinh nghiệm (Tuần 13–14) ngay tại **Phần II** của tài liệu này.
- [x] **2. Liên kết kho mã nguồn & lịch sử Commit thực tế (`Repo link` — real commit history, not a single end-of-semester commit):**
  - **Repository chính thức:** `https://github.com/CRP-2026/Sentiment-Driven-Ticket-Triage-System`
  - **Chuỗi lịch sử commit trải dài theo từng giai đoạn phát triển thực tế:**
    - *Giai đoạn khởi tạo & Baseline (Weeks 1–4):* `e971fd4` (*Initial commit: project structure and setup*) $\rightarrow$ `e415dc9` & `5d59373` (PR `#11`: *docs: update project charter and add wbs v2.0 / v3.0*).
    - *Giai đoạn Sprint 1 — Khung kiến trúc 2 bài toán, CI & tiền xử lý (Weeks 5–7):* `7e682ac` (*feat: initialize sentiment-driven ticket triage system with backend and frontend services*) $\rightarrow$ `5bc492c` & `653214b` (PR `#15`: *feat(ci): add automated AI code review workflow with Gemini 3.8 Flash*) $\rightarrow$ `d40a2fd` (PR `#23`: *fix(pre-data): resolve data processing issue*) $\rightarrow$ `378cbc5` (*fix: setup database session management with testing and dev environment*).
    - *Giai đoạn Sprint 2 — Xử lý hồi quy, cấu hình động YAML & nâng cấp React SPA (Weeks 8–12):* `f065d7f`, `a626b2a`, `f1dd583`, `8ae045e` (PR `#27`: *fix/CI-critical-high & fix test regression*) $\rightarrow$ `e42f4bb`, `e465360`, `7c94f86`, `fecb309` (PR `#28`: *fix(core): load yaml configs dynamically, unify specifications and remove redundant not_mentioned*) $\rightarrow$ `3744172`, `68643d2`, `e437b3a` (PR `#30`: *feat(inbox): update ticket table and actions*) $\rightarrow$ `9989760` (*docs: add second issue documentation*) $\rightarrow$ `5f995c4` (*feat(web): update live testing*).
- [x] **3. Hồ sơ bảng theo dõi tiến độ qua các Sprint (`Board export` — Sprint 1 & 2 history, not just a final-state screenshot):**
  - **GitHub Project Board URL:** `http://github.com/orgs/CRP-2026/projects/1/views/1` (Kanban 4 cột: `To do` $\rightarrow$ `In Progress` $\rightarrow$ `In Review` $\rightarrow$ `Done`).
  - Lịch sử dịch chuyển thẻ công việc (Work Packages), vận tốc thực thi (Velocity/Burndown) và đối soát giữa kế hoạch đầu Sprint với kết quả bàn giao cuối Sprint của **Sprint 1 (Weeks 5–7)** và **Sprint 2 (Weeks 8–12)** được trích xuất đầy đủ tại **Mục II.4** dưới đây.
- [x] **4. Sổ đăng ký rủi ro động có lịch sử tiến hóa (`Risk register` — both updates Week 6 & Week 11, showing it evolved):**
  - **Tài liệu đính kèm:** [Risk-Register-Ticket-Triage-System.md](./Risk-Register-Ticket-Triage-System.md).
  - Chứng minh rõ sự tiến hóa của 10 mã rủi ro (`RR-01` $\rightarrow$ `RR-10`) giữa **Cập nhật #1 (Tuần 6)** — khi các lỗi ca biên thực tế phát sinh (`RR-01` $\rightarrow$ `RR-06`) — và **Cập nhật #2 (Tuần 11)** — khi toàn bộ `RR-01` $\rightarrow$ `RR-08` (bao gồm các rủi ro ở tầng NLP, Backend, Database và giao diện Frontend/CI) được đóng lại thành công, đồng thời kiểm soát và xử lý 2 rủi ro đồng bộ ở đợt rà soát 2 (`RR-09, RR-10` tại [Issue-second.md](./Issue-second.md)).
- [x] **5. Hồ sơ kiểm soát thay đổi phạm vi thực tế (`Change record` — the real scope change processed in Week 11):**
  - Ghi nhận đầy đủ 3 yêu cầu thay đổi phạm vi/kiến trúc thực tế (`CR-01`: Cắt dịch máy chuyển sang English-only; `CR-02`: Bỏ nhãn thứ 4 `not_mentioned` trong NLI ở PR `#28` và đổi thang điểm `[0.0, 1.0]` sang `[0, 100]` 3 mức; `CR-03`: Chuyển đổi giao diện từ Streamlit/Plotly sang React 18 + TypeScript + Vite + TailwindCSS + Recharts SPA ở PR `#30` & Commit `5f995c4`). Chi tiết phân tích tác động nằm tại **Mục II.5.2**.
- [x] **6. Xác nhận nghiệm thu đóng dự án tuần 13 (`Acceptance confirmation` — from Week 13's closure):**
  - Biên bản kiểm tra nghiệm thu theo tiêu chuẩn *Definition of Done (DoD)* đối với 38 gói công việc WBS, kết quả chạy script xác thực hệ thống `verify_system.py` và xác nhận bàn giao tại mốc **M8/M9 (Tuần 13)** được trình bày tại **Mục II.6**.

---

## II. BÁO CÁO TỔNG KẾT ĐỒ ÁN HỌC KỲ (SEMESTER SYNTHESIS REPORT)

### 1. Tổng quan dự án (Project Overview — Khởi tạo từ Project Charter tuần 2)

* **Bối cảnh & bài toán thực tế:**
  Dự án **Sentiment-Driven Ticket Triage System (`TICKET-TRIAGE-01`)** được nhóm **DogTowFaces** khởi tạo vào ngày 21/09/2026 nhằm giải quyết điểm nghẽn vận hành cốt lõi tại các trung tâm chăm sóc khách hàng (Customer Support - CSKH) thương mại điện tử: cơ chế xếp hàng truyền thống **FIFO (First In, First Out)** xử lý các yêu cầu theo thứ tự thời gian tiếp nhận, khiến những khách hàng đang gặp sự cố nghiêm trọng (bị trừ tiền hai lần, lừa đảo thanh toán, dọa khởi kiện, thất lạc đơn hàng lâu ngày) phải chờ đợi sau hàng trăm câu hỏi tra cứu thông thường.
* **Giải pháp kiến trúc đã xây dựng:**
  Nhóm đã thiết kế và hiện thực hóa một hệ thống tự động phân tích cảm xúc đa khía cạnh và điều phối hàng đợi ưu tiên cho ticket tiếng Anh, được phân tách rạch ròi thành **2 bài toán kỹ thuật độc lập (Two-Subsystem Architecture)**:
  1. **Bài toán 1 — Phân tích khía cạnh cảm xúc (ABSA Subsystem):** Kết hợp bộ lọc từ khóa trước (`keyword_prefilter.py`) và mô hình suy luận ngôn ngữ tự nhiên **Zero-shot NLI** (`valhalla/distilbart-mnli-12-3` / `deberta-v3`) để trích xuất 5 khía cạnh nghiệp vụ chuẩn (`customer_service`, `refund_payment`, `product_quality`, `shipping`, `general`) cùng sắc thái cảm xúc 3 lớp (`negative`, `neutral`, `positive`) và độ tin cậy.
  2. **Bài toán 2 — Động cơ tính điểm ưu tiên & hàng đợi định tuyến (Priority Triage & Queue Subsystem):** Áp dụng công thức tính điểm **Rule-based toán học minh bạch** theo nguyên lý *khía cạnh tiêu cực nghiêm trọng nhất quyết định điểm nền (Worst-Aspect-Wins)* kết hợp trọng số từ khóa khẩn cấp và cường độ cú pháp câu trên thang `[0.0, 100.0]`, đẩy vào hàng đợi ưu tiên in-memory `heapq` (giải quyết đồng điểm theo FIFO), lưu trữ bền vững trong SQLite (WAL mode) và điều phối trực quan trên giao diện React SPA.
* **Các bên liên quan (Stakeholders) & phân công thực thi:**
  - **Academic Supervisor / Approver:** Giảng viên *Nguyễn Thanh Tuấn*.
  - **Đội ngũ thực hiện (5 thành viên):**
    - *Võ Tấn Đức (`23IT.EB024` - `@Ducinviciable`):* **Project Lead / PM** — Quản trị tiến độ Kanban, Risk Register & Change Control, thiết lập workflow AI Code Review và rà soát hệ thống.
    - *Lê Công Quốc Mỹ (`23IT.EB060` - `@lupinname`):* **Technical Lead** — Kiến trúc Clean Architecture, Docker Compose, GitHub Actions CI, Preprocessing, SQLite ORM & FastAPI Pipeline.
    - *Nguyễn Văn Lê Duy (`23IT.EB026` - `@conangamo`):* **Lead Dev Bài toán 1 (ABSA)** — Taxonomy YAML, Keyword Pre-filter, Zero-shot NLI Pipeline & Mock Model.
    - *Nguyễn Viết Pháp (`23IT.EB070` - `@vietphap035`):* **Lead Dev Bài toán 2 (Priority & Queue)** — Priority Engine, Intensity Extractor, `heapq`, Repository DAL & cấu hình YAML.
    - *Nguyễn Phương Thảo (`23IT.EB098` - `@phuongthaonee`):* **QA/QC & Frontend UI Engineer** — Chuẩn hóa tài liệu Charter/WBS, kiểm thử hồi quy & E2E, và hoàn thiện giao diện người dùng React SPA (`InboxPage`, `TicketTable`, `TesterPage`).

---

### 2. Phương pháp luận phát triển & lý do lựa chọn (Methodology Chosen & Why — Tuần 1–2)

* **Phương pháp luận đã áp dụng:** Nhóm đã lựa chọn mô hình **Agile kết hợp phát triển lặp & tăng trưởng theo hợp đồng giao diện (Contract-First Iterative & Incremental Development)**, chia thành các chu kỳ Sprint và đồng bộ qua 10 cột mốc kiểm soát (Milestones M1–M10).
* **Lý do lựa chọn xuất phát từ đặc thù kỹ thuật của dự án:**
  1. **Giải quyết rủi ro phụ thuộc phần cứng AI (Decoupling AI Training from Software Engineering):** Trong một dự án tích hợp AI/NLP của sinh viên, việc thu thập dữ liệu, gán nhãn và tinh chỉnh mô hình NLI trên Google Colab T4 thường mất nhiều tuần và tiềm ẩn rủi ro đứt gãy phiên GPU. Nếu áp dụng mô hình Waterfall tuần tự (đợi có model AI hoàn chỉnh mới viết Backend và UI), các thành viên phụ trách Backend và Frontend sẽ bị rơi vào trạng thái chờ đợi trong nửa đầu học kỳ.
  2. **Thiết kế theo hợp đồng đóng băng (`Frozen Contract`):** Ngay từ tuần 3–4, nhóm đã chốt cứng giao diện dữ liệu trung gian `AbsaResult` (`ticket-triage-be/src/ticket_triage/core/sentiment/base.py`) và hợp đồng OpenAPI (`contracts/openapi.json`). Nhờ đó, các luồng công việc (**ABSA & Data**, **Priority Engine & SQLite API**, và **React SPA Dashboard & QA**) đã chạy song song hoàn toàn nhờ `MockSentimentModel` và dữ liệu mock.
  3. **Kiểm soát chất lượng liên tục (Continuous Verification):** Thay vì dồn việc kiểm thử vào cuối kỳ, quy trình Agile kết hợp GitHub Actions CI (`ci.yml`) và AI Code Reviewer (`ai-review.yml`) buộc mọi Pull Request vào nhánh `dev` phải vượt qua `ruff`, `pytest`, `tsc`, `eslint` và `vitest`, giúp phát hiện sớm các lỗi kiến trúc/ca biên ngay ở cuối Sprint 1 (tuần 6).

---

### 3. Tóm tắt lập kế hoạch: WBS, ước lượng & lịch trình (Planning Summary — Tuần 3–4)

* **Cấu trúc phân rã công việc (WBS v3.0):**
  Trong tuần 3–4, nhóm đã hoàn thiện [WBS-Ticket-Triage-System.md](./WBS-Ticket-Triage-System.md) tuân thủ nguyên tắc *Deliverable-Oriented* và *Quy tắc 100%* của PMI, phân rã dự án thành **8 nhóm chính (Level 2)** và **38 gói công việc (Work Packages - Level 3)**:
  - `1.1 Quản trị dự án & hồ sơ học phần` (5 gói: `1.1.1` $\rightarrow$ `1.1.5`)
  - `1.2 Hạ tầng kỹ thuật, môi trường & dữ liệu` (7 gói: `1.2.1` $\rightarrow$ `1.2.7`)
  - `1.3 Module 1 — Tiền xử lý văn bản tiếng Anh & lọc trước khía cạnh` (4 gói: `1.3.1` $\rightarrow$ `1.3.4`)
  - `1.4 Module 2 — Bài toán 1: Hệ thống phân tích khía cạnh ABSA Zero-shot NLI` (5 gói: `1.4.1` $\rightarrow$ `1.4.5`)
  - `1.5 Module 3 — Bài toán 2: Bộ tính điểm ưu tiên nghiệp vụ Rule-Based` (4 gói: `1.5.1` $\rightarrow$ `1.5.4`)
  - `1.6 Module 4 — Bài toán 2: Hệ thống hàng đợi & lưu trữ dữ liệu` (4 gói: `1.6.1` $\rightarrow$ `1.6.4`)
  - `1.7 Module 5 — Giao diện điều phối & trực quan hóa dữ liệu` (4 gói: `1.7.1` $\rightarrow$ `1.7.4`)
  - `1.8 Tích hợp toàn hệ thống, kiểm thử & đóng gói bàn giao` (5 gói: `1.8.1` $\rightarrow$ `1.8.5`)
* **Ước lượng nỗ lực (Effort Estimation) & đường găng (Critical Path):**
  - Toàn bộ 38 gói công việc được ước lượng tổng cộng **152 Story Points (SP)** (~456 giờ công cho 5 thành viên trong 15 tuần), với kích thước mỗi gói công việc giới hạn trong khoảng **3–8 SP** (hoàn thành trong 1–2 tuần).
  - **Đường găng dự án (Critical Path):** `1.1.1/1.1.2 (Charter & WBS)` $\rightarrow$ `1.2.1/1.6.1 (Repo, CI & SQLite Schema)` $\rightarrow$ `1.3.1–1.3.4 (Preprocessing & Keyword Prefilter)` $\rightarrow$ `1.4.1/1.5.3 (NLI Baseline & Priority Engine)` $\rightarrow$ `1.8.1/1.7.1–1.7.4 (FastAPI Pipeline & React SPA UI)` $\rightarrow$ `1.8.2/1.8.3 (E2E & Regression Testing)` $\rightarrow$ `1.8.5/1.1.5 (Release & Defense)`.

---

### 4. Tóm tắt thực thi: Lịch sử các Sprint & sản phẩm đã bàn giao (Execution Summary — Tuần 5–12)

Quá trình thực thi trải qua các đợt tích hợp, phát hiện lỗi ca biên và nâng cấp kiến trúc rõ rệt qua 2 giai đoạn Sprint lớn:

#### 4.1. Giai đoạn Sprint 1 (Tuần 5 – Tuần 7 | Milestones M3 & M4)
* **Mục tiêu Sprint 1:** Xây dựng xong toàn bộ tầng tiền xử lý tiếng Anh (Module 1), khung cơ sở dữ liệu SQLite + DAL CRUD (Module 4), công thức Priority Engine v1 chạy trên `MockSentimentModel` (Module 3), khung `ZeroShotNliModel` baseline (Module 2), khung Frontend cơ bản và thiết lập hệ thống CI/CD tự động.
* **Những gì đã thực sự bàn giao (What Shipped in Sprint 1):**
  - Khởi tạo kiến trúc monorepo gồm `ticket-triage-be/` (FastAPI + SQLAlchemy 2.0 + SQLite WAL mode) và `ticket-triage-fe/` kèm `docker.yaml` và `Makefile` (Commit `7e682ac`).
  - Thiết lập luồng kiểm thử tự động `.github/workflows/ci.yml` và tích hợp **AI Code Reviewer** sử dụng Gemini API để tự động kiểm tra quy chuẩn kiến trúc trên mỗi Pull Request (Commits `5bc492c`, `653214b` - PR `#15`).
  - Hoàn thiện chuỗi tiền xử lý `normalizer.py` $\rightarrow$ `lang_validator.py` $\rightarrow$ `keyword_prefilter.py` $\rightarrow$ `pipeline.py` (PR `#23` - Commit `d40a2fd`) và tách biệt quản lý session SQLite giữa môi trường test và dev (Commit `378cbc5`).
* **Sự cố thực tế cuối Sprint 1:**
  - Dù `22/22` unit tests cơ bản đều PASS, khi nhóm chạy kiểm thử ca biên (ngày 31/10/2026), đã phát hiện **8 lỗi kỹ thuật nghiêm trọng**: (1) `langdetect` nhận nhầm 40% câu tiếng Anh ngắn thành ngoại ngữ; (2) hàm `_is_negated()` triệt tiêu nhầm điểm khẩn cấp của câu *"I did not receive my refund"*; (3) `MockSentimentModel` bắt nhầm chuỗi con `"issue"` thành `"sue"`; (4) `clean_text()` làm hỏng từ có 2 chữ cái lặp (*"coool"* $\rightarrow$ *"col"*); (5) lỗ hổng nhận ticket rỗng/payload 350.000 ký tự; (6) thiếu hậu tố `"Z"` gây lệch 7 giờ GMT+7; (7) `heapq` không xóa ticket khi chuyển sang `resolved`; (8) lệnh `make gen-api` ghi đè làm vỡ type của Frontend.

#### 4.2. Giai đoạn Sprint 2 & tích hợp toàn trình (Tuần 8 – Tuần 12 | Milestones M5, M6 & M7)
* **Mục tiêu Sprint 2:** Khắc phục triệt để 8 lỗi từ Sprint 1, nạp động cấu hình YAML (`aspects.yaml`, `aspect_hypotheses.yaml`, `priority_rules.yaml`), hoàn thiện 8 RESTful API endpoints của FastAPI, nâng cấp giao diện React SPA (Inbox, Live Tester, Analytics) và đóng băng toàn bộ pipeline 2 bài toán.
* **Những gì đã thực sự bàn giao (What Shipped in Sprint 2):**
  - **Sửa dứt điểm 8 lỗi Sprint 1 & khóa bằng Regression Suite (PR `#27` - Commits `f065d7f`, `a626b2a`, `f1dd583`, `8ae045e`):** Sửa heuristic câu ngắn ASCII trong `lang_validator.py`, thu hẹp bán kính phủ định $\le 5$ ký tự trong `priority_engine.py`, dùng regex `\b` + MD5 seed trong `mock.py`, nén chữ lặp về `\1\1` trong `normalizer.py`, thêm validator `[3, 5000]` ký tự & serializer ISO-8601 `"Z"` trong `schemas.py`, bổ sung `queue.remove(ticket_id)` khi `resolved`. Bổ sung file `tests/test_regression_issues.py`, nâng toàn bộ bộ test Backend lên mức PASS 100%.
  - **Đồng bộ cấu hình YAML động & tinh gọn NLI 3 lớp (PR `#28` & nhánh `fix/priority-rule-in-be` - Commits `e42f4bb`, `e465360`, `7c94f86`, `fecb309`):** Kết nối hàm `load_aspect_hypotheses()` và `load_priority_rules()` có `@lru_cache`, loại bỏ hoàn toàn nhãn thứ 4 `not_mentioned` dư thừa để tăng tốc suy luận NLI gấp $2\times - 3\times$.
  - **Hoàn thiện giao diện điều phối React 18 SPA (PR `#30` & nhánh `feature/update-live-testing` - Commits `3744172`, `68643d2`, `e437b3a`, `5f995c4`):**
    - `InboxPage.tsx` & `TicketTable.tsx`: Bảng hàng đợi ưu tiên với 4 thẻ KPI tổng quan, thanh phân bố khía cạnh trực quan, bộ lọc 3 chiều (Trạng thái, Khía cạnh, Cảm xúc), cập nhật trạng thái trực tiếp (`StatusSelect.tsx`) và hộp thoại giải trình công thức điểm (`PriorityBreakdown.tsx`).
    - `TesterPage.tsx`: Khung mô phỏng thời gian thực với 5 kịch bản mẫu (bao gồm cả kịch bản tiếng Việt để demo chặn ngoại ngữ), hiệu ứng chuyển trạng thái skeleton mượt mà (`MIN_SKELETON_MS`), hiệu ứng đếm số `useCountUp` và đồng hồ đo thời gian thực thi (`executionTime`).
    - `AnalyticsPage.tsx`: Biểu đồ tròn (`PieChart`) và biểu đồ cột (`BarChart`) bằng Recharts tự động làm mới mỗi 10 giây.

#### 4.3. Bảng lịch sử dịch chuyển bảng công việc & vận tốc thực thi (Board History & Burndown Export)

| Giai đoạn / Sprint | Tổng SP kế hoạch (Planned) | SP hoàn thành (Completed) | Thẻ công việc (WBS Work Packages) đã dịch chuyển `To do` $\rightarrow$ `In Progress` $\rightarrow$ `In Review` $\rightarrow$ `Done` | Minh chứng PR / Commit trên GitHub |
| :--- | :---: | :---: | :--- | :--- |
| **Giai đoạn 0: Initiation & Planning (Weeks 1–4)** | 28 SP | **28 SP** *(100%)* | `1.1.1` (Charter v3.0), `1.1.2` (WBS v3.0), `1.1.3` (Kanban Board), `1.2.1` (Repo & CI), `1.6.1` (SQLite ORM Schema) | `e971fd4`, `e415dc9`, `5d59373`, PR `#11` (`effb2b2`) |
| **Sprint 1: Core Foundation & Mock Pipeline (Weeks 5–7)** | 52 SP | **44 SP** *(84.6%)*<br>*(8 SP chuyển sang đầu Sprint 2 để sửa 8 lỗi ca biên)* | **Hoàn tất (`Done`):** `1.2.2`, `1.2.5`, `1.3.1` (`normalizer`), `1.3.2` (`lang_validator`), `1.3.3` (`keyword_prefilter`), `1.3.4` (`preprocessing_pipeline`), `1.4.1` (`baseline.py`), `1.5.2` (`intensity`), `1.6.2` (`repository.py`), `1.6.4` (`state_manager`).<br>**Giữ lại ở `In Review` cuối W6:** `1.5.3` (`priority_engine`), `1.6.3` (`heapq`) do phát hiện lỗi `#2` và `#7`. | `7e682ac`, PR `#15` (`64e8fe1`), PR `#23` (`55e618a`), `378cbc5` |
| **Sprint 2: Regression Fix, YAML Unification & React SPA (Weeks 8–12)** | 56 SP *(+8 SP carryover = 64 SP)* | **58 SP** *(90.6%)* | **Hoàn tất (`Done`):** Đóng 8 lỗi hồi quy (`1.5.3`, `1.6.3`), `1.4.2` (`taxonomy.py` + `aspects.yaml`), `1.4.5` (`predict`), `1.5.1` (`priority_rules.yaml`), `1.7.1` (`InboxPage`), `1.7.2` (`AnalyticsPage`), `1.7.3` (`TesterPage`), `1.7.4` (`StatusSelect` & `TicketTable`), `1.8.1` (`FastAPI routers & pipeline`), `1.8.2` (`test_end_to_end_pipeline.py`), `1.8.3` (`test_regression_issues.py`), `1.8.4` (`seed_demo_data.py`). | PR `#27` (`8ae045e`), PR `#28` (`fecb309`), PR `#30` (`e437b3a`), `9989760`, `5f995c4` |
| **Giai đoạn Closure & Verification (Weeks 13–14)** | 16 SP *(+6 SP nợ kỹ thuật đợt 2)* | **22 SP** *(100%)* | **Hoàn tất (`Done`):** `1.1.4` (Dynamic Risk Register & Change Log), `1.8.5` (Docker Compose Demo & `verify_system.py`), `1.1.5` (Final Report & Week 14 Evidence Package). | `verify_system.py`, `docker-compose.demo.yml`, Hồ sơ Báo cáo 3, 4, 5 |
| **TỔNG CỘNG TOÀN DỰ ÁN** | **152 SP** | **152 SP (100%)** | **38 / 38 gói công việc WBS hoàn tất nghiệm thu** | **Toàn bộ lịch sử nhánh `main` & `dev`** |

---

### 5. Quản trị rủi ro & thay đổi phạm vi: Những gì đã thực sự diễn ra (Risk & Change Management — Tuần 6 & Tuần 11)

*(Chi tiết đầy đủ được lưu trữ tại tệp [Risk-Register-Ticket-Triage-System.md](./Risk-Register-Ticket-Triage-System.md))*

#### 5.1. Sự tiến hóa thực tế của sổ đăng ký rủi ro (Week 6 $\rightarrow$ Week 11)
* **Tại tuần 6 (Sprint 1 Review):** Thay vì giữ các rủi ro chung chung ở tuần 2, nhóm đã ghi nhận trực tiếp **6 rủi ro kỹ thuật & phạm vi có thật (`RR-01` $\rightarrow$ `RR-06`)**:
  - `RR-01` (Trôi phạm vi đa ngôn ngữ Việt - Anh $\rightarrow$ đã chốt cắt bỏ ở PR `#11`).
  - `RR-02` (Độ trễ NLI 20 lượt forward-pass/ticket) & `RR-03` (Thiếu GPU trên máy local + lỗi substring `"issue"` $\rightarrow$ `"sue"` trong `mock.py`).
  - `RR-04` (`langdetect` nhận nhầm 40% câu tiếng Anh ngắn thành tiếng Đan Mạch/Đức/Hà Lan + regex `clean_text` biến `"coool"` thành `"col"`).
  - `RR-05` (Hàm `_is_negated` bán kính 25 ký tự làm mất điểm khẩn cấp của câu *"I did not receive my refund"*).
  - `RR-06` (Hàng đợi `heapq` không xóa vé đã `resolved`, lệch 7 giờ GMT+7 do thiếu hậu tố `"Z"`, và lỗ hổng nhận chuỗi rỗng/350.000 ký tự).
* **Tại tuần 11 (Sprint 2 Review):**
  - **Đóng thành công toàn bộ rủi ro tuần 6 (`RR-01` $\rightarrow$ `RR-06` $\rightarrow$ `Resolved / Closed`):** Minh chứng trực tiếp qua PR `#11, #23, #27, #28` và bộ bài kiểm thử tự động trong `ticket-triage-be/tests/test_regression_issues.py`.
  - **Xử lý dứt điểm 2 rủi ro về giao diện Frontend & Lockfile CI (`RR-07, RR-08` $\rightarrow$ `Resolved / Closed`):**
    1. `RR-07`: Cải thiện khả năng nhận diện mức độ ưu tiên trên bảng `InboxPage` / `TicketTable` và tính trực quan của hộp thoại giải trình `PriorityBreakdown` (PR `#30`).
    2. `RR-08`: Xử lý hiện tượng nháy trạng thái loading trên `TesterPage.tsx` khi phản hồi nhanh và dọn dẹp xung đột `package-lock.json` với `pnpm` trên CI (Commits `68643d2` và `5f995c4`).
  - **Phát hiện và kiểm soát 2 rủi ro đồng bộ ở đợt rà soát kỹ thuật thứ hai (`RR-09, RR-10` — đối chiếu [Issue-second.md](./Issue-second.md) Commit `9989760`):**
    1. `RR-09`: Nối danh sách từ khóa trong `priority_engine.py` vào `configs/priority_rules.yaml`.
    2. `RR-10`: Tách `src/api/generated.ts` bảo vệ `schema.d.ts` và kiểm soát nhánh `MODEL_NAME=deberta` qua cờ `is_mock` tại `/api/v1/health`.

#### 5.2. Hồ sơ kiểm soát thay đổi phạm vi (Scope Change Record — Tuần 11)
Trong suốt dự án, nhóm đã xử lý chính thức **3 yêu cầu thay đổi phạm vi/kiến trúc (Change Requests)**:
1. **`CR-01` — Thu hẹp ranh giới ngôn ngữ về English-only & tách 2 bài toán độc lập (Commits `e415dc9`, `5d59373` - PR `#11`):** Loại bỏ module dịch máy tiếng Việt (`opus-mt-vi-en`) để tránh suy giảm chất lượng phân tích cảm xúc và độ trễ; thay bằng cổng kiểm soát `lang_validator.py` tự động gắn cờ `needs_manual_review = True` và gán điểm sàn an toàn `50.0` (`MEDIUM`) cho mọi ticket ngoại ngữ.
2. **`CR-02` — Loại bỏ nhãn thứ 4 `not_mentioned` trong NLI & chuẩn hóa thang điểm `[0, 100]` 3 cấp độ (PR `#28` - Commit `7c94f86`):** Vì `keyword_prefilter.py` đã lọc khía cạnh ứng viên ở bước 1, việc bắt mô hình NLI dự đoán thêm nhãn `not_mentioned` là dư thừa. Nhóm đã thống nhất mô hình NLI chỉ phân loại 3 lớp cảm xúc (`negative`, `neutral`, `positive`) và chuẩn hóa điểm đầu ra của Priority Engine từ đoạn `[0.0, 1.0]` (4 mức) sang thang `[0.0, 100.0]` với 3 mức trực quan: `CRITICAL` ($\ge 70$), `MEDIUM` ($30 - 69.9$), `LOW` ($< 30$).
3. **`CR-03` — Thay thế giao diện Streamlit/Plotly bằng kiến trúc React 18 + TypeScript + Vite + TailwindCSS + Recharts SPA (PR `#30` & Commit `5f995c4`):** Nhằm khắc phục hiện tượng tải lại toàn trang (full-page rerun) của Streamlit khi polling hàng đợi 3 giây/lần và nâng cao chất lượng hiển thị giải trình điểm, nhóm đã xây dựng ứng dụng SPA hoàn chỉnh tại `ticket-triage-fe/`.

---

### 6. Đóng dự án, nghiệm thu & bài học kinh nghiệm (Closure, Acceptance & Lessons Learned — Tuần 13)

#### 6.1. Biên bản xác nhận nghiệm thu đóng dự án (Week 13 Acceptance Confirmation)
Vào cuối tuần 13 (Milestone M8/M9 — Code Freeze), nhóm đã thực hiện kiểm toán nghiệm thu toàn hệ thống thông qua kịch bản kiểm tra tự động `ticket-triage-be/scripts/verify_system.py` và bộ test CI:

| Tiêu chí nghiệm thu (Acceptance Criterion từ Charter v3.0) | Chỉ tiêu cam kết | Kết quả thực tế đạt được (Week 13 Closure) | Minh chứng kiểm toán (Verification Evidence) | Trạng thái |
| :--- | :--- | :--- | :--- | :---: |
| **1. Tích hợp End-to-End 2 bài toán & giao diện Dashboard** | Chạy thông suốt từ `raw_text` $\rightarrow$ Preprocessing $\rightarrow$ ABSA $\rightarrow$ Priority $\rightarrow$ SQLite & `heapq` $\rightarrow$ React Dashboard | **Hoạt động thông suốt 100%** trên cả 8 REST endpoints và 3 màn hình giao diện (`InboxPage`, `TesterPage`, `AnalyticsPage`). | `tests/test_end_to_end_pipeline.py`, `tests/test_api_tickets.py`, `scripts/verify_system.py` | **PASSED** |
| **2. Tính minh bạch & giải trình của Priority Engine** | 100% ticket được tính điểm bằng công thức toán học Rule-based kèm mảng `reasons` giải trình chi tiết | **100% ticket** trả về đối tượng `priority_breakdown` gồm `base`, `urgency_bonus`, `intensity_bonus`, `aspect_bonus` và danh sách lý do tiếng Việt rõ ràng; hiển thị trực tiếp trên modal `PriorityBreakdown.tsx`. | `core/priority/priority_engine.py`, `tests/test_priority_engine.py` | **PASSED** |
| **3. Kiểm soát ca biên, chống DoS & ranh giới English-only** | Không crash trước dữ liệu xấu; chặn ngoại ngữ an toàn với `needs_manual_review = True` | Vượt qua toàn bộ bộ bài test hồi quy cho các lỗi ca biên; chặn chính xác chuỗi rỗng, HTML rỗng và payload $> 5000$ ký tự bằng HTTP 422. | `tests/test_regression_issues.py`, `tests/test_preprocessing.py` | **PASSED** |
| **4. Kỷ luật kỹ thuật, Linter & CI/CD** | 100% commit theo Conventional Commits; CI kiểm tra tự động Backend & Frontend | `ruff check .` (0 lỗi), `pytest` (100% passed), `pnpm run check` (`tsc --noEmit && eslint src` — 0 lỗi), `vitest` (3/3 passed). | `.github/workflows/ci.yml`, `.github/workflows/ai-review.yml` | **PASSED** |
| **5. Đóng gói & dữ liệu Demo sẵn sàng bảo vệ** | Khởi chạy bằng 1 lệnh (`make up` / `make seed`), có sẵn dữ liệu mẫu đa kịch bản | Kịch bản `scripts/seed_demo_data.py` nạp 15 ticket mẫu bao phủ đủ P0–P3 và ngoại ngữ; Live Tester tích hợp sẵn 5 nút kịch bản mẫu chạy tức thì. | `docker.yaml`, `docker-compose.demo.yml`, `Makefile` | **ACCEPTED** |

> **Xác nhận nghiệm thu nội bộ & đủ điều kiện bảo vệ (Week 13 Sign-off):**
> - **Đại diện Quản lý Dự án (PM):** *Võ Tấn Đức* — Xác nhận hoàn tất 100% gói công việc WBS và hồ sơ quản trị.
> - **Đại diện Kỹ thuật (Tech Lead):** *Lê Công Quốc Mỹ* — Xác nhận kiến trúc, CSDL và API đạt chuẩn ổn định.
> - **Đại diện Kiểm định Chất lượng (QA/QC):** *Nguyễn Phương Thảo* — Xác nhận vượt qua toàn bộ bộ kiểm thử tự động và hồi quy.

#### 6.2. Bài học kinh nghiệm rút ra (Key Lessons Learned)
1. **Kiến trúc hợp đồng đóng băng (`Frozen Dataclass Contract`) là chìa khóa sống còn của dự án AI:** Việc định nghĩa sớm `AbsaResult` tại `base.py` và xây dựng `MockSentimentModel` tất định đã cứu dự án khỏi nguy cơ đình trệ khi chờ đợi huấn luyện mô hình Deep Learning. Nhóm Backend và Frontend đã hoàn thiện 100% tính năng nghiệp vụ, database và giao diện ngay trên môi trường CPU thông thường.
2. **Các thư viện NLP có sẵn (`langdetect`, Regex) luôn thất bại ở các ca biên thực tế nếu thiếu luật bảo vệ (Guardrails):** Thư viện `langdetect` hoạt động tốt trên văn bản dài nhưng sai tới 40% trên câu khiếu nại ngắn 1–4 từ; hay luật phủ định ngữ nghĩa đơn giản có thể vô tình triệt tiêu chính từ khóa sự cố (`"did not receive my refund"`). Bài học rút ra là mọi bộ lọc NLP trong môi trường sản xuất đều phải đi kèm heuristic bảo vệ ca biên và bộ kiểm thử hồi quy chuyên biệt.
3. **Tài liệu hóa và cấu hình YAML phải được kiểm tra bằng Unit Test:** Như đã phát hiện ở đợt rà soát thứ hai (`docs/Issue-second.md`), mọi file cấu hình nghiệp vụ (`priority_rules.yaml`, `aspects.yaml`) cần có unit test kiểm chứng việc thay đổi giá trị trong YAML thực sự làm thay đổi đầu ra của hàm.

---

### 7. Phản tư & cải tiến: Nhóm sẽ làm gì khác đi nếu thực hiện lại (Reflection: What Would We Do Differently)

Nhìn lại toàn bộ hành trình 14 tuần phát triển dự án `TICKET-TRIAGE-01`, nếu bắt đầu lại từ tuần 1, nhóm **DogTowFaces** sẽ thực hiện **4 thay đổi chiến lược** sau:

1. **Thiết lập quy trình tự động kiểm tra đồng bộ hợp đồng OpenAPI (`Contract Drift Check`) ngay trong GitHub Actions CI từ tuần 3:**
   - *Vấn đề đã gặp:* Nhóm từng viết tay `ticket-triage-fe/src/api/schema.d.ts`, dẫn đến việc khi chạy lệnh `make gen-api` (`openapi-typescript`) thì cấu trúc kiểu bị ghi đè làm gãy trình biên dịch Frontend (`Issue #8` & `#11`).
   - *Cách làm khác đi:* Ngay từ đầu, chỉ sinh tự động `src/api/generated.ts` từ `app.openapi()` và thêm một bước trong `.github/workflows/ci.yml` để so khớp `contracts/openapi.json` với schema thực tế của FastAPI.
2. **Đơn giản hóa kiến trúc hàng đợi: Sử dụng SQLite Indexed Queue làm nguồn sự thật duy nhất thay vì duy trì song song `heapq` trong RAM và SQLite trên đĩa:**
   - *Vấn đề đã gặp:* Việc giữ đồng thời `TicketPriorityQueue` (`heapq` in-memory) và bảng `tickets` trong SQLite khiến nhóm tốn nhiều công sức xử lý lỗi bất đồng bộ khi ticket chuyển sang trạng thái `resolved` (`Issue #7`) và đồng bộ đối tượng trong heap (`Issue #13`), trong khi endpoint `GET /api/v1/tickets` thực chất vẫn truy vấn trực tiếp từ SQLite với `ORDER BY priority_score DESC, created_at ASC`.
   - *Cách làm khác đi:* Với quy mô dưới 100.000 ticket của bài toán vừa và nhỏ, việc đánh Composite Index trên `(status, priority_score DESC, created_at ASC)` trong SQLite (chế độ WAL) vừa đạt tốc độ truy vấn vài mili-giây, vừa đảm bảo tính bền vững mà không cần đồng bộ hai nơi.
3. **Đưa bộ dữ liệu kiểm thử gán nhãn (`testset_human_labeled.json`) và script đo độ đồng thuận vào kho Git ngay từ tuần 6:**
   - *Vấn đề đã gặp:* Các tệp dữ liệu đánh giá định lượng và notebook thực nghiệm trên Google Colab được lưu trữ rời rạc trên Google Drive thay vì đưa tập testset nhỏ gọn (150–200 mẫu JSON) vào thư mục `ticket-triage-be/tests/data/` để chạy benchmark tự động.
   - *Cách làm khác đi:* Commit trực tiếp tập `testset_human_labeled.json` vào repository và viết một pytest benchmark tự động kiểm tra độ đồng thuận ($\ge 80\%$) của `calculate_priority()` mỗi khi có thay đổi trong `priority_rules.yaml`.
4. **Chốt sớm công nghệ Frontend (React SPA vs Streamlit) ngay ở giai đoạn lập kế hoạch (Tuần 3):**
   - *Vấn đề đã gặp:* Việc lên kế hoạch ban đầu bằng Streamlit trong Charter/WBS rồi sau đó chuyển sang React 18 + TypeScript + Vite trong quá trình code tuy mang lại sản phẩm đẹp và mượt hơn, nhưng khiến nhóm phải tốn thêm thời gian cập nhật lại tài liệu kiến trúc và xử lý thay đổi phạm vi (`CR-03`).
   - *Cách làm khác đi:* Đánh giá kỹ yêu cầu UX (polling thời gian thực không giật trang, modal giải trình tương tác) ngay từ tuần 2 để chọn thẳng kiến trúc React + Vite + TailwindCSS ngay trong WBS ban đầu.

---

## III. BẢNG ĐỐI CHIẾU LIÊN KẾT HỒ SƠ ĐỒ ÁN (MASTER ARTIFACT INDEX)

| STT | Tên hồ sơ / hiện vật kiểm toán (Artifact) | Đường dẫn tệp / liên kết thực tế | Cột mốc tuần |
| :-: | :--- | :--- | :---: |
| 1 | **Project Charter v3.0** | [Project-Charter-Ticket-Triage-System.md](./Project-Charter-Ticket-Triage-System.md) | Week 2 (M1) |
| 2 | **Work Breakdown Structure (WBS v3.0)** | [WBS-Ticket-Triage-System.md](./WBS-Ticket-Triage-System.md) | Week 3 (M1) |
| 3 | **System Architecture Report v3.0** | [System-Ticket-Report.md](./System-Ticket-Report.md) | Week 4 (M2) |
| 4 | **Dynamic Risk Register (Week 6 & Week 11 Updates)** | [Risk-Register-Ticket-Triage-System.md](./Risk-Register-Ticket-Triage-System.md) | Weeks 6 & 11 (M4, M6) |
| 5 | **Issues Tracker & System Synchronization (`Issue-second.md`)** | [Issue-second.md](./Issue-second.md) | Weeks 6–11 |
| 6 | **Kế hoạch thực thi Backend & Frontend** | [Backend-Plan.md](./Backend-Plan.md) · [Frontend-Plan.md](./Frontend-Plan.md) | Weeks 7–12 (M7) |
| 7 | **Bộ kiểm thử hồi quy & toàn trình (Pytest Suite)** | [ticket-triage-be/tests/](../ticket-triage-be/tests/) | Weeks 6–13 (M8) |
| 8 | **Hợp đồng giao tiếp OpenAPI 3.1** | [contracts/openapi.json](../contracts/openapi.json) | Weeks 4–12 |
| 9 | **Luồng CI & AI Code Review tự động (GitHub Actions)** | [ci.yml](../.github/workflows/ci.yml) · [ai-review.yml](../.github/workflows/ai-review.yml) | Weeks 2–14 |
