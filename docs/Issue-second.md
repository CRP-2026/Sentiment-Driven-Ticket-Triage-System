# 📌 Báo Cáo & Danh Sách Vấn Đề Cần Xử Lý — Đợt 2 (Issues Tracker v2)

> **Dự án:** Hệ thống phân loại & định tuyến phản hồi khách hàng theo cảm xúc (*Sentiment-Driven Ticket Triage System*)  
> **Mã dự án:** `TICKET-TRIAGE-01` | **Ngày rà soát:** 2026-11-12  
> **Tiếp nối từ:** [Issue.md](./Issue.md) (Đợt 1 đã xử lý 8 lỗi baseline `#1`–`#8`)  
> **Trạng thái kiểm tra hiện tại (16/11/2026):** `ruff check ticket-triage-be` PASSED, **63/63** backend tests PASSED, `contracts/openapi.json` == `app.openapi()`, `pnpm run check` & `vitest` (**23/23** trên 5 file test) & `pnpm run build` PASSED; toàn bộ các vấn đề **`#9`–`#14`** (Backend, Contract `openapi.json`/`generated.ts`, Frontend và Tài liệu) đã xử lý xong (lưu ý: suy luận AI thật cần `requirements-ml.txt` + checkpoint trong `models/`, còn test component/page FE sử dụng static SSR markup `renderToStaticMarkup` để không thêm dependency ngoài quy tắc `AGENT.md`).

---

## 🔍 I. Phân Tích Chi Tiết 6 Vấn Đề Kỹ Thuật & Điểm Lệch Còn Tồn Tại

### 9. ~~`priority_rules.yaml` chưa được nạp vào `priority_engine.py`~~ ✅ ĐÃ XỬ LÝ
* **Trạng thái hiện tại:** Đã xử lý hoàn tất ở nhánh Priority BE: bổ sung `load_priority_rules()` + `load_aspect_weights()` (`@lru_cache`), nạp `priority_rules.yaml` theo `settings.configs_dir` trong `main.py` → `tickets.py` → `pipeline.py` → `calculate_priority()`, đồng bộ `"charged twice"` (`critical`), `"damaged"`, `"overcharged"` (`high`), bổ sung `urgency_points` (`30/20/15/10`), bỏ hardcode `DEFAULT_ASPECT_WEIGHTS`, sửa đa phủ định, `REMEDY_ACTION_KEYWORDS`, `_is_resolved_clause`, `CONTRAST_CLAUSE_RE` và `???` trong `intensity_extractor.py`.
* **Mức độ (trước khi sửa):** Nghiêm trọng (Lệch kiến trúc Single Source of Truth)
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

### 11. ~~`contracts/openapi.json` lệch với API thực tế & Frontend chưa dùng type sinh tự động~~ ✅ ĐÃ XỬ LÝ
* **Trạng thái hiện tại:** Đã đồng bộ [contracts/openapi.json](../contracts/openapi.json) trực tiếp từ `app.openapi()`, chạy `pnpm run gen-api` sinh [generated.ts](../ticket-triage-fe/src/api/generated.ts) và cấu trúc lại [schema.d.ts](../ticket-triage-fe/src/api/schema.d.ts) để re-export toàn bộ schema chuẩn từ `generated.ts` (gồm `is_mock`, `model_loaded` trên `HealthResponse`, `PriorityBreakdownOut`, `AspectStatsItem`). [TesterPage.tsx](../ticket-triage-fe/src/pages/TesterPage.tsx) và [Navigation.tsx](../ticket-triage-fe/src/components/layout/Navigation.tsx) đã kết nối `useHealth()` hiển thị trạng thái model và hàng đợi thực tế.

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
* **Tác động (Cập nhật trạng thái):** 🟡 **Đã xử lý phần an toàn luồng & ORM** (`RLock`, dedup `ticket_id`, chuẩn hóa UTC trong `TicketPriorityQueue`, và lưu `ticket_queue_metadata(ticket)` dict thay vì ORM `Ticket`). Phần còn lại chỉ là cân nhắc kiến trúc có giữ heap song song với truy vấn SQLite hay không.

---

