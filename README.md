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

## 🌐 Các địa chỉ truy cập quan trọng

Sau khi khởi động thành công (bằng Cách 1 hoặc Cách 2), mở trình duyệt truy cập:

| Thành phần | Địa chỉ truy cập | Mô tả |
| :--- | :--- | :--- |
| **Giao diện Dashboard** | [http://localhost:5173](http://localhost:5173) | Hộp thư ưu tiên (Inbox), Live Tester, Bảng phân tích thống kê |
| **Tài liệu API (Swagger UI)** | [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs) | Giao diện thử nghiệm các RESTful endpoints trực tiếp |
| **Kiểm tra trạng thái (Health)** | [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health) | Trả về `{"status":"ok", "queue_size": N}` |
| **Hợp đồng OpenAPI JSON** | [http://localhost:8000/api/v1/openapi.json](http://localhost:8000/api/v1/openapi.json) | Bản đặc tả chuẩn của API backend |

---

## 📋 Các tính năng chính trên Giao diện (Dashboard)

1. **Hộp thư phân loại ưu tiên (`/` - Inbox):**
   - Danh sách ticket tự động sắp xếp theo điểm ưu tiên `priority_score` giảm dần từ cao xuống thấp.
   - Thẻ màu nhận diện trực quan:
     - <span style="color:red">**CRITICAL / Cao (≥ 70 điểm)**</span>: Viền đỏ, xử lý khẩn cấp.
     - <span style="color:orange">**MEDIUM / Trung bình (30 - 69 điểm)**</span>: Viền vàng.
     - <span style="color:green">**LOW / Thấp (< 30 điểm)**</span>: Viền xanh.
   - Chip khía cạnh cảm xúc (tiêu cực xếp trước).
   - Click vào bất kỳ dòng nào để xem **Bảng giải trình chi tiết từng thành phần điểm (`reasons`)**.
   - Cập nhật trực tiếp trạng thái (`new` → `assigned` → `in_progress` → `resolved`).
2. **Khung mô phỏng thời gian thực (`/tester` - Live Tester):**
   - Thử nghiệm các nút kịch bản mẫu ("Bị trừ tiền 2 lần", "Hàng hỏng + trễ", "Hỏi đáp", "Ngoại ngữ tiếng Việt").
   - Nhập nội dung bất kỳ và nhấn **Phân tích & Triage ngay** để theo dõi kết quả ABSA và công thức điểm ưu tiên trong 1-2 giây.
3. **Phân tích thống kê (`/analytics`):**
   - Biểu đồ phân bố tỷ lệ cảm xúc (Tiêu cực / Trung tính / Tích cực).
   - Biểu đồ phân cấp ưu tiên.
   - Biểu đồ tần suất các khía cạnh phàn nàn nhiều nhất.

---

## 🛠️ Các lệnh tiện ích (Cheat Sheet)

| Lệnh | Ý nghĩa |
| :--- | :--- |
| `make up` | Chạy dev server qua Docker |
| `make seed` | Nạp dữ liệu mẫu vào CSDL SQLite |
| `make test` | Chạy kiểm thử tự động (pytest + vitest) |
| `make lint` | Kiểm tra cú pháp và định dạng mã nguồn (ruff + eslint) |
| `make gen-api` | Tự động đồng bộ hợp đồng OpenAPI sang TypeScript schema |
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
│   ├── configs/             # YAML: aspects, hypotheses, priority rules
│   ├── tests/               # Test suite đầy đủ (pytest)
│   └── scripts/             # Script seed dữ liệu mẫu
├── ticket-triage-fe/         # Frontend: React, Vite, TypeScript, pnpm, TailwindCSS
│   ├── src/
│   │   ├── api/             # Fetch client, TanStack Query hooks, schema types
│   │   ├── components/      # PriorityBadge, AspectChips, TicketTable, StatusSelect
│   │   └── pages/           # InboxPage, TesterPage, AnalyticsPage
├── contracts/               # Hợp đồng openapi.json giao tiếp giữa BE và FE
├── docs/                    # Hồ sơ dự án: Charter, WBS, System Architecture Report
├── docker.yaml              # Docker Compose dev environment
├── Makefile                 # Lệnh điều khiển tự động
└── README.md                # Tài liệu hướng dẫn sử dụng
```
