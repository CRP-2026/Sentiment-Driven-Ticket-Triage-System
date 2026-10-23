# Backend (FastAPI + Core, ABSA Zero-shot NLI)

## Lệnh (chạy qua Docker hoặc Local)
- Khởi động: `make up` (hoặc `docker compose -f docker.yaml up --build`)
- Kiểm thử: `docker compose -f docker.yaml exec backend pytest -v` (hoặc `pytest -v`)
- Linter: `docker compose -f docker.yaml exec backend ruff check .` (hoặc `ruff check .`)
- Xuất hợp đồng: `make gen-api`  Seed demo: `make seed`
- Bật mô hình NLI: `INSTALL_ML=true MODEL_NAME=baseline make up` (checkpoint trong `ticket-triage-be/models`, trỏ `MODEL_PATH`)

## Kiến trúc và quy tắc phụ thuộc
`api -> core, db` (một chiều). Trong `src/ticket_triage/`:
- `core/`: Logic thuần túy. TUYỆT ĐỐI không import `fastapi`, `sqlalchemy`, `pydantic-settings`.
  Gồm `preprocessing/`, `lang_validator.py`, `keyword_prefilter.py`, `priority/`, `queue/` (heapq), `taxonomy.py`, `sentiment/` (ABSA).
- `db/`: SQLAlchemy 2.0, SQLite cục bộ (`tickets.db`). Không chứa logic tính điểm.
- `api/`: Routes mỏng; ghép pipeline ở `services/pipeline.py`. `schemas.py` là hợp đồng với FE.
- `scripts/`: Script seed dữ liệu mẫu, script huấn luyện Colab/Kaggle.
- `settings.py`: Mọi giá trị cấu hình theo môi trường đọc từ `.env`.

## Kiểu dữ liệu và hợp đồng mô hình (ĐÓNG BĂNG, đổi phải qua họp nhóm)
```python
Sentiment = Literal["negative", "neutral", "positive"]

@dataclass(frozen=True)
class SentimentResult:            # Cảm xúc tổng thể của ticket
    label: Sentiment
    confidence: float             # [0.0, 1.0]

@dataclass(frozen=True)
class AspectSentiment:
    aspect: str                   # ID lấy từ configs/aspects.yaml
    sentiment: Sentiment          # Khía cạnh không được nhắc đến thì KHÔNG đưa vào danh sách
    confidence: float             # [0.0, 1.0]
    terms: tuple[str, ...] = ()   # Chỉ có khi ENABLE_ABTE=true (cụm từ trích xuất)

@dataclass(frozen=True)
class AbsaResult:
    overall: SentimentResult
    aspects: list[AspectSentiment]   # Rỗng nếu là mô hình cấp văn bản (dự phòng)
```
- Mọi mô hình cùng interface `predict(text: str, candidates: list[str] | None = None) -> AbsaResult`. Chọn bằng `MODEL_NAME=mock|baseline|deberta`
  và `MODEL_TASK=absa|document` (document = dự phòng cấp văn bản). Import baseline/nli kiểu lazy
  để máy không cài torch vẫn chạy `mock`.
- Bài toán lõi: Với mỗi khía cạnh trong taxonomy, phân loại 4 lớp `{not_mentioned, negative, neutral, positive}`
  trên văn bản tiếng Anh; khía cạnh `not_mentioned` bị loại khỏi đầu ra.
- `overall` lấy từ đầu ra phân loại cảm xúc tổng thể của ticket, không được để trống.
- ABTE (Could Have): Nằm trong `core/sentiment/abte.py`, chỉ chạy khi `ENABLE_ABTE=true`, chỉ điền `terms`.
  Tắt thì hệ thống chạy y hệt tầng lõi.

## Taxonomy
- `configs/aspects.yaml`: Danh sách 5 khía cạnh chuẩn: `customer_service` (1.0), `refund_payment` (1.0), `product_quality` (0.8), `shipping` (0.7), `general` (0.5).
- `core/taxonomy.py` nạp và kiểm tra tính hợp lệ (id duy nhất, trọng số trong khoảng `[0.0, 2.0]`).
- Mọi nơi cần danh sách khía cạnh đều đọc từ đây; API công bố qua `GET /api/v1/meta/aspects`.

## Priority Engine (Rule-based, cấu hình trong configs/priority_rules.yaml)
`calculate_priority(result: AbsaResult, text: str) -> PriorityBreakdown` với
`PriorityBreakdown(score, base, urgency_bonus, intensity_bonus, aspect_bonus, level, dominant_aspect, reasons: list[str])`.
- **base:** Negative = $60.0 \times \text{confidence}$; Neutral = $20.0$; Positive = $5.0$ (theo `result.overall`).
- **urgency:** Từ khóa khẩn cấp tiếng Anh (`lawsuit`, `fraud`, `chargeback`, `broken`, `urgent`...); câu cuối $+20$, câu trước $+10$, mỗi từ khóa một lần, trần `urgency_cap = 30.0`;
  bỏ qua nếu bị phủ định ngay trước bằng tiếng Anh (`"not"`, `"never"`, `"no"`, `"won't"`, `"without"`).
