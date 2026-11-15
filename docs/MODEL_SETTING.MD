# Hướng dẫn cấu hình & kích hoạt Model AI thật (`MODEL_SETTING`)

Hệ thống hỗ trợ chuyển đổi giữa chế độ giả lập (`mock`) và các mô hình Zero-shot NLI thật (`baseline`, `deberta`, model từ HuggingFace bất kỳ, hoặc model local/fine-tuned) hoàn toàn qua biến môi trường (`.env`) mà không cần sửa mã nguồn.

---

## 1. Điều kiện tiên quyết (Cài thư viện ML)

Mặc định `requirements.txt` chỉ cài các thư viện nhẹ để chạy FastAPI + `MockSentimentModel`. Để chạy model thật (`torch` + `transformers`), bạn cần cài thêm gói ML:

### Chạy Local (Python `.venv` trong `ticket-triage-be/`)
```powershell
cd ticket-triage-be
.\.venv\Scripts\python.exe -m pip install -r requirements-ml.txt
```
> **Lưu ý nếu dùng DeBERTa (`deberta-v3`):** Tokenizer của DeBERTa v3 thường cần thêm `sentencepiece` (và `protobuf` nếu môi trường báo thiếu):
> ```powershell
> .\.venv\Scripts\python.exe -m pip install sentencepiece protobuf
> ```

### Chạy Docker
Build container kèm cờ `INSTALL_ML=true`:
```powershell
docker compose -f docker.yaml build --build-arg INSTALL_ML=true
```

---

## 2. Thứ tự ưu tiên nạp model trong hệ thống

Khi khởi động Backend (`src/ticket_triage/api/main.py`):

1. Nếu `MODEL_NAME=mock` (hoặc rỗng) → dùng `MockSentimentModel`.
2. Nếu `MODEL_NAME` khác `mock` (ví dụ `baseline`, `deberta`, `custom`):
   - **Ưu tiên 1 (`MODEL_PATH` local):** Kiểm tra thư mục ở `MODEL_PATH` (mặc định `./models` khi chạy từ `ticket-triage-be/`, hoặc `/app/models` trong Docker). Nếu trong thư mục đó **có file `config.json`**, hệ thống nạp model trực tiếp từ ổ cứng.
   - **Ưu tiên 2 (`MODEL_ID` trong `.env`):** Nếu `MODEL_PATH` rỗng hoặc chưa có `config.json` (như thư mục `models/` chỉ có `.gitkeep`), hệ thống đọc biến `MODEL_ID`.
   - **Ưu tiên 3 (`DEFAULT_HF_MODELS` mặc định):** Nếu cả `MODEL_ID` cũng trống, tự chọn repo HuggingFace mặc định trong `baseline.py`:
     - `baseline` → `valhalla/distilbart-mnli-12-3`
     - `deberta` → `MoritzLaurer/deberta-v3-base-zeroshot-v1.1-all-33`

---

## 3. Ba cách thiết lập qua `.env`

Copy file mẫu trước khi cấu hình:
- Chạy local ở `ticket-triage-be/`: copy `ticket-triage-be/.env.example` → `ticket-triage-be/.env`
- Chạy Docker ở thư mục gốc: copy `.env.example` → `.env`

### Cách A — Dùng model HuggingFace mặc định (`baseline` hoặc `deberta`)
Phù hợp khi chạy lần đầu có Internet (mạng sẽ tự tải và cache vào `~/.cache/huggingface`):

```env
MODEL_NAME=deberta
MODEL_PATH=./models
MODEL_ID=
HF_HUB_OFFLINE=0
```
- Nếu máy RAM ít hoặc muốn chạy nhẹ/nhanh hơn, đổi `MODEL_NAME=baseline` (`valhalla/distilbart-mnli-12-3`).
- Sau lần chạy đầu tiên đã cache xong, có thể đặt lại `HF_HUB_OFFLINE=1`.

### Cách B — Chỉ định một model HuggingFace Zero-shot NLI bất kỳ qua `MODEL_ID`
Không cần sửa `DEFAULT_HF_MODELS` trong code:

```env
MODEL_NAME=deberta
MODEL_PATH=
MODEL_ID=facebook/bart-large-mnli
HF_HUB_OFFLINE=0
```

