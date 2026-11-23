# Sentiment-Driven Ticket Triage System

> **Mã dự án:** `TICKET-TRIAGE-01` 
> **Kiến trúc:** Two-Subsystem Architecture (ABSA Zero-shot NLI + Priority Triage & Queue)  
> **Ngôn ngữ xử lý:** Tiếng Anh chuyên biệt (English-only)

---

## 🚀 Hướng dẫn khởi chạy dự án chi tiết

Bạn có thể chạy dự án theo **2 cách**: Sử dụng **Docker Compose** hoặc chạy **Trực tiếp trên máy (Local)**.

---

### CÁCH 1: Chạy bằng Docker Compose 

> 💡 **Yêu cầu:** Đã cài đặt và mở ứng dụng **Docker Desktop**.

#### 1. Khởi động hệ thống
Mở terminal tại thư mục gốc dự án:
```bash
make up
```
*(Nếu không dùng lệnh `make`, bạn chạy lệnh tương đương: `docker compose -f docker.yaml up --build`)*

Docker sẽ tự động:
- Build container `backend` (Python 3.11, FastAPI, SQLite).
- Build container `frontend` (Node 20, Vite, React, pnpm).
- Tự động map cổng và hot-reload khi bạn sửa code.

#### 2. Nạp dữ liệu mẫu (Seed Data)
Mở một terminal mới và chạy:
```bash
make seed
```
*(Hoặc lệnh tương đương: `docker compose -f docker.yaml exec backend python scripts/seed_demo_data.py`)*

Lệnh này sẽ nạp 15 ticket mẫu đa dạng (khiếu nại trừ tiền trùng, hàng hỏng, trễ hẹn, hỏi đáp và cả ticket ngoại ngữ) vào SQLite.

#### 3. Tắt hệ thống
```bash
make down
```
*(Hoặc: `docker compose -f docker.yaml down`)*

#### 4. Cấu hình biến môi trường AI (`.env` / `docker.yaml`)
- `MODEL_NAME`: `mock` (mặc định, nhẹ), `baseline` (DistilBART MNLI) hoặc `deberta` (DeBERTa-v3 Zero-shot).
- `MODEL_ID`: HuggingFace model ID ghi đè tùy chọn (nếu không dùng `MODEL_PATH` cục bộ).
- `MODEL_TASK`: `aspect` (mặc định, suy luận từng khía cạnh) hoặc `document`.
- `ENABLE_ABTE`: `false` (mặc định) hoặc `true` để trích xuất từ khóa `terms` cho từng khía cạnh.
- `HF_HUB_OFFLINE`: `1` (chạy offline từ `./ticket-triage-be/models`; nếu chưa có weights cục bộ khi dùng `MODEL_NAME=mock` hệ thống vẫn chạy bình thường, hoặc gán `model_loaded=false` an toàn mà không làm sập API) hoặc `0` (cho phép tải model từ HuggingFace Hub).

---

### CÁCH 2: Chạy trực tiếp trên máy cục bộ (Local không cần Docker)

> 💡 Dành cho trường hợp máy không bật Docker Desktop hoặc muốn debug trực tiếp.

#### Bước 1: Khởi động Backend (FastAPI + SQLite)
Mở **Terminal 1** tại thư mục gốc:

1. Di chuyển vào thư mục backend:
   ```bash
   cd ticket-triage-be
   ```

2. Tạo và kích hoạt môi trường ảo Python (khuyên dùng Python 3.11):
   ```bash
   python -m venv .venv
   # Trên Windows PowerShell:
   .venv\Scripts\Activate.ps1
   # (Nếu bị chặn execution policy: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass)
   ```

3. Cài đặt dependencies:
   ```bash
   pip install -r requirements-dev.txt
   pip install -e . --no-deps
   ```

4. Nạp dữ liệu mẫu (tùy chọn):
   ```bash
   python scripts/seed_demo_data.py
   ```

5. Khởi động Backend API server:
   ```bash
   uvicorn ticket_triage.api.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   Backend sẽ lắng nghe tại: `http://localhost:8000`.

---

#### Bước 2: Khởi động Frontend (React + Vite + pnpm)
Mở **Terminal 2** tại thư mục gốc:

1. Di chuyển vào thư mục frontend:
   ```bash
   cd ticket-triage-fe
   ```

2. Cài đặt các gói phụ thuộc bằng `pnpm`:
   ```bash
   pnpm install
   ```

3. Khởi động máy chủ giao diện Vite:
   ```bash
   pnpm run dev
   ```
   Giao diện sẽ chạy tại: `http://localhost:5173`.

---

## 📋 Các tính năng chính trên Giao diện (Dashboard)