### 14. ~~Frontend lãng phí API `/stats/aspects`, chưa chặn chuyển trạng thái sai ở UI và thiếu test component~~ ✅ ĐÃ XỬ LÝ
* **Trạng thái hiện tại:** Đã hoàn tất 3 đợt nâng cấp Frontend:
  * [AnalyticsPage.tsx](../ticket-triage-fe/src/pages/AnalyticsPage.tsx): bổ sung Stacked Bar Chart **Ma trận Khía cạnh × Cảm xúc** từ `useAspectsStats()` + `buildAspectSentimentMatrix()`, thêm 4 thẻ KPI tổng quan, sửa lỗi lệch màu `PieChart` (gắn `color` trước `.filter((d) => d.value > 0)`) và map nhãn khía cạnh sang `name_vi`.
  * [StatusSelect.tsx](../ticket-triage-fe/src/components/tickets/StatusSelect.tsx): khóa (`disabled`) `<option>` cấm qua `ALLOWED_STATUS_TRANSITIONS` / `canTransitionStatus()` khớp `StateManager` BE, đồng thời chặn gọi mutation sai và ổn định layout nút lọc trên [InboxPage.tsx](../ticket-triage-fe/src/pages/InboxPage.tsx).
  * [ticketHelpers.ts](../ticket-triage-fe/src/lib/ticketHelpers.ts): gom `resolvePriorityLevel()` (ưu tiên `priority_level` từ API), đồng bộ `"charged twice"` sang `critical` khớp `priority_rules.yaml`, chuẩn hóa highlight evidence và mapping tên khía cạnh; [MOCK_TICKETS](../ticket-triage-fe/src/mocks/tickets.ts) `#103` đã chỉnh `confidence: 0.80` khớp `base = 48.0`.
  * Vitest suite mở rộng từ 3 tests lên **23/23 tests PASSED (5 file)**: [format.test.ts](../ticket-triage-fe/src/lib/format.test.ts) (3), [ticketHelpers.test.ts](../ticket-triage-fe/src/lib/ticketHelpers.test.ts) (8), [apiAndMocks.test.ts](../ticket-triage-fe/src/api/apiAndMocks.test.ts) (3), [ticketComponents.test.tsx](../ticket-triage-fe/src/components/tickets/ticketComponents.test.tsx) (5) và [pages.test.tsx](../ticket-triage-fe/src/pages/pages.test.tsx) (4) qua `renderToStaticMarkup` + `StaticRouter` (không thêm dependency ngoài `AGENT.md`).

---

## ⚖️ II. Bảng Tổng Hợp Đối Chiếu Code vs Tài Liệu / Hợp Đồng

