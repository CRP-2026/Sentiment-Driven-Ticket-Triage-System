# Backend (FastAPI + core, ABSA)

## Lệnh (chạy qua Docker)
- Khởi động: `make up`  Test: `docker compose exec backend pytest`  Lint: `docker compose exec backend ruff check .`
- Xuất hợp đồng: `make gen-api`  Seed demo: `make seed`
- Bật RoBERT: `INSTALL_ML=true MODEL_NAME=robert make up` (checkpoint trong backend/models, trỏ MODEL_PATH)

## Kiến trúc và quy tắc phụ thuộc
`api -> core, db` (một chiều). Trong `src/ticket_triage/`:
- `core/`: logic thuần. TUYỆT ĐỐI không import fastapi, sqlalchemy, pydantic-settings.
  Gồm preprocessing, language, priority, queue (heapq), taxonomy, sentiment/ (ABSA).
- `db/`: SQLAlchemy 2.0, SQLite. Không chứa logic tính điểm.
- `api/`: routes mỏng; ghép pipeline ở `services/pipeline.py`. `schemas.py` là hợp đồng với FE.
- `training/`: script huấn luyện/đánh giá, dùng lại `core.preprocessing` để train và predict giống nhau.
- `settings.py`: mọi giá trị theo môi trường đọc từ `.env`.

## Kiểu dữ liệu và hợp đồng mô hình (ĐÓNG BĂNG, đổi phải qua họp nhóm)
```python
Sentiment = Literal["negative", "neutral", "positive"]

@dataclass(frozen=True)
class SentimentResult:            # cảm xúc tổng thể của ticket
    label: Sentiment
    confidence: float             # [0,1]

@dataclass(frozen=True)
class AspectSentiment:
    aspect: str                   # id lấy từ configs/aspects.yaml
    sentiment: Sentiment          # khía cạnh không được nhắc đến thì KHÔNG đưa vào danh sách
    confidence: float             # [0,1]
    terms: tuple[str, ...] = ()   # chỉ có khi ENABLE_ABTE=true (cụm từ trích xuất)

@dataclass(frozen=True)
class AbsaResult:
    overall: SentimentResult
    aspects: list[AspectSentiment]   # rỗng nếu là mô hình cấp văn bản (dự phòng)
```
- Mọi mô hình cùng interface `predict(text: str) -> AbsaResult`. Chọn bằng `MODEL_NAME=mock|baseline|robert`
  và `MODEL_TASK=absa|document` (document = dự phòng cấp văn bản). Import baseline/robert kiểu lazy
  để máy không cài torch vẫn chạy `mock`.
- Bài toán lõi: với mỗi khía cạnh trong taxonomy, phân loại 4 lớp {not_mentioned, negative, neutral, positive}
  trên cả văn bản; khía cạnh `not_mentioned` bị loại khỏi đầu ra. Không cần trích xuất span ở tầng này.
- `overall` lấy từ đầu ra riêng của mô hình (hoặc quy tắc gộp ghi trong docstring), không được để trống.
- ABTE (Could Have): nằm trong `core/sentiment/abte.py`, chỉ chạy khi `ENABLE_ABTE=true`, chỉ điền `terms`.
  Tắt thì hệ thống phải chạy y hệt tầng lõi.

## Taxonomy
- `configs/aspects.yaml`: danh sách khía cạnh {id, tên tiếng Việt, mô tả, bộ phận xử lý, trọng số mặc định}.
  Số khía cạnh 5-8 *(xác nhận sau khi chọn bộ dữ liệu)*.
- `core/taxonomy.py` nạp và kiểm tra tính hợp lệ (id duy nhất, trọng số trong khoảng cho phép).
- Mọi nơi cần danh sách khía cạnh đều đọc từ đây; API công bố qua `GET /api/v1/meta/aspects`.

## Priority Engine (rule-based, trọng số trong configs/priority_rules.yaml)
`calculate_priority(result: AbsaResult, text: str) -> PriorityBreakdown` với
`PriorityBreakdown(score, base, urgency_bonus, intensity_bonus, aspect_bonus, reasons: list[str])`.
- base: negative = 60*confidence; neutral = 20; positive = 5 (theo `result.overall`).
- urgency: từ khóa rủi ro; câu cuối +20, câu trước +10, mỗi từ khóa một lần, trần `urgency_cap` = 30 *(xác nhận)*;
  bỏ qua nếu bị phủ định ngay trước ("không|chưa|đừng|chẳng") *(xác nhận)*.
- intensity: +5 nếu có "!!!" hoặc viết hoa toàn bộ (len>5) VÀ overall là negative *(xác nhận)*.
- aspect_bonus: với mỗi khía cạnh negative, cộng `weight[aspect] * confidence`; lấy khía cạnh nặng nhất cộng
  đủ, các khía cạnh còn lại cộng 25% *(xác nhận công thức)*, trần `aspect_cap` trong YAML.