1. **Hộp thư phân loại ưu tiên (`/` - Inbox):**
   - Danh sách ticket tự động sắp xếp theo điểm ưu tiên `priority_score` giảm dần từ cao xuống thấp, hỗ trợ phân trang (`offset`/`limit`, 50 yêu cầu/trang) và bộ lọc theo trạng thái / khía cạnh / cảm xúc kèm thống kê khía cạnh toàn hệ thống từ `/api/v1/stats/overview`.
   - Thẻ màu nhận diện trực quan ưu tiên sử dụng trường `priority_level` từ API (fallback ngưỡng 70 / 30):
     - <span style="color:red">**CRITICAL / Nghiêm trọng (≥ 70 điểm)**</span>: Viền đỏ, xử lý khẩn cấp.
     - <span style="color:orange">**MEDIUM / Trung bình (30 - 69 điểm)**</span>: Viền vàng.
     - <span style="color:green">**LOW / Thấp (< 30 điểm)**</span>: Viền xanh.
   - Chip khía cạnh cảm xúc hiển thị nhãn tiếng Việt từ `/api/v1/meta/aspects` (tiêu cực xếp trước).
   - Click vào bất kỳ dòng nào để xem **Bảng giải trình chi tiết từng thành phần điểm (`reasons`)** trong modal overlay toàn màn hình.
   - Cập nhật trực tiếp trạng thái kèm kiểm tra FSM (`StatusSelect` vô hiệu hóa các bước chuyển không hợp lệ như `new` → `resolved`; chỉ mở `new` → `assigned`/`in_progress`, `assigned` ↔ `in_progress`, `in_progress` → `resolved`, `resolved` → `new`).
2. **Khung mô phỏng thời gian thực (`/tester` - Live Tester):**
   - Thử nghiệm các nút kịch bản mẫu ("Bị trừ tiền 2 lần", "Hàng hỏng + trễ", "Hỏi đáp", "Ngoại ngữ tiếng Việt").
   - Nhập nội dung bất kỳ và nhấn **Phân tích & Triage ngay** để theo dõi kết quả ABSA và công thức điểm ưu tiên; thanh điều hướng và trang Tester đồng thời hiển thị trạng thái model thực tế từ `/api/v1/health` (`model_name`, `Mock` / `AI thật`, cảnh báo khi `model_loaded=false` và kích thước hàng đợi).
3. **Phân tích thống kê (`/analytics`):**
   - 4 thẻ KPI tổng quan: Tổng số ticket, Ưu tiên Nghiêm trọng, Ưu tiên Trung bình, Ưu tiên Thấp.
   - Biểu đồ phân bố tỷ lệ cảm xúc (Tiêu cực / Trung tính / Tích cực) và phân cấp ưu tiên (giữ nguyên bảng màu cố định theo từng hạng mục).
   - Bảng tổng quan & thanh phân đoạn **Ma trận Khía cạnh × Cảm xúc** từ `/api/v1/stats/aspects` cùng biểu đồ tần suất các khía cạnh (`name_vi`).

---

## 🛠️ Các lệnh tiện ích (Cheat Sheet)

| Lệnh | Ý nghĩa |
| :--- | :--- |
| `make up` | Chạy dev server qua Docker |
| `make seed` | Nạp dữ liệu mẫu vào CSDL SQLite |
| `make test` | Chạy kiểm thử tự động (pytest + vitest) |
| `make lint` | Kiểm tra cú pháp và định dạng mã nguồn (ruff + eslint) |
| `make gen-api` | Tự động đồng bộ hợp đồng OpenAPI (`contracts/openapi.json`) sang TypeScript schema (`ticket-triage-fe/src/api/schema.d.ts`) |
| `make reset-db` | Xóa và tạo mới lại cơ sở dữ liệu SQLite sạch |
| `make demo` | Khởi chạy bản đóng gói phục vụ thuyết trình bảo vệ đồ án |

---

## 📁 Cấu trúc thư mục dự án

```text
.
├── ticket-triage-be/         # Backend: Python, FastAPI, SQLAlchemy 2.0, SQLite
│   ├── src/ticket_triage/
│   │   ├── core/            # Logic nghiệp vụ thuần (ABSA, Priority Engine, heapq, State Machine)
│   │   ├── db/              # ORM models, session SQLite, Repository DAL CRUD
│   │   └── api/             # FastAPI routers, schemas, services
│   ├── configs/             # YAML bắt buộc: aspects, hypotheses, priority rules
│   ├── tests/               # Test suite đầy đủ (pytest)
│   └── scripts/             # Script seed dữ liệu mẫu
├── ticket-triage-fe/         # Frontend: React, Vite, TypeScript, pnpm, TailwindCSS
│   ├── src/
│   │   ├── api/             # Fetch client, TanStack Query hooks & schema.d.ts
│   │   ├── components/      # PriorityBadge, AspectChips, TicketTable, StatusSelect, PriorityBreakdown
│   │   ├── lib/             # format, ticketHelpers (FSM, evidence highlight, matrix), unit tests
│   │   └── pages/           # InboxPage, TesterPage, AnalyticsPage (+ Vitest static SSR specs)
├── contracts/               # Hợp đồng openapi.json giao tiếp giữa BE và FE
├── docs/                    # Hồ sơ dự án: Charter, WBS, System Architecture Report
├── docker.yaml              # Docker Compose dev environment
├── Makefile                 # Lệnh điều khiển tự động
└── README.md                # Tài liệu hướng dẫn sử dụng
```