| ID | Thành phần | Hiện trạng sau xử lý | Kỳ vọng theo Tài liệu / Hợp đồng | Trạng thái |
|:---:|:---|:---|:---|:---|
| **#9** | `priority_engine.py` & `priority_rules.yaml` | ✅ **Đã xử lý:** Nạp động `load_priority_rules()` & `load_aspect_weights()`, đồng bộ từ khóa/caps/ngưỡng + `_is_resolved_clause`. | Nạp động qua `load_priority_rules()` (`lru_cache`), thống nhất 1 nguồn sự thật YAML. | ✅ Đã xử lý |
| **#10** | `main.py`, `baseline.py`, `abte.py`, `docker.yaml` | ✅ **Đã xử lý (Code):** Hỗ trợ `baseline \| deberta`, `MODEL_ID`, `MODEL_TASK`, `ENABLE_ABTE`, trích xuất `terms` từ `aspects.yaml`, cập nhật `docker.yaml` & `/health` `model_loaded`. (Suy luận thật cần `requirements-ml.txt` + checkpoint trong `models/`). | Hỗ trợ `mock \| baseline \| deberta`, fallback `MODEL_TASK=document`, tùy chọn `ENABLE_ABTE`. | ✅ Đã xử lý (chờ env ML) |
| **#11** | `contracts/openapi.json` & `schema.d.ts` | ✅ **Đã xử lý:** Sync `contracts/openapi.json` == `app.openapi()`; sinh `generated.ts` (`pnpm run gen-api`) và re-export tại `schema.d.ts`. | `contracts/openapi.json` khớp 100% `app.openapi()`; FE dùng type từ `generated.ts`. | ✅ Đã xử lý |
| **#12** | `baseline.py`, `config_utils.py` | ✅ **Đã xử lý:** Guard `target_path is not None`, đọc `overall_sentiment_template` từ YAML, trích xuất helper dùng chung `config_utils.find_config_file()`. | Trả về `{}` an toàn khi thiếu file và ưu tiên `settings.configs_dir`. | ✅ Đã xử lý |
| **#13** | `priority_queue.py` & `tickets.py` | ✅ **Đã xử lý phần an toàn luồng & ORM:** Thêm `RLock`, dedup `ticket_id`, chuẩn hóa UTC và lưu `ticket_queue_metadata`; SQLite phục vụ phân trang/lọc. | An toàn luồng, chỉ lưu dữ liệu thuần hoặc chuyển hẳn sang DB-backed queue. | ✅ Đã xử lý |
| **#14** | `AnalyticsPage.tsx`, `StatusSelect.tsx`, Vitest | ✅ **Đã xử lý:** Vẽ Stacked Bar Chart từ `/stats/aspects`, khóa option FSM trên `StatusSelect.tsx`, gom `ticketHelpers.ts` + bổ sung Vitest (**23/23** static SSR & unit tests). | Hiển thị ma trận Aspect × Sentiment, khóa bước chuyển sai, bổ sung component tests. | ✅ Đã xử lý |

---

## 💡 III. Tóm Tắt Thực Thi Theo Từng Nhóm (`#9`–`#14`)

1. **Backend Core & AI (`#9`, `#10`, `#12` — ✅ Đã xử lý):**
   * Hoàn thiện `load_priority_rules()`, `load_aspect_weights()`, `load_aspect_keywords()` (nạp bắt buộc fail-fast từ `aspects.yaml`, bỏ bộ từ khóa fallback cứng trong `keyword_prefilter.py`), `config_utils.find_config_file()`, `extract_aspect_terms()` (`ENABLE_ABTE`), guard `target_path is not None` & `overall_sentiment_template` trong `baseline.py`, nhánh `baseline | deberta` + `MODEL_ID` + `MODEL_TASK` trong `main.py`, sửa `model_loaded` trong `health.py`, và bổ sung env AI trong `docker.yaml`.
2. **Backend API, Queue & Hợp đồng (`#11`, `#13` — ✅ Đã xử lý):**
   * Xuất lại `contracts/openapi.json` (`== app.openapi()`), sinh `ticket-triage-fe/src/api/generated.ts` qua `pnpm run gen-api`, cấu trúc `schema.d.ts` re-export, và dùng `RLock` + `ticket_queue_metadata` trong Heap.
3. **Frontend & Tài liệu (`#14` — ✅ Đã xử lý):**
   * Hoàn thiện `ticketHelpers.ts` (ưu tiên `priority_level` API, `"charged twice"` critical, FSM transitions), `AnalyticsPage.tsx` (4 KPI + Pie color fix + Stacked Bar Chart), `TesterPage.tsx` & `Navigation.tsx` (`useHealth()`), `InboxPage.tsx` (phân trang 50/trang + `aspect_counts` server + bộ lọc cố định), `MOCK_TICKETS` `#103`, đồng bộ `Backend-Plan.md`, `Frontend-Plan.md`, `System-Ticket-Report.md`, `README.md` và các tài liệu audit.
   * **Nghiệm thu cuối:** `pytest -v` (**63/63**), `ruff check ticket-triage-be` (PASSED), `contracts/openapi.json` == `app.openapi()`, `pnpm run check` (PASSED), `pnpm run test` (**23/23** trên 5 file qua `renderToStaticMarkup` + `StaticRouter`), `pnpm run build` (PASSED). Lưu ý chạy model ML thật vẫn yêu cầu cài `requirements-ml.txt` (`torch`/`transformers`/`peft`) + checkpoint thật, và FE chưa chạy test tương tác `jsdom` / browser E2E live.