### Cách C — Chạy model Offline từ thư mục `ticket-triage-be/models/`
Phù hợp khi bạn đã tải sẵn model hoặc có model fine-tuned lưu trên máy (và chạy Docker offline với volume `./ticket-triage-be/models:/app/models:ro`):

1. Chép toàn bộ thư mục model vào `ticket-triage-be/models/` (hoặc thư mục con `ticket-triage-be/models/deberta-v3/`). Bên trong **bắt buộc phải có `config.json`** cùng các file trọng số (`model.safetensors` hoặc `pytorch_model.bin`) và tokenizer (`tokenizer.json`, `tokenizer_config.json`, ...).
2. Cấu hình `.env`:
   - Khi chạy **local** trong `ticket-triage-be/`:
     ```env
     MODEL_NAME=deberta
     MODEL_PATH=./models
     MODEL_ID=
     HF_HUB_OFFLINE=1
     ```
     *(Nếu đặt trong thư mục con thì trỏ `MODEL_PATH=./models/deberta-v3`.)*
   - Khi chạy **Docker** (`docker.yaml`):
     ```env
     MODEL_NAME=deberta
     MODEL_PATH=/app/models
     MODEL_ID=
     HF_HUB_OFFLINE=1
     ```

---

## 4. Tùy biến câu giả định (Prompt / Hypotheses NLI)

Không cần sửa code Python, bạn có thể tinh chỉnh cách model NLI chấm điểm khía cạnh trong `ticket-triage-be/configs/aspect_hypotheses.yaml`:
- `overall_sentiment_template`: Mẫu câu kiểm tra sắc thái tổng thể (mặc định: `"The sentiment of this customer review is {}."`).
- `aspect_sentiment_template`: Mẫu câu kiểm tra cảm xúc theo từng khía cạnh (`{aspect}`, `{sentiment}`).
- `aspect_names`: Mô tả tự nhiên cho từng khía cạnh trong `aspects.yaml`.
- `sentiments`: Nhãn diễn đạt cho `positive`, `neutral`, `negative`.

---

## 5. Cách kiểm tra model thật đã nạp thành công chưa

Sau khi khởi động server, gọi endpoint kiểm tra sức khỏe:
```powershell
curl http://localhost:8000/api/v1/health
```
- **Thành công (đang chạy AI thật):**
  ```json
  {
    "status": "ok",
    "version": "0.1.0",
    "model_name": "deberta",
    "is_mock": false,
    "model_loaded": true,
    "queue_size": 0
  }
  ```
- **Chưa thành công (`"is_mock": true` dù đã đặt `deberta` / `baseline`):**
  Hệ thống đã âm thầm fallback về `MockSentimentModel` để tránh sập API. Hãy xem dòng `CRITICAL WARNING` trong log server để xử lý các lỗi thường gặp:
  1. Thiếu `torch` / `transformers` / `sentencepiece` → cài lại theo Mục 1.
  2. `HF_HUB_OFFLINE=1` nhưng chưa có file trong `models/` và chưa có cache HuggingFace → đổi `HF_HUB_OFFLINE=0` cho lần tải đầu.
  3. Thiếu `config.json` trong `MODEL_PATH` hoặc đặt sai đường dẫn.

---

## 6. Lưu ý nếu dùng model tự huấn luyện không theo chuẩn Zero-shot NLI

`ZeroShotNliModel` hiện dùng `transformers.pipeline("zero-shot-classification", ...)`, nên mọi model chuẩn NLI (MNLI / Zero-shot) đều chạy ngay chỉ qua `.env`.  
Nếu bạn huấn luyện riêng một kiến trúc khác (ví dụ model `AutoModelForSequenceClassification` multi-label hoặc encoder tùy chỉnh không chạy qua `zero-shot-classification`), bạn cần:
1. Tạo class mới trong `ticket-triage-be/src/ticket_triage/core/sentiment/` kế thừa `BaseSentimentModel` và trả về `AbsaResult`.
2. Thêm nhánh khởi tạo class đó trong `ticket-triage-be/src/ticket_triage/api/main.py` ứng với giá trị `MODEL_NAME` mới.