- score = min(100, tổng), làm tròn 2 chữ số. `reasons` là danh sách giải thích tiếng Việt cho từng phần cộng
  (FE hiển thị, hội đồng kiểm toán được).
- Mô hình dự phòng (aspects rỗng) cho aspect_bonus = 0, kết quả phải khớp công thức document-level cũ.
- Mọi hàm là hàm thuần; không đọc DB hay mạng.

## Quy tắc code
- Type hint đầy đủ, docstring ngắn, hàm nhỏ.
- Endpoint gọi model (nặng CPU) dùng `def` thường, không `async def`.
- Nạp model 1 lần trong `lifespan` và warm-up; không nạp trong request.
- Heap chỉ là cache trong RAM, SQLite là nguồn sự thật; nạp lại heap từ DB khi khởi động. Chạy 1 worker.
- SQLite: `connect_args={"check_same_thread": False}`; tạo bảng bằng `create_all`, không dùng Alembic.
- Lỗi trả JSON thống nhất `{"detail": ..., "code": ...}`; validate đầu vào bằng Pydantic.
- Tiền tố API `/api/v1`. Đổi response_model thì cập nhật hợp đồng.

## Database
- `tickets`: như thiết kế gốc (content, processed_content, sentiment_label, confidence, priority_score, status,
  language_flag, created_at, updated_at) cộng `priority_breakdown` (JSON) và `low_confidence` (bool).
- `ticket_aspects`: id PK, ticket_id FK (index, ON DELETE CASCADE), aspect (index), sentiment, confidence, terms (JSON, nullable).
- Ticket được lưu cùng các dòng `ticket_aspects` trong một transaction.

## API
- `POST /tickets/triage` (201), `GET /tickets/queue` (limit, offset, status, aspect, sentiment),
  `PATCH /tickets/{id}/status`, `GET /meta/aspects`, `GET /health`.
- `GET /stats/sentiment`, `/stats/priority`, `/stats/trend`, `/stats/aspects` (ma trận khía cạnh x cảm xúc,
  có thể lọc theo khoảng ngày).
- `TicketOut` có: `aspects: list[AspectOut]`, `priority_breakdown`, `low_confidence`, `language_flag`.
- `low_confidence = true` khi confidence tổng thể < 0.5 *(xác nhận)*; mô hình ngôn ngữ không hỗ trợ thì
  không gọi model, gắn cờ thủ công và điểm 50.

## Mô hình và dữ liệu
- roBERT cần văn bản ĐÃ TÁCH TỪ; dùng đúng `preprocess()` (remove_stopwords=False) ở cả train và predict.
- Bộ dữ liệu ABSA và domain *(xác nhận: VLSP 2018 hoặc UIT-ViSFD)*; taxonomy suy ra từ bộ này.
  Mỗi nguồn có mapping nhãn riêng trong `training/data_prep.py`; in mẫu để kiểm tra trước khi gộp.
- Chia train/val/test stratified với seed=42; với đa nhãn dùng chia theo tổ hợp nhãn hoặc theo mẫu, không để một
  câu xuất hiện ở nhiều tập. Chọn mô hình bằng val; chạy test đúng một lần ở cuối.
- Mất cân bằng nhãn nghiêm trọng theo từng khía cạnh: dùng class weight theo khía cạnh, báo cáo F1 từng khía cạnh.
- Metric: F1 phát hiện khía cạnh (micro/macro) và F1-macro cảm xúc trên các cặp (khía cạnh, cảm xúc). Ngưỡng
  nghiệm thu đặt SAU khi có baseline *(xác nhận)*.
- Checkpoint đặt tên `<model>_<yyyy-mm-dd>_f1-<số>`; nạp bằng `local_files_only=True`.

## Test
- Unit test cho mọi hàm trong `core/` (ca biên: rỗng, rất dài, teencode nặng, tiếng nước ngoài, nhiều khía cạnh
  cùng lúc, khía cạnh trùng, khía cạnh ngoài taxonomy).
- Test Priority: từng thành phần của breakdown, trần, phủ định, mô hình dự phòng cho kết quả khớp công thức cũ.
- Integration test dùng TestClient + SQLite in-memory + MockSentimentModel (mock trả cả aspects).
- Test cần torch phải tự skip khi không có torch. CI không cài extras `ml`.

## Không làm
Không thêm Docker service mới, ORM khác, phân quyền, hàng đợi phân tán, hay ML cho điểm ưu tiên.
Không đổi taxonomy hoặc dataclass hợp đồng khi chưa có quyết định của nhóm. Không thêm thư viện vào
pyproject khi chưa hỏi.