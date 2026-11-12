# 📌 Báo Cáo & Danh Sách Vấn Đề Cần Xử Lý — Đợt 2 (Issues Tracker v2)

> **Dự án:** Hệ thống phân loại & định tuyến phản hồi khách hàng theo cảm xúc (*Sentiment-Driven Ticket Triage System*)  
> **Mã dự án:** `TICKET-TRIAGE-01` | **Ngày rà soát:** 2026-11-12  
> **Tiếp nối từ:** [Issue.md](./Issue.md) (Đợt 1 đã xử lý 8 lỗi baseline `#1`–`#8`)  
> **Trạng thái kiểm tra hiện tại:** `ruff check` PASSED, `18/18` unit/e2e backend tests PASSED, `19/19` non-TestClient regression tests PASSED, `pnpm run check` & `vitest` (`3/3`) PASSED; còn tồn tại **6 vấn đề kỹ thuật & điểm lệch đồng bộ (`#9`–`#14`)**.

---

## 🔍 I. Phân Tích Chi Tiết 6 Vấn Đề Kỹ Thuật & Điểm Lệch Còn Tồn Tại

### 9. `priority_rules.yaml` chưa được nạp vào `priority_engine.py` (cấu hình hardcode & lệch tài liệu)
* **Mức độ:** Nghiêm trọng (Lệch kiến trúc Single Source of Truth)
* **Hiện tượng:**
  * Dù [Issue.md](./Issue.md#L94) (Mục II & VI) ghi nhận đã kết nối `load_priority_rules()` từ `configs/priority_rules.yaml`, trên thực tế việc chỉnh sửa [priority_rules.yaml](../ticket-triage-be/configs/priority_rules.yaml) hoàn toàn **không có tác dụng** khi chạy hệ thống.
  * Danh sách từ khóa, điểm cộng và ngưỡng ưu tiên giữa YAML, code và tài liệu đang mâu thuẫn nhau.
* **Root Cause:**
  * Trong [priority_engine.py](../ticket-triage-be/src/ticket_triage/core/priority/priority_engine.py#L15-L27), chưa có hàm `load_priority_rules()`; toàn bộ `CRITICAL_KEYWORDS`, `HIGH_KEYWORDS`, `urgency_cap = 30.0`, `aspect_cap = 20.0`, `intensity_bonus = 5.0` và ngưỡng phân cấp `70.0 / 30.0` (dòng 174–179) vẫn bị hardcode.
  * Sai lệch cụ thể giữa YAML và code:
    * `"charged twice"` nằm trong nhóm `high` ở `priority_rules.yaml` (dòng 20), nhưng nằm trong `CRITICAL_KEYWORDS` ở `priority_engine.py` (dòng 17).
    * `"damaged"` và `"overcharged"` có trong `HIGH_KEYWORDS` ở `priority_engine.py` (dòng 21), nhưng không tồn tại trong `priority_rules.yaml`.
    * Điểm cộng từ khóa `CRITICAL` ở dòng 100 của `priority_engine.py` đang là `30.0 if is_last else 20.0`, trong khi [Issue.md](./Issue.md#L96) ghi `+20 / +15` còn [System-Ticket-Report.md](./System-Ticket-Report.md#L196-L197) ghi `+20 / +10`.
* **Tác động:** Nhóm vận hành/BA không thể điều chỉnh luật ưu tiên qua YAML như cam kết thiết kế; hành vi tính điểm thực tế không khớp với tài liệu báo cáo.

---

### 10. Cấu hình `MODEL_NAME=deberta`, `MODEL_TASK`, `ENABLE_ABTE` và nạp checkpoint chưa hoạt động
* **Mức độ:** Nghiêm trọng (Ảnh hưởng trực tiếp suy luận AI thật)
* **Hiện tượng:**
  * Đặt biến môi trường `MODEL_NAME=deberta`, `MODEL_TASK=document` hoặc `ENABLE_ABTE=true` không kích hoạt đúng mô hình hoặc luồng xử lý tương ứng.
  * Khi bật `MODEL_NAME=baseline` với cấu hình mặc định, hệ thống vẫn rơi về `MockSentimentModel`.
* **Root Cause:**
  * Trong [main.py](../ticket-triage-be/src/ticket_triage/api/main.py#L44-L47):
    ```python
    if model_name == "baseline":
        app.state.sentiment_model = ZeroShotNliModel(model_name_or_path=settings.model_path or "valhalla/distilbart-mnli-12-3")
    else:
        app.state.sentiment_model = MockSentimentModel()
    ```
    Chỉ kiểm tra `"baseline"`, khiến giá trị `"deberta"` (khai báo trong [settings.py](../ticket-triage-be/src/ticket_triage/settings.py#L12) và [docker.yaml](../docker.yaml#L9)) rơi vào nhánh `else` dùng `MockSentimentModel`.
  * `settings.model_path` luôn có giá trị mặc định là chuỗi đường dẫn thư mục `ticket-triage-be/models` (hiện chỉ có `.gitkeep`), nên biểu thức `settings.model_path or "valhalla/distilbart-mnli-12-3"` luôn truyền thư mục rỗng vào `ZeroShotNliModel` và gây lỗi load ở runtime.
  * `settings.model_task` và `settings.enable_abte` không được tham chiếu trong [pipeline.py](../ticket-triage-be/src/ticket_triage/api/services/pipeline.py) hay `baseline.py`; [abte.py](../ticket-triage-be/src/ticket_triage/core/sentiment/abte.py) mới chỉ là stub `return ()`.
* **Tác động:** Không thể chuyển đổi sang mô hình `deberta` hoặc chế độ dự phòng `MODEL_TASK=document` bằng biến môi trường; dễ gây nhầm lẫn khi demo model thật.

---

### 11. `contracts/openapi.json` lệch với API thực tế & Frontend chưa dùng type sinh tự động
* **Mức độ:** Nghiêm trọng (Lệch hợp đồng giao tiếp BE–FE)
* **Hiện tượng:**
  * Kiểm tra đối chiếu `app.openapi()` với [contracts/openapi.json](../contracts/openapi.json) trả về không khớp (`Equal: False`).
  * Chạy `make gen-api` sinh ra `src/api/generated.ts`, nhưng toàn bộ Frontend vẫn phụ thuộc vào file viết tay `src/api/schema.d.ts` vốn đã lạc hậu.
* **Root Cause:**
  * [tickets.py](../ticket-triage-be/src/ticket_triage/api/routers/tickets.py#L12-L13) khai báo thêm route `POST /api/v1/tickets/triage`, nhưng route này **chưa có** trong `contracts/openapi.json`.
  * [package.json](../ticket-triage-fe/package.json#L12) cấu hình `"gen-api": "pnpm dlx openapi-typescript ../contracts/openapi.json -o src/api/generated.ts"`, nhưng file `src/api/generated.ts` chưa tồn tại và [hooks.ts](../ticket-triage-fe/src/api/hooks.ts#L4-L11) vẫn import từ [schema.d.ts](../ticket-triage-fe/src/api/schema.d.ts).
  * `HealthResponse` trong `schema.d.ts` (dòng 61–66) đang thiếu 2 trường `is_mock: boolean` và `model_loaded: boolean` so với `HealthResponse` ở [schemas.py](../ticket-triage-be/src/ticket_triage/api/schemas.py#L107-L115).
* **Tác động:** Vi phạm quy tắc contract-first tại [AGENT.md](../AGENT.md#L24-L25); nếu backend đổi schema, TypeScript compiler trên Frontend sẽ không phát hiện được sai lệch.

---

### 12. Lỗi `AttributeError` tiềm ẩn trong `load_aspect_hypotheses()` khi thiếu file config
* **Mức độ:** Trung bình (Lỗi runtime khi cấu hình/đóng gói thiếu file)
* **Hiện tượng:** Gọi `load_aspect_hypotheses()` khi không tìm thấy `configs/aspect_hypotheses.yaml` sẽ ném exception thay vì trả về `{}` an toàn.
* **Root Cause:**
  * Trong [baseline.py](../ticket-triage-be/src/ticket_triage/core/sentiment/baseline.py#L37-L46):
    ```python
    if yaml_path is not None:
        target_path = Path(yaml_path)
    else:
        target_path = _find_config_file("aspect_hypotheses.yaml")

    if target_path.is_file():
        return _read_hypotheses_yaml(str(target_path.resolve()))
    return {}
    ```
    Khi `_find_config_file()` trả về `None`, `target_path.is_file()` sẽ gây `AttributeError: 'NoneType' object has no attribute 'is_file'`.
  * Ngoài ra `ZeroShotNliModel.__init__` gọi `load_aspect_hypotheses()` không dùng `settings.configs_dir`, khác với cách nạp `aspects.yaml` ở `main.py`.
* **Tác động:** Ứng dụng có thể crash ở bước khởi tạo model nếu chạy từ thư mục làm việc hoặc gói cài đặt không tìm thấy thư mục `configs/`.

---

### 13. `TicketPriorityQueue` thiếu thread-safety, lưu ORM object dễ detached và ít giá trị sử dụng
* **Mức độ:** Trung bình (Rủi ro concurrency & kiến trúc dư thừa)
* **Hiện tượng:**
  * Hàng đợi in-memory `heapq` được cập nhật khi `POST /tickets` và `PATCH /tickets/{id}/status`, nhưng không có API nào đọc/lấy ticket từ hàng đợi này.
  * Khi cập nhật đồng thời từ nhiều request hoặc push lại ticket, heap không an toàn luồng và có thể giữ bản ghi trùng.
* **Root Cause:**
  * `GET /api/v1/tickets` và `GET /api/v1/tickets/queue` trong [tickets.py](../ticket-triage-be/src/ticket_triage/api/routers/tickets.py#L35-L59) truy vấn trực tiếp SQLite (`ORDER BY priority_score DESC, created_at ASC`); [priority_queue.py](../ticket-triage-be/src/ticket_triage/core/queue/priority_queue.py) hiện chỉ được dùng để lấy `.size()` cho `/api/v1/health`.
  * `TicketPriorityQueue` chưa có `threading.Lock` (trong khi các sync endpoint của FastAPI chạy đồng thời trên AnyIO threadpool); `push()` không loại bỏ entry cũ nếu `ticket_id` đã tồn tại trong `_item_map`; `remove()` rebuild toàn bộ heap ($O(N)$); và [pipeline.py](../ticket-triage-be/src/ticket_triage/api/services/pipeline.py#L61) / [main.py](../ticket-triage-be/src/ticket_triage/api/main.py#L63) truyền trực tiếp ORM `Ticket` vào `data` dù DB `Session` sẽ đóng sau request.
* **Tác động:** Có nguy cơ race condition hoặc `DetachedInstanceError` nếu mở rộng tính năng pop/peek từ `priority_queue`; đồng thời phát sinh chi phí duy trì cấu trúc RAM song song với DB mà chưa phục vụ truy vấn thực tế.

---

### 14. Frontend lãng phí API `/stats/aspects`, chưa chặn chuyển trạng thái sai ở UI và thiếu test component
* **Mức độ:** Trung bình (Trải nghiệm người dùng & độ phủ kiểm thử)
* **Hiện tượng:**
  * Trang Analytics gọi API `/api/v1/stats/aspects` nhưng không hiển thị dữ liệu ma trận khía cạnh × cảm xúc.
  * Dropdown trạng thái trên bảng Inbox cho phép chọn bước chuyển bị backend cấm (ví dụ `new` → `resolved`), gây lỗi HTTP 400 rồi mới báo đỏ trên UI.
  * Độ phủ test Frontend còn rất mỏng.
* **Root Cause:**
  * [AnalyticsPage.tsx](../ticket-triage-fe/src/pages/AnalyticsPage.tsx#L22) gọi `useAspectsStats()` nhưng chỉ lấy `isLoading: isAspectsLoading`, còn biểu đồ cột (dòng 48–53) vẫn dùng `stats.aspect_counts` từ `/stats/overview`.
  * [StatusSelect.tsx](../ticket-triage-fe/src/components/tickets/StatusSelect.tsx#L40-L44) render toàn bộ `STATUSES` mà không lọc theo luật chuyển trạng thái của `StateManager`.
  * [TicketTable.tsx](../ticket-triage-fe/src/components/tickets/TicketTable.tsx#L10-L11) và [PriorityBreakdown.tsx](../ticket-triage-fe/src/components/tickets/PriorityBreakdown.tsx#L19-L20) đang hardcode danh sách từ khóa highlight (`criticalPhrases`, `highPhrases`) ở FE thay vì đồng bộ từ backend.
  * Thư mục `ticket-triage-fe` hiện mới có 1 file test ([format.test.ts](../ticket-triage-fe/src/lib/format.test.ts), 3 tests), chưa có test cho `InboxPage`, `TesterPage`, `TicketTable`, `StatusSelect`, `PriorityBreakdown` hay hooks.
* **Tác động:** Bỏ phí endpoint `/stats/aspects` đã xây ở backend; UX xử lý ticket dễ phát sinh thao tác lỗi 400; rủi ro regression UI khi sửa component.

---

## ⚖️ II. Bảng Tổng Hợp Đối Chiếu Code vs Tài Liệu / Hợp Đồng

| ID | Thành phần | Hiện trạng trong Code | Kỳ vọng theo Tài liệu / Hợp đồng | Rủi ro |
|:---:|:---|:---|:---|:---|
| **#9** | `priority_engine.py` & `priority_rules.yaml` | Hardcode từ khóa, điểm cộng (`+30/+20`), caps và ngưỡng; lệch `"charged twice"`, `"damaged"`, `"overcharged"`. | Nạp động qua `load_priority_rules()` (`lru_cache`), thống nhất 1 nguồn sự thật YAML. | Cao |
| **#10** | `main.py`, `baseline.py`, `abte.py` | Chỉ nhận `baseline` vs `mock`; `model_path` trỏ thư mục rỗng; `MODEL_TASK` & `ENABLE_ABTE` chưa nối. | Hỗ trợ `mock \| baseline \| deberta`, fallback `MODEL_TASK=document`, tùy chọn `ENABLE_ABTE`. | Cao |
| **#11** | `contracts/openapi.json` & `schema.d.ts` | Thiếu `/api/v1/tickets/triage` trong `openapi.json`; FE dùng `schema.d.ts` viết tay thiếu `is_mock`, `model_loaded`. | `contracts/openapi.json` khớp 100% `app.openapi()`; FE dùng type từ `generated.ts`. | Cao |
| **#12** | `baseline.py` (`load_aspect_hypotheses`) | `target_path.is_file()` lỗi nếu `target_path` là `None`. | Trả về `{}` an toàn khi thiếu file và ưu tiên `settings.configs_dir`. | Trung bình |
| **#13** | `priority_queue.py` & `tickets.py` | Heap không lock, không dedup, lưu ORM `Ticket`, API đọc thẳng SQLite. | An toàn luồng, chỉ lưu dữ liệu thuần hoặc chuyển hẳn sang DB-backed queue. | Trung bình |
| **#14** | `AnalyticsPage.tsx`, `StatusSelect.tsx`, Vitest | Bỏ qua data `/stats/aspects`, cho chọn chuyển trạng thái sai trên UI, chỉ có 3 unit test. | Hiển thị ma trận Aspect × Sentiment, khóa bước chuyển sai, bổ sung component tests. | Trung bình |

---

## 💡 III. Đề Xuất Hành Động Theo Từng Nhóm

### 1. Backend Core & AI (`#9`, `#10`, `#12`)
* **#9:** Viết hàm `load_priority_rules()` (dùng `@lru_cache`) đọc `configs/priority_rules.yaml` (nếu thiếu thì fallback về default an toàn). Đồng bộ lại phân nhóm `"charged twice"`, `"damaged"`, `"overcharged"` và điểm cộng `critical` / `high` giữa YAML, `priority_engine.py` và `System-Ticket-Report.md` / `Issue.md`.
* **#10:** Cập nhật `main.py` hỗ trợ `MODEL_NAME in ("baseline", "deberta")` (chỉ dùng `settings.model_path` khi thư mục có file config model hợp lệ, ngược lại dùng HuggingFace repo ID mặc định tương ứng). Nối `settings.model_task == "document"` và `settings.enable_abte` vào `pipeline.py`.
* **#12:** Sửa điều kiện thành `if target_path is not None and target_path.is_file():` trong `load_aspect_hypotheses()`, đồng thời truyền đường dẫn từ `settings.configs_dir` khi khởi tạo `ZeroShotNliModel` trong `main.py`.

### 2. Backend API, Queue & Hợp đồng (`#11`, `#13`)
* **#11:** Xuất lại `contracts/openapi.json` từ `app.openapi()` để bao gồm `/api/v1/tickets/triage`, chạy `pnpm run gen-api` sinh `src/api/generated.ts` và tái xuất các type trong `src/api/schema.d.ts` từ `components["schemas"]`.
* **#13:** Thêm `threading.Lock` vào `TicketPriorityQueue`, chỉ lưu primitive metadata (hoặc bỏ ORM object `Ticket` khỏi heap), xử lý cập nhật/dedup theo `ticket_id` (hoặc quyết định dùng hẳn truy vấn SQLite làm hàng đợi chính thức để bỏ phần dư thừa ở RAM).

### 3. Frontend & QA (`#14`)
* **#14:**
  * Dùng dữ liệu từ `useAspectsStats()` trên `AnalyticsPage.tsx` để vẽ biểu đồ stacked bar / bảng ma trận **Khía cạnh × Cảm xúc** (`negative` / `neutral` / `positive`).
  * Áp dụng bản đồ chuyển trạng thái hợp lệ trong `StatusSelect.tsx` để vô hiệu hóa (`disabled`) các trạng thái không được phép chuyển tiếp.
  * Bổ sung unit/regression test cho `load_priority_rules()`, `MODEL_NAME=deberta`, `load_aspect_hypotheses(None)`, và viết thêm component tests bằng `@testing-library/react` cho `PriorityBadge`, `StatusSelect`, `TicketTable`.

---

## 🚀 IV. Kế Hoạch Triển Khai Đề Xuất

### Đợt 1 — Đồng bộ Cấu hình & Hợp đồng (Ưu tiên cao)
1. **Sửa #9:** Triển khai `load_priority_rules()` và thống nhất `priority_rules.yaml` với `priority_engine.py` + tài liệu.
2. **Sửa #12:** Guard `target_path is not None` trong `baseline.py`.
3. **Sửa #11:** Cập nhật `contracts/openapi.json`, chạy `gen-api`, nối `schema.d.ts` với `generated.ts`.

### Đợt 2 — Hoàn thiện Model Loading & Queue
4. **Sửa #10:** Hoàn thiện nhánh `deberta`, fallback `MODEL_TASK=document`, và kiểm tra model dir trong `main.py`.
5. **Sửa #13:** Bổ sung `threading.Lock`, dedup theo `ticket_id` và bỏ lưu ORM object trong `TicketPriorityQueue` (hoặc tinh giản dùng DB-backed queue).

### Đợt 3 — Nâng cấp Frontend & Nghiệm thu Test
6. **Sửa #14:** Hiển thị dữ liệu `useAspectsStats()`, giới hạn transition hợp lệ ở `StatusSelect.tsx`, bổ sung test Frontend và test hồi quy Backend cho các issue `#9`–`#14`.
7. Chạy lại đầy đủ `ruff check .`, `pytest -v` (bao gồm cả nhóm `TestClient` ngoài sandbox), `pnpm run check` và `pnpm run test`.