- **intensity:** $+5.0$ nếu có `"!!!"` hoặc viết hoa toàn bộ (CAPS LOCK, len > 5) VÀ cảm xúc tổng thể là negative.
- **aspect_bonus:** Lấy khía cạnh tiêu cực nghiêm trọng nhất cộng đủ 100% ($\text{weight} \times \text{confidence} \times 10.0$), các khía cạnh tiêu cực còn lại cộng $25\%$ phạt dồn, trần `aspect_cap = 20.0`.
- **score:** $\min(100.0, \text{tổng})$, làm tròn 2 chữ số. `reasons` là danh sách giải thích tiếng Việt minh bạch cho từng phần cộng (FE hiển thị, hội đồng kiểm toán được).
- Phân cấp: $\ge 70.0$ `CRITICAL` (Cao), $30.0 - 69.9$ `MEDIUM` (Trung bình), $< 30.0$ `LOW` (Thấp).
- Mọi hàm là hàm thuần túy (Pure Function); không đọc CSDL hay mạng.

## Quy tắc code
- Type hint đầy đủ, docstring ngắn, hàm nhỏ.
- Endpoint gọi model (nặng CPU/GPU) dùng `def` thường, không dùng `async def` để tránh chặn event loop.
- Nạp model 1 lần trong `lifespan` và warm-up; tuyệt đối không nạp model trong từng request.
- Heap chỉ là cache trong RAM, SQLite là nguồn sự thật duy nhất; nạp lại heap từ DB khi khởi động.
- SQLite: `connect_args={"check_same_thread": False}`; bật WAL mode; tạo bảng bằng `create_all`, không dùng Alembic.
- Lỗi trả JSON thống nhất `{"detail": ...}`; validate đầu vào bằng Pydantic.
- Tiền tố API: `/api/v1`. Đổi response_model thì cập nhật hợp đồng qua `make gen-api`.

## Database
- Bảng `tickets`: `id`, `content`, `processed_content`, `language_flag`, `needs_manual_review`, `sentiment_label`, `confidence`, `low_confidence`, `priority_score`, `priority_level`, `dominant_aspect`, `priority_breakdown` (JSON), `status`, `assigned_to`, `created_at`, `updated_at`.
- Bảng `ticket_aspects`: `id` PK, `ticket_id` FK (index, `ON DELETE CASCADE`), `aspect`, `sentiment`, `confidence`, `terms` (JSON, nullable).
- Ticket được lưu cùng các dòng `ticket_aspects` trong một Database Transaction duy nhất.

## API Endpoints
- `POST /api/v1/tickets` (201), `GET /api/v1/tickets` (phân trang, lọc `status`, `aspect`, `sentiment`).
- `GET /api/v1/tickets/{id}`, `PATCH /api/v1/tickets/{id}/status`, `GET /api/v1/meta/aspects`, `GET /api/v1/health`.
- `GET /api/v1/stats/overview`, `/api/v1/stats/aspects`.
- `low_confidence = true` khi confidence tổng thể < 0.50; nếu phát hiện ngoại ngữ (không phải tiếng Anh), không gọi model, gắn cờ `needs_manual_review = True` và gán điểm sàn an toàn 50.0.

## Mô hình ABSA Zero-shot NLI và Dữ liệu
- Ngôn ngữ: **Chuyên biệt tiếng Anh (English-only)**. Không dùng module tách từ tiếng Việt.
- Mô hình: Zero-shot Classification NLI (`valhalla/distilbart-mnli-12-3` hoặc `MoritzLaurer/deberta-v3-base-zeroshot-v1.1-all-33`), fine-tuned với LoRA/PEFT trên Google Colab/Kaggle T4 GPU.
- Dữ liệu nghiên cứu: Amazon Reviews 2023 / Customer Support datasets tiếng Anh công khai; tập kiểm thử là 150–200 ticket CSKH tiếng Anh gán nhãn thủ công.
- Chỉ tiêu nghiệm thu (M5): F1-macro trên từng khía cạnh đạt **$\ge 0.78$**.
- Checkpoint đặt tên `<model>_<yyyy-mm-dd>_f1-<số>`; nạp bằng `local_files_only=True`.

## Kiểm thử (Tests)
- Unit test cho mọi hàm trong `core/` (ca biên: chuỗi rỗng, văn bản dài, viết tắt/slang tiếng Anh, ngoại ngữ bị chặn, nhiều khía cạnh cùng lúc).
- Test Priority: Từng thành phần breakdown, trần điểm, xử lý từ phủ định tiếng Anh.
- Integration test dùng `TestClient` + SQLite in-memory + `MockSentimentModel`.
- Test cần torch phải tự skip khi không có torch. CI không cài extras `ml`.

## Không làm
- Không thêm Docker service mới, không dùng ORM khác ngoài SQLAlchemy 2.0, không phân quyền RBAC phức tạp, không dùng Kafka/Celery, không dùng ML hộp đen cho điểm ưu tiên.
- Không đổi taxonomy hoặc dataclass hợp đồng khi chưa có quyết định của nhóm.