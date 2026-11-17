# BỘ SLIDE THUYẾT TRÌNH BẢO VỆ TRƯỚC HỘI ĐỒNG & TỰ ĐÁNH GIÁ THEO RUBRIC (WEEK 15 DEFENSE SLIDES & RUBRIC SELF-ASSESSMENT)
## Dự án: Hệ thống phân loại & định tuyến phản hồi khách hàng theo cảm xúc (*Sentiment-Driven Ticket Triage System*)

**Mã dự án:** `TICKET-TRIAGE-01` | **Học phần:** Quản trị dự án phần mềm  
**Giảng viên hướng dẫn:** *Nguyễn Thanh Tuấn*  
**Nhóm thực hiện:** *DogTowFaces* (Võ Tấn Đức, Lê Công Quốc Mỹ, Nguyễn Văn Lê Duy, Nguyễn Viết Pháp, Nguyễn Phương Thảo)  
**Cột mốc áp dụng:** **Tuần 15 — Bảo vệ đồ án cuối kỳ (Week 15 Capstone Defense)** — *Ngày lập: 15/11/2026*  
**Tài liệu căn cứ:** [Risk-Register-Ticket-Triage-System.md](./Risk-Register-Ticket-Triage-System.md) · [Final-Report-Evidence-Package-Ticket-Triage-System.md](./Final-Report-Evidence-Package-Ticket-Triage-System.md)

---

## PHẦN I: TỰ ĐÁNH GIÁ THEO RUBRIC HỌC PHẦN (MILESTONE & DEFENSE RUBRIC SELF-ASSESSMENT)

### 1.1. Bảng đối soát 6 mốc kiểm tra theo tuần (Weekly Checkpoints Pass/Fail Audit)

Theo quy định của học phần, mỗi cột mốc tuần là một cổng kiểm tra **Pass/Fail** dựa trên tiêu chuẩn *"Dự án thực tế" (Real repo, Real stakeholder, Real evidence)*. Dưới đây là bảng kiểm toán toàn bộ 6 mốc của dự án `TICKET-TRIAGE-01`:

| Tuần (Week) | Hạng mục bàn giao (Deliverable) | Tiêu chuẩn đạt yêu cầu ("Meets the bar" means) | Bằng chứng thực tế trong dự án `TICKET-TRIAGE-01` (Real Project Evidence) | Tự đánh giá (Status) |
| :---: | :--- | :--- | :--- | :---: |
| **Week 2** | **Real Project Charter** | Điền đầy đủ các thành phần bắt buộc bằng câu trả lời thực tế của nhóm (không dùng văn bản giữ chỗ); dự án đạt chuẩn "thực tế". | [Project-Charter-Ticket-Triage-System.md](./Project-Charter-Ticket-Triage-System.md): Xác lập rõ bài toán FIFO tại trung tâm CSKH, kiến trúc 2 bài toán độc lập (`ABSA Zero-shot NLI` + `Rule-based Priority & Queue`), mục tiêu SMART định lượng ($F_1 \ge 0.78$, độ đồng thuận $\ge 80\%$) và phân công 5 thành viên *DogTowFaces*. | **PASS** ✅ |
| **Week 3** | **Real WBS** | Hướng sản phẩm bàn giao (*Deliverable-oriented*), tuân thủ Quy tắc 100%, mỗi gói công việc có quy mô ~1–2 tuần. | [WBS-Ticket-Triage-System.md](./WBS-Ticket-Triage-System.md): Phân rã thành **8 nhóm (Level 2)** và **38 Work Packages (Level 3)** đặt tên bằng cụm danh từ chỉ sản phẩm, tổng nỗ lực **152 Story Points** (mỗi gói từ 3–8 SP, tương đương 1–2 tuần làm việc), kèm WBS Dictionary và tiêu chí nghiệm thu chi tiết. | **PASS** ✅ |
| **Week 6** | **Risk Register update #1** | Chứa các rủi ro **thực sự đã xảy ra trong Sprint 1** — không chỉ là các rủi ro lý thuyết, chung chung. | [Risk-Register-Ticket-Triage-System.md](./Risk-Register-Ticket-Triage-System.md) (Mục 3.1): Ghi nhận 6 nhóm rủi ro kỹ thuật nổ ra thật trong Sprint 1 (`RR-01` $\rightarrow$ `RR-06`), bao gồm: trôi phạm vi đa ngôn ngữ (`RR-01`), `langdetect` nhận nhầm 40% câu tiếng Anh ngắn (`RR-04`), regex `clean_text` biến `"coool"` thành `"col"` (`RR-04`), hàm `_is_negated` triệt tiêu nhầm điểm khẩn cấp của từ `"refund"` (`RR-05`), lỗi substring `"issue"` $\rightarrow$ `"sue"` trong `mock.py` (`RR-03`), và lệch 7 giờ GMT+7 (`RR-06`). | **PASS** ✅ |
| **Week 7** | **Sprint 1 Retrospective + Sprint 2 Plan** | Phản ánh trung thực những gì *thực sự* đã diễn ra (cụ thể, không chung chung); kế hoạch Sprint 2 tích hợp bài học từ Sprint 1. | [Risk-Register-Ticket-Triage-System.md](./Risk-Register-Ticket-Triage-System.md) & [Issue-second.md](./Issue-second.md): Phân tích Root Cause của các lỗi phát sinh cuối Sprint 1, phân công lại nhiệm vụ theo mã WBS cho 5 thành viên và lập **Kế hoạch triển khai 3 đợt (Sprint 2 Implementation Plan)** gồm: viết bộ kiểm thử hồi quy `test_regression_issues.py`, nạp cấu hình YAML động và đại tu toàn diện giao diện React SPA. | **PASS** ✅ |
| **Week 11** | **Risk Register update #2 + Real scope change handled** | Sổ đăng ký rủi ro thể hiện sự tiến hóa thực sự kể từ tuần 6; ít nhất một thay đổi phạm vi thực tế được xử lý và ghi nhận. | [Risk-Register-Ticket-Triage-System.md](./Risk-Register-Ticket-Triage-System.md) (Mục 3.2):<br>1. **Tiến hóa rủi ro:** Đóng toàn bộ rủi ro tuần 6 (`RR-01` $\rightarrow$ `RR-06`) cùng 2 rủi ro về Frontend UI/UX & Lockfile CI (`RR-07, RR-08`), đồng thời kiểm soát và xử lý 2 rủi ro đồng bộ ở đợt 2 (`RR-09, RR-10` từ [Issue-second.md](./Issue-second.md)).<br>2. **Xử lý Scope Change thực tế:** Ghi nhận `CR-01` (cắt dịch máy sang English-only ở PR `#11`), `CR-02` (bỏ nhãn `not_mentioned` ở PR `#28`, đổi thang điểm `0–100` 3 mức), và `CR-03` (nâng cấp giao diện từ Streamlit sang React 18 + Vite + TailwindCSS + Recharts SPA ở PR `#30` & Commit `5f995c4`). | **PASS** ✅ |
| **Week 13** | **Project Closure** | Nghiệm thu thực tế trên sản phẩm bàn giao thực tế; thực hiện tổng kết hồi cứu toàn dự án (*Whole-project retrospective*). | [Final-Report-Evidence-Package-Ticket-Triage-System.md](./Final-Report-Evidence-Package-Ticket-Triage-System.md) (Mục II.6 & II.7): Chạy script nghiệm thu `ticket-triage-be/scripts/verify_system.py`, hoàn tất 100% bài kiểm thử Backend + Frontend, đóng gói Docker Compose (`docker-compose.demo.yml`) và đúc kết 3 bài học kinh nghiệm cùng 4 cải tiến chiến lược toàn dự án. | **PASS** ✅ |

---

### 1.2. Bảng tự đánh giá & chấm điểm theo Rubric bảo vệ cuối kỳ (Week 15 Final Defense Rubric)

| Tiêu chí chấm điểm (Rubric Component) | Trọng số (Weight) | Giải trình bằng chứng thực tế từ hệ thống `TICKET-TRIAGE-01` (Evidence Justification) | Điểm tự đánh giá (Thang 10) | Điểm quy đổi theo trọng số |
| :--- | :---: | :--- | :---: | :---: |
| **0. Cổng xác thực dự án (`Project Authenticity Gate` — real repo/deliverable, real management event handled)** | **Pass / Fail Gate**<br>*(Khống chế tối đa 5/10 nếu không đạt)* | **ĐẠT TUYỆT ĐỐI (PASS):**<br>- **Real Deliverable:** Hệ thống Full-stack hoạt động hoàn chỉnh gồm Backend FastAPI + SQLAlchemy 2.0 + SQLite WAL (`ticket-triage-be/`) và Frontend React 18 + TypeScript + TailwindCSS + Recharts (`ticket-triage-fe/`).<br>- **Real Management Events:** Xử lý 2 đợt rà soát lỗi kỹ thuật thực tế (#1–#8 và #9–#14) cùng 3 yêu cầu thay đổi phạm vi (`CR-01, CR-02, CR-03`). | **PASS** | **Mở khóa 100% thang điểm** |
| **1. Tính đầy đủ & khả thi của kế hoạch (`Plan completeness & feasibility`: WBS, schedule, risk)** | **30%** | - **WBS chuẩn PMI:** 8 nhóm, 38 Work Packages phủ 100% phạm vi, ước lượng 152 SP hợp lý cho nhóm 5 người trong 15 tuần.<br>- **Schedule & Milestones:** 10 cột mốc (M1–M10) phân định rõ điểm đóng băng Bài toán 1 (M5) và Bài toán 2 (M6).<br>- **Dynamic Risk Register:** 10 rủi ro kỹ thuật chiều sâu (`RR-01` $\rightarrow$ `RR-10`) được phân bổ cân đối cho cả 5 thành viên theo đúng commit thực tế, có chiến lược *Avoid / Mitigate / Transfer / Accept* cụ thể và tiến hóa rõ rệt giữa tuần 6 và tuần 11. | **9.5 / 10** | **2.85 / 3.00** |
| **2. Sự phù hợp của phương pháp luận (`Methodology fit`: Agile / Hybrid, justified)** | **20%** | - Áp dụng **Agile kết hợp Contract-First Iterative Development** cực kỳ phù hợp với bài toán tích hợp AI.<br>- Đóng băng dataclass `AbsaResult` (`base.py`) và xây dựng `MockSentimentModel` tất định (MD5 seed) giúp tách rời hoàn toàn rủi ro huấn luyện GPU Colab khỏi tiến độ xây dựng Priority Engine, SQLite và React UI. | **9.5 / 10** | **1.90 / 2.00** |
| **3. Bằng chứng thực thi thực tế (`Real execution evidence`: commit/board history, burndown, CI/CD, tests)** | **30%** | - **Lịch sử Git & PR minh bạch của cả 5 thành viên:** Tuân thủ Conventional Commits, phân nhánh `feat/*`, `fix/*`, `docs/*`, tích hợp cả GitHub Actions CI (`ci.yml`) và AI Reviewer (`ai-review.yml`).<br>- **Kiểm thử hồi quy thực chất:** Toàn bộ bộ kiểm thử pytest (bao gồm `test_regression_issues.py` khóa chặt các lỗi ca biên thực tế) và vitest đều vượt qua 100%. | **9.0 / 10** | **2.70 / 3.00** |
| **4. Thuyết trình, Live Demo & phản biện Q&A (`Presentation, Live Demo & Defense Q&A`)** | **20%** | - Bộ 15 slide cấu trúc mạch lạc, kết nối chặt chẽ giữa quản trị dự án và kiến trúc kỹ thuật.<br>- Kịch bản **Live Demo 5 phút** chạy trực tiếp trên `InboxPage`, `TesterPage` (5 kịch bản mẫu + ca biên phủ định & ngoại ngữ, hiệu ứng chống nháy `MIN_SKELETON_MS` và `useCountUp`) và `AnalyticsPage`.<br>- Chuẩn bị sẵn bộ câu hỏi phản biện chuyên sâu về cả PM, Backend/AI lẫn Frontend UI/UX. | **9.5 / 10** | **1.90 / 2.00** |
| **TỔNG ĐIỂM TỰ ĐÁNH GIÁ DỰ KIẾN** | **100%** | **Hồ sơ nhất quán, trung thực, cân đối đóng góp 5 thành viên, có chiều sâu kỹ thuật và quản trị thực tế cao.** | **9.35 / 10** | **9.35 / 10.00** |

---

## PHẦN II: BỘ SLIDE THUYẾT TRÌNH BẢO VỆ TRƯỚC HỘI ĐỒNG (15 SLIDES CHI TIẾT)

> **Tổng thời lượng thuyết trình tiêu chuẩn:** 15 – 18 phút (Thuyết trình slide: 10–12 phút | Live Demo trực tiếp: 5 phút | Phản biện Q&A: 10–15 phút).  
> **Phân công trình bày cân đối theo đúng đóng góp thực tế của 5 thành viên:**
> - **Võ Tấn Đức (PM & DevOps):** Slide 1, 2, 4, 9, 14, 15.
> - **Lê Công Quốc Mỹ (Tech Lead - Backend & CI):** Slide 3, 6, 13.
> - **Nguyễn Văn Lê Duy (Lead Dev Bài toán 1 - ABSA):** Slide 7.
> - **Nguyễn Viết Pháp (Lead Dev Bài toán 2 - Priority & Queue):** Slide 8, 10.
> - **Nguyễn Phương Thảo (Frontend UI/UX & QA Engineer):** Slide 5 (WBS v3.0), Slide 11 (Change Management, React SPA Overhaul & QA), Slide 12 (Live Demo trên giao diện React SPA).

---

### SLIDE 1: Trang bìa & định danh dự án (Title Slide)
* **Tiêu đề slide:** HỆ THỐNG PHÂN LOẠI & ĐỊNH TUYẾN PHẢN HỒI KHÁCH HÀNG THEO CẢM XÚC (*Sentiment-Driven Ticket Triage System*)
* **Nội dung chính trên slide:**
  - **Mã dự án:** `TICKET-TRIAGE-01` | **Học phần:** Quản trị dự án phần mềm
  - **Giảng viên hướng dẫn:** ThS. Nguyễn Thanh Tuấn
  - **Nhóm thực hiện — *DogTowFaces*:**
    1. Võ Tấn Đức (`23IT.EB024` - `@Ducinviciable`) — *Project Lead / PM & DevOps*
    2. Lê Công Quốc Mỹ (`23IT.EB060` - `@lupinname`) — *Technical Lead (Backend Core & CI)*
    3. Nguyễn Văn Lê Duy (`23IT.EB026` - `@conangamo`) — *Lead Dev — Bài toán 1 (ABSA Subsystem)*
    4. Nguyễn Viết Pháp (`23IT.EB070` - `@vietphap035`) — *Lead Dev — Bài toán 2 (Priority Engine & Queue)*
    5. Nguyễn Phương Thảo (`23IT.EB098` - `@phuongthaonee`) — *Frontend UI/UX Engineer & QA/QC*
  - **Khẩu hiệu thiết kế:** *"Aspect Severity is the Foundation — Sentiment & Urgency are the Amplifiers — Auditable Rule-Based Triage"*

---

### SLIDE 2: Bài toán nghiệp vụ & mục tiêu dự án (Business Case & SMART Objectives)
* **Tiêu đề slide:** Tại sao FIFO thất bại trong chăm sóc khách hàng & mục tiêu SMART của dự án
* **Nội dung chính trên slide:**
  - **Nỗi đau vận hành (The FIFO Bottleneck):**
    - Trung tâm CSKH thương mại điện tử nhận hàng nghìn ticket tiếng Anh/ngày.
    - Xử lý theo **FIFO (Đến trước phục vụ trước)** khiến khách hàng bị *trừ tiền 2 lần (`charged twice`)*, *dọa kiện (`lawsuit`)* hoặc *mất hàng* phải xếp hàng sau các câu hỏi *tra cứu thông số thông thường*.
  - **Triết lý giải quyết cốt lõi:**
    - *Bình tĩnh báo cáo sự cố nghiêm trọng* (*"I was charged twice"*) **>** *Giận dữ vì lỗi nhỏ* (*"The box is ugly!!!"*).
    - Tuyệt đối **không dùng ML hộp đen (Black-box)** để chấm điểm ưu tiên $\rightarrow$ bắt buộc dùng **Rule-based toán học có giải trình (`reasons`)**.
    - Chuyên biệt **English-only**: Tự động chặn và gắn cờ `needs_manual_review = True` cho ngoại ngữ.
  - **4 mục tiêu SMART (Charter v3.0):**
    1. **Bài toán 1 (ABSA NLI):** Nhận diện 5 khía cạnh CSKH chuẩn, đạt $F_1\text{-macro} \ge 0.78$ trước tuần 9 (M5).
    2. **Bài toán 2 (Priority & Queue):** Công thức *Worst-Aspect-Wins* + `heapq` FIFO tie-break, đạt độ đồng thuận $\ge 80\%$ với nhãn thủ công trước tuần 11 (M6).
    3. **Kỷ luật kỹ thuật:** 100% Conventional Commits, GitHub Actions CI + AI Code Review trên mọi PR.
    4. **Sản phẩm tích hợp:** Full-stack FastAPI + SQLite + React 18 SPA sẵn sàng demo trực tiếp tại tuần 15 (M10).

---

### SLIDE 3: Kiến trúc hệ thống & phân tách 2 bài toán độc lập (System Architecture)
* **Tiêu đề slide:** Kiến trúc phân tách 2 bài toán & luồng xử lý toàn trình (End-to-End Pipeline)
* **Nội dung chính trên slide:**
  - **Sơ đồ luồng 6 bước (`pipeline.py`):**
    1. `Ingest (Pydantic v2)` $\rightarrow$ Chặn chuỗi rỗng, HTML rác, giới hạn `[3, 5000]` ký tự.
    2. `Module 1: Preprocessing` $\rightarrow$ `normalizer.py` (NFC, ẩn PII, giữ CAPS/`!!!`) + `lang_validator.py` (cổng chặn ngoại ngữ $\rightarrow$ điểm sàn `50.0`) + `keyword_prefilter.py` (lọc ứng viên khía cạnh).
    3. `Bài toán 1: ABSA Subsystem` $\rightarrow$ `ZeroShotNliModel` (`distilbart-mnli` / `deberta-v3`) hoặc `MockSentimentModel` $\rightarrow$ xuất dataclass đóng băng **`AbsaResult`**.
    4. `Bài toán 2: Priority Engine` $\rightarrow$ Công thức *Worst-Aspect-Wins* $\rightarrow$ xuất **`PriorityBreakdown`** (`0–100`, `CRITICAL / MEDIUM / LOW`, `reasons`).
    5. `Storage & Queue` $\rightarrow$ Ghi đơn giao dịch (Single Atomic Transaction) vào **SQLite (WAL mode)** + đẩy vào **Max-Heap (`heapq`)**.
    6. `React 18 SPA Dashboard` $\rightarrow$ Hộp thư ưu tiên (`/`), Live Tester (`/tester`), Thống kê (`/analytics`).

---

### SLIDE 4: Phương pháp luận Agile & cơ chế phát triển song song (Methodology Fit — 20% Rubric)
* **Tiêu đề slide:** Tại sao chọn Agile + Contract-First Iterative Development?
* **Nội dung chính trên slide:**
  - **Thách thức đặc thù của đồ án AI sinh viên:**
    - Huấn luyện/fine-tune NLI phụ thuộc vào Google Colab GPU, tốn thời gian chuẩn bị dữ liệu.
    - Máy cá nhân chạy Docker không có GPU rời.
    - Nếu làm tuần tự (Waterfall): Nhóm làm Backend, Database và Frontend sẽ bị "đứng hình" chờ nhóm AI suốt 6 tuần đầu.
  - **Giải pháp phương pháp luận của *DogTowFaces*:**
    - **Chốt cứng hợp đồng từ tuần 3:** Đóng băng `AbsaResult` (`base.py`) và `contracts/openapi.json`.
    - **Chiến lược `MockSentimentModel` tất định + `MOCK_TICKETS`:** Dùng regex word-boundary `\b` + MD5 seed giả lập đầu ra của Bài toán 1.
    - **Chạy 3 track song song trong mỗi Sprint 2 tuần:**
      - *Track 1 (Lê Duy):* Dữ liệu CSKH, Keyword Pre-filter, NLI Baseline & Fine-tuning.
      - *Track 2 (Viết Pháp + Quốc Mỹ):* SQLite ORM, Priority Engine, `heapq` & FastAPI.
      - *Track 3 (Phương Thảo):* Giao diện React 18 SPA (`InboxPage`, `TicketTable`, `TesterPage`) & kiểm thử QA.

---

### SLIDE 5: Cấu trúc phân rã công việc (WBS v3.0), ước lượng & lịch trình (Plan Completeness — 30% Rubric)
* **Tiêu đề slide:** Đường cơ sở phạm vi: WBS v3.0 (38 Work Packages - 152 Story Points) & 10 Milestones
* **Nội dung chính trên slide:**
  - **Cây WBS v3.0 tuân thủ chuẩn PMI (100% Rule & Deliverable-Oriented — PR `#11`):**
    - `1.1 Quản trị dự án` (5 WP - 16 SP) | `1.2 Hạ tầng & dữ liệu` (7 WP - 26 SP)
    - `1.3 Module 1: Tiền xử lý` (4 WP - 16 SP) | `1.4 Bài toán 1: ABSA NLI` (5 WP - 24 SP)
    - `1.5 Bài toán 2: Priority Engine` (4 WP - 18 SP) | `1.6 Bài toán 2: Queue & SQLite` (4 WP - 16 SP)
    - `1.7 Module 5: Dashboard UI` (4 WP - 18 SP) | `1.8 Tích hợp & kiểm thử` (5 WP - 18 SP)
  - **Lộ trình 10 cột mốc kiểm soát (M1 $\rightarrow$ M10):**
    - `M1 (W2)`: Charter & WBS v3.0 | `M2 (W4)`: Architecture & SQLite Schema
    - `M3 (W6)`: Preprocessing + Priority v1 (Mock) | `M4 (W7)`: Risk Update #1 & Sprint 1 Retro
    - `M5 (W9)`: **Freeze Bài toán 1 (ABSA)** | `M6 (W11)`: **Freeze Bài toán 2 (Priority)** + Risk Update #2
    - `M7 (W12)`: Full Integration & React SPA Overhaul | `M8 (W13)`: **Code Freeze & Acceptance** | `M9 (W14)`: Evidence Package | `M10 (W15)`: Defense.

---

### SLIDE 6: Đi sâu kỹ thuật (1) — Module 1: Tiền xử lý & cổng kiểm duyệt tiếng Anh
* **Tiêu đề slide:** Cổng kiểm soát dữ liệu đầu vào: Chuẩn hóa NLP, chặn ngoại ngữ & lọc khía cạnh
* **Nội dung chính trên slide:**
  - **1. Làm sạch bảo toàn cảm xúc (`normalizer.py`):**
    - Ẩn thông tin nhạy cảm PII (`[EMAIL]`, `[URL]`), loại bỏ HTML tags.
    - Nén ký tự lặp $\ge 3$ về **2 ký tự chuẩn NLP (`r"\1\1"`)**: *"coool"* $\rightarrow$ *"cool"*, *"goood"* $\rightarrow$ *"good"* (tránh lỗi làm hỏng từ gốc).
    - **Bảo toàn 100%** chữ viết hoa (`CAPS LOCK`) và chuỗi dấu cảm thán (`!!!`) cho bước tính cường độ.
  - **2. Cổng xác thực tiếng Anh kết hợp heuristic câu ngắn (`lang_validator.py`):**
    - Câu ngắn ($< 5$ từ hoặc $< 35$ ký tự) thuần ASCII Latin $\rightarrow$ Mặc định là tiếng Anh hợp lệ (`en`, `conf = 1.0`).
    - Câu dài $\rightarrow$ Kiểm tra qua `langdetect` (ngưỡng `0.70`). Nếu là ngoại ngữ (Việt, Pháp...) $\rightarrow$ gắn `needs_manual_review = True`, gán điểm sàn `50.0` (`MEDIUM`), **không gọi mô hình AI**.
  - **3. Bộ lọc trước từ khóa (`keyword_prefilter.py`):**
    - Quét regex word-boundary `\b...\b` tìm ứng viên trong 5 khía cạnh $\rightarrow$ giảm $2\times - 3\times$ tải suy luận NLI.

---

### SLIDE 7: Đi sâu kỹ thuật (2) — Bài toán 1: Hệ thống phân tích khía cạnh ABSA Zero-shot NLI
* **Tiêu đề slide:** Bài toán 1 (ABSA Subsystem): Taxonomy động & suy luận Zero-shot NLI 3 lớp
* **Nội dung chính trên slide:**
  - **Nguồn taxonomy duy nhất (`configs/aspects.yaml`):**
    - `customer_service` (weight `1.0`) | `refund_payment` (weight `1.0`) | `product_quality` (weight `0.8`) | `shipping` (weight `0.7`) | `general` (weight `0.5`).
  - **Kiến trúc suy luận 2 bước (`core/sentiment/baseline.py`):**
    - **Bước 1:** Nhận danh sách `candidate_aspects` từ `keyword_prefilter`.
    - **Bước 2:** Kiểm định giả thuyết NLI (`aspect_hypotheses.yaml`): *"The customer's feedback regarding {aspect} is {sentiment}"* trên 3 lớp cảm xúc chuẩn: `{negative, neutral, positive}`.
    - **Tối ưu hóa kiến trúc (PR `#28`):** Loại bỏ hoàn toàn nhãn thứ 4 `not_mentioned` dư thừa, nạp YAML qua `@lru_cache`.
  - **Cơ chế Fallback minh bạch (`/api/v1/health`):**
    - Nếu thiếu thư viện GPU hoặc chạy chế độ dev, tự động chuyển về `MockSentimentModel` (tất định theo mã băm MD5) và bật cờ `is_mock: true`, ghi log cảnh báo rõ ràng.

---

### SLIDE 8: Đi sâu kỹ thuật (3) — Bài toán 2: Công thức Priority Engine & hàng đợi `heapq`
* **Tiêu đề slide:** Bài toán 2 (Priority & Queue): Toán học minh bạch *Worst-Aspect-Wins* & Max-Heap FIFO
* **Nội dung chính trên slide:**
  - **Công thức tính điểm thuần túy (`priority_engine.py`):**
    $$\text{score} = \min\left(100.0, \; \text{base} + \text{urgency\_bonus} + \text{intensity\_bonus} + \text{aspect\_bonus}\right)$$
    1. **Điểm nền (`base`):** Negative $= 60.0 \times \text{conf}$ | Neutral $= 20.0$ | Positive $= 5.0$.
    2. **Từ khóa khẩn cấp (`urgency_bonus`, trần `30.0`):** Phân tầng `CRITICAL` (`lawsuit`, `fraud`, `chargeback`...) và `HIGH` (`refund`, `broken`, `dispute`...). Câu kết được ưu tiên điểm cao hơn câu trước; xử lý phủ định thông minh (`_is_negated` chỉ chặn *"not urgent"*, không chặn *"did not receive my refund"*).
    3. **Cường độ câu (`intensity_bonus`):** $+5.0$ khi có `!!!` hoặc `CAPS LOCK` **VÀ** cảm xúc tổng thể là `negative`.
    4. **Khía cạnh tiêu cực (`aspect_bonus`, trần `20.0`):** Khía cạnh tệ nhất cộng $100\%$ ($W_{\text{worst}} \times \text{conf} \times 10$), các khía cạnh tiêu cực phụ cộng phạt lũy kế $25\%$.
  - **Hàng đợi Max-Heap (`priority_queue.py`) & vòng đời 4 bước (`state_manager.py`):**
    - Khóa heap: `(-priority_score, created_at, ticket_id)` $\rightarrow$ Điểm cao nhất lên đầu, đồng điểm xử lý theo **FIFO**.
    - FSM kiểm soát chặt: `new` $\rightarrow$ `assigned` $\rightarrow$ `in_progress` $\rightarrow$ `resolved` (tự động `queue.remove()` khi đóng vé).

---

### SLIDE 9: Bằng chứng thực thi — Lịch sử Git, CI/CD & vận tốc 2 Sprint (Real Execution Evidence — 30% Rubric)
* **Tiêu đề slide:** Minh chứng thực thi thực tế: Lịch sử commit 5 thành viên, AI Code Review & Burndown 152 SP
* **Nội dung chính trên slide:**
  - **Hệ thống kiểm soát chất lượng tự động kép (GitHub Actions):**
    1. **Standard CI (`ci.yml`):** Tự động chạy `ruff check`, `pytest --cov` (Backend) và `tsc --noEmit`, `eslint`, `vitest` (Frontend) trên mọi PR vào `main`/`dev`.
    2. **Automated AI Code Review (`ai-review.yml` + `ai_reviewer.py`):** Tích hợp mô hình Gemini Flash tự động đọc diff của PR, đối chiếu với `.github/review_guidelines.md` và bình luận bắt lỗi kiến trúc trực tiếp trên GitHub PR.
  - **Tiến độ hoàn thành thực tế qua các giai đoạn (152 / 152 Story Points):**
    - *Weeks 1–4 (Initiation & Planning):* **28/28 SP (100%)** — Charter, WBS v3.0 (PR `#11`), CI, SQLite Schema.
    - *Weeks 5–7 (Sprint 1 - Core & Mock):* **44/52 SP (84.6%)** — Chuyển 8 SP sang đầu Sprint 2 do giữ lại `priority_engine` và `heapq` để sửa 8 lỗi ca biên phát hiện ở cuối tuần 6 (PR `#15`, `#23`).
    - *Weeks 8–12 (Sprint 2 - Regression Fix, YAML & React SPA Overhaul):* **58/64 SP (90.6%)** — Hoàn tất bộ tests hồi quy (PR `#27`), nạp YAML động (PR `#28`), hoàn thiện Inbox & Live Tester (PR `#30`, Commit `5f995c4`).
    - *Weeks 13–14 (Closure & Verification):* **22/22 SP (100%)** — Hoàn tất nghiệm thu toàn hệ thống.

---

### SLIDE 10: Quản trị rủi ro động — Tiến hóa thực tế tuần 6 $\rightarrow$ tuần 11 (Risk Management)
* **Tiêu đề slide:** Sổ đăng ký rủi ro động (`RR-01` $\rightarrow$ `RR-10`): Cân đối 5 thành viên & tiến hóa qua 2 Sprint
* **Nội dung chính trên slide:**
  - **Những rủi ro kỹ thuật đã thực sự nổ ra ở Sprint 1 (Week 6 Update #1):**
    - **`RR-01` (Trôi phạm vi đa ngôn ngữ):** Dịch máy Việt - Anh làm lệch sắc thái từ khóa $\rightarrow$ Cắt bỏ ở PR `#11` (`@phuongthaonee` & `@Ducinviciable`).
    - **`RR-02` & `RR-03` (Độ trễ NLI & Substring trap trong Mock):** Quét 20 lượt NLI/ticket; từ *"issue"* bị bắt nhầm thành *"sue"* $\rightarrow$ Xử lý bởi `@conangamo`.
    - **`RR-04` (Lỗi `langdetect` & `normalizer`):** 40% câu tiếng Anh ngắn (*"Order missing"*) bị nhận nhầm là ngoại ngữ; chữ *"coool"* bị nén thành *"col"* $\rightarrow$ Xử lý bởi `@lupinname` (PR `#27`).
    - **`RR-05` & `RR-06` (Bẫy phủ định `_is_negated`, lệch 7h GMT+7 & `heapq`):** Câu *"I did not receive my refund"* bị mất điểm khẩn cấp; vé `resolved` kẹt trong `heapq` $\rightarrow$ Xử lý bởi `@vietphap035` & `@lupinname`.
  - **Sự tiến hóa trạng thái tại tuần 11 (Week 11 Update #2):**
    - **Đóng thành công 8 rủi ro (`RR-01` $\rightarrow$ `RR-08` $\rightarrow$ `Resolved / Closed`):** Bao gồm cả 2 rủi ro trên Frontend React SPA là `RR-07` (quá tải thông tin bảng Inbox) và `RR-08` (nháy giao diện Live Tester & xung đột `package-lock.json` trên CI) được xử lý tại PR `#30` & Commit `5f995c4`.
    - **Kiểm soát và xử lý 2 rủi ro đồng bộ ở đợt 2 (`RR-09, RR-10` — `docs/Issue-second.md`).**

---

### SLIDE 11: Quản trị thay đổi hành vi, tái thiết kế giao diện React SPA & đảm bảo chất lượng (Change Management & UI/QA)
* **Tiêu đề slide:** Xử lý 3 thay đổi phạm vi (`CR-01` $\rightarrow$ `CR-03`), nâng cấp React SPA & kiểm thử hồi quy
* **Nội dung chính trên slide:**
  - **3 yêu cầu thay đổi phạm vi (Change Requests) đã xử lý:**
    1. **`CR-01` (English-only Boundary — PR `#11`):** Loại bỏ dịch máy tiếng Việt, thay bằng cổng `lang_validator.py` gắn cờ `needs_manual_review = True` và điểm sàn `50.0`.
    2. **`CR-02` (Tối ưu NLI 3 lớp & thang điểm 100 — PR `#28`):** Loại bỏ nhãn thứ 4 `not_mentioned`; chuẩn hóa thang `[0, 100]` với 3 cấp (`CRITICAL` $\ge 70$, `MEDIUM` $30-69$, `LOW` $< 30$).
    3. **`CR-03` (Tái thiết kế giao diện sang React 18 SPA — PR `#30` & Commit `5f995c4`):**
       - Cập nhật đồng bộ các thành phần trên `ticket-triage-fe/` (`InboxPage`, `TicketTable`, `PriorityBreakdown`, `StatusSelect`, `PriorityBadge`, `TesterPage`, `index.css`).
       - Áp dụng bảng màu *Pastel Teal & Severity Highlights*, thanh phân bố khía cạnh trực tiếp trên Inbox, cơ chế chống nháy `MIN_SKELETON_MS = 450ms`, hiệu ứng đếm `useCountUp`, hỗ trợ `prefers-reduced-motion` và xóa `package-lock.json` bảo vệ luồng CI `pnpm`.
  - **Bộ kiểm thử hồi quy (`ticket-triage-be/tests/` & `vitest`):**
    - **100% Pytest Cases PASSED** (bao gồm bộ bài test hồi quy tại `test_regression_issues.py`) + **3/3 Vitest PASSED** + `tsc --noEmit` & `eslint` sạch 100%.

---

### SLIDE 12: Trình diễn trực tiếp hệ thống (LIVE DEMO — 5 phút)
* **Tiêu đề slide:** Kịch bản Live Demo toàn trình: Từ phân tích thời gian thực đến điều phối hàng đợi
* **Nội dung chính trên slide:**
  - **Môi trường trình diễn:** Backend FastAPI + Frontend React SPA.
  - **5 kịch bản demo trực tiếp trước hội đồng:**
    1. **Khám phá hộp thư ưu tiên (`/` - InboxPage):** Quan sát 4 thẻ KPI, thanh phân bố khía cạnh, danh sách vé tự động sắp xếp giảm dần theo `priority_score`, bấm vào vé P0 để mở bảng giải trình toán học `PriorityBreakdown`.
    2. **Thử nghiệm ca khẩn cấp (`/tester` - Live Tester):** Bấm mẫu *"Bị trừ tiền hai lần"* (`"I was charged twice... dispute the chargeback with my bank!"`) $\rightarrow$ Xem hiệu ứng skeleton 450ms & `useCountUp`, điểm số `CRITICAL`, chip `refund_payment` tiêu cực và lý do cộng điểm từ khóa câu kết.
    3. **Kiểm chứng bẫy phủ định (Regression Verification):** Nhập trực tiếp *"I did not receive my refund yet"* vs *"This request is not urgent"* để chứng minh hệ thống phân biệt chính xác từ khóa sự cố và từ khóa hạ nhiệt.
    4. **Kiểm chứng cổng chặn ngoại ngữ (`lang_validator`):** Bấm mẫu tiếng Việt *"Tôi muốn yêu cầu hỗ trợ đổi trả..."* $\rightarrow$ Hệ thống lập tức gắn cờ `Cần duyệt thủ công`, điểm sàn `50.0` (`MEDIUM`).
    5. **Điều phối trạng thái & thống kê (`/analytics`):** Chuyển trạng thái vé từ `Mới` $\rightarrow$ `Đã phân công` $\rightarrow$ `Đang xử lý` $\rightarrow$ `Đã giải quyết` và kiểm tra biểu đồ Recharts cập nhật tức thì.

---

### SLIDE 13: Đóng dự án, bài học kinh nghiệm & phản tư (Closure & Reflection)
* **Tiêu đề slide:** Nhìn lại hành trình 14 tuần: Bài học xương máu & những điều nhóm sẽ làm khác đi
* **Nội dung chính trên slide:**
  - **3 bài học kinh nghiệm cốt lõi (Lessons Learned):**
    1. *Contract-First Architecture cứu tiến độ dự án AI:* Đóng băng `AbsaResult` giúp 80% hệ thống hoàn thiện mà không bị chặn bởi việc huấn luyện GPU.
    2. *UX cho hệ thống AI thời gian thực đòi hỏi xử lý chống nháy (`MIN_SKELETON_MS`) và phân cấp thị giác rõ ràng:* Phản hồi quá nhanh mà không có chuyển cảnh mượt sẽ gây cảm giác giật cục.
    3. *Thư viện NLP có sẵn và cấu hình YAML luôn cần Unit Test bảo vệ:* Không thể tin tưởng mù quáng vào `langdetect` trên câu ngắn hay regex phủ định đơn giản nếu thiếu kiểm thử ca biên.
  - **4 cải tiến nếu thực hiện lại dự án (What We Would Do Differently):**
    1. Đưa bước kiểm tra đồng bộ `openapi.json` (`Contract Drift Check`) vào thẳng GitHub Actions CI ngay từ tuần 3.
    2. Dùng **SQLite Indexed Queue** (`ORDER BY priority_score DESC, created_at ASC` trên WAL mode) làm hàng đợi duy nhất thay vì duy trì kép cả `heapq` trong RAM và SQLite trên đĩa.
    3. Chốt thẳng kiến trúc **React 18 SPA** và chặn `package-lock.json` trong `.gitignore` ngay từ WBS tuần 3 thay vì đi vòng qua thiết kế Streamlit ban đầu.
    4. Đưa tập `testset_human_labeled.json` vào kho Git từ tuần 6 để chạy pytest đo độ đồng thuận tự động.

---

### SLIDE 14: Tổng kết tự đánh giá theo Rubric bảo vệ (Rubric Self-Assessment Summary)
* **Tiêu đề slide:** Đối chiếu kết quả đạt được với tiêu chí chấm điểm bảo vệ tuần 15
* **Nội dung chính trên slide:**
  - **Project Authenticity Gate:** **PASS** (Kho mã nguồn thật, sản phẩm chạy thật, xử lý sự cố kỹ thuật & thay đổi phạm vi thật).
  - **Plan Completeness & Feasibility (30%):** **9.5 / 10** — Charter v3.0, WBS 38 gói công việc (152 SP), Dynamic Risk Register 10 rủi ro cân đối 5 thành viên qua 2 đợt cập nhật.
  - **Methodology Fit (20%):** **9.5 / 10** — Agile + Contract-First (`AbsaResult` + `MockSentimentModel`) giải quyết triệt để nút thắt chờ GPU.
  - **Real Execution Evidence (30%):** **9.0 / 10** — Lịch sử commit/PR đầy đủ, CI + AI Reviewer, 100% bài test pytest + vitest vượt qua, trung thực ghi nhận cả các điểm rà soát đợt 2 (`Issue-second.md`).
  - **Presentation, Live Demo & Q&A (20%):** **9.5 / 10** — Demo trực tiếp toàn trình mượt mà.
  - **Tổng điểm tự đánh giá đề xuất:** **9.35 / 10.0**.

---

### SLIDE 15: Lời cảm ơn & phiên hỏi đáp phản biện (Thank You & Defense Q&A)
* **Tiêu đề slide:** Cảm ơn thầy và hội đồng! — Phiên hỏi đáp & phản biện (Q&A)
* **Nội dung chính trên slide:**
  - **Liên kết kho mã nguồn & hồ sơ kiểm toán:**
    - GitHub Repository: `https://github.com/CRP-2026/Sentiment-Driven-Ticket-Triage-System`
    - GitHub Project Board: `http://github.com/orgs/CRP-2026/projects/1/views/1`
    - Tài liệu đính kèm: Charter v3.0 · WBS v3.0 · System Architecture Report v3.0 · Dynamic Risk Register (W6 & W11) · Final Report & Evidence Package (W14).
  - **Sẵn sàng lắng nghe câu hỏi từ hội đồng!**
