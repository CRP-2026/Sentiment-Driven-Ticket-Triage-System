# Ticket Triage System (ABSA): quy tắc chung

Hệ thống phân tích cảm xúc theo khía cạnh (ABSA) cho phản hồi khách hàng tiếng Anh, tính điểm ưu tiên
(0-100) để đẩy ticket khẩn cấp lên đầu hàng đợi. Đồ án nhóm, chạy bằng Docker Compose trên máy local,
không deploy lên server.

## Cấu trúc
- `backend/`  Python, FastAPI, SQLAlchemy, SQLite (xem backend/AGENTS.md)
- `frontend/` React, Vite, TypeScript (xem frontend/AGENTS.md)
- `contracts/openapi.json` hợp đồng BE-FE, sinh từ backend
- `docs/` tài liệu quản lý, kiến trúc, báo cáo

## Pipeline
preprocess -> ABSA (aspects + sentiment từng khía cạnh + cảm xúc tổng thể) -> priority (0-100, có breakdown)
-> queue (max-heap) + SQLite -> dashboard.

## Phạm vi mô hình (3 tầng, làm theo thứ tự)
1. LÕI (Must Have): với mỗi ticket, phân loại cảm xúc cho từng khía cạnh trong danh mục cố định.
   Mỗi khía cạnh có 4 lớp: not_mentioned, negative, neutral, positive.
2. DỰ PHÒNG (luôn chạy được): mô hình cảm xúc cấp văn bản (MODEL_TASK=document), trả AbsaResult với aspects rỗng.
3. MỞ RỘNG (Could Have, chỉ làm khi tầng 1 xong và được nhóm đồng ý): ABTE, trích xuất cụm từ nêu khía cạnh,
   bật bằng ENABLE_ABTE=true. Không được làm hỏng hợp đồng của tầng 1.

## Quy tắc xuyên suốt
1. Backend là nguồn sự thật của schema. FE không tự định nghĩa lại kiểu response.
2. Đổi schema API: chạy `make gen-api`, commit `openapi.json` và `schema.d.ts` trong cùng PR.
3. Danh mục khía cạnh (taxonomy) nằm ở MỘT nơi: `backend/configs/aspects.yaml`. FE lấy qua
   `GET /api/v1/meta/aspects`, không hard-code. Đổi taxonomy sau khi đã gán nhãn nghĩa là gán lại dữ liệu,
   nên chỉ đổi khi có quyết định của nhóm và ghi vào docs/management/change_log.md.
4. Trạng thái ticket (đúng thứ tự): "Mới tiếp nhận", "Đã phân công", "Đang xử lý", "Đã giải quyết".
5. Ngưỡng ưu tiên: >=70 Cao (đỏ), 30-69 Trung bình (vàng), <30 Thấp (xanh).
6. Priority Engine là rule-based có chủ đích (minh bạch, kiểm toán được). Trọng số khía cạnh nằm trong YAML.
   Không thay bằng ML.
7. Ngoài phạm vi, không làm: RBAC, Kafka/RabbitMQ, tích hợp API Zendesk/Gmail, deploy lên cloud/server.
8. Không commit: dữ liệu, checkpoint model, file .db, .env, node_modules, .venv.
9. Dữ liệu huấn luyện ABSA đến từ bộ công khai (lệch miền so với CSKH) và ticket là dữ liệu mô phỏng.
   Luôn ghi rõ điều này trong báo cáo, không trình bày như dữ liệu CSKH thật.

## Docker
- Môi trường chuẩn là Docker Compose. Mọi lệnh test/lint/seed chạy qua `make` (bên trong container).
- `make up` (dev, hot reload), `make demo` (bản đóng gói cho bảo vệ), `make reset-db` (xóa SQLite).
- Không đóng gói dữ liệu, checkpoint, .env vào image. Model được mount từ `backend/models`.
- Huấn luyện chạy ngoài Docker (Colab/Kaggle); Docker chỉ dùng cho suy luận.
- Thêm biến môi trường hoặc cổng mới phải cập nhật docker-compose.yml, .env.example và README.

## Quy trình
- Nhánh: `feat/<module>-<mô tả>`, `fix/...`, `docs/...`. Không push thẳng vào main.
- Commit: Conventional Commits, scope: core, api, db, training, web, docs, ci. Ví dụ `feat(core): add aspect weights`.
- PR: một việc, gắn `Fixes #<issue>`, CI xanh, có test, ít nhất 1 approval. PR đổi hợp đồng cần người của cả BE và FE review.
- Chỉ làm đúng phạm vi yêu cầu. Thiếu thông tin thì nêu giả định trước khi code, không tự mở rộng tính năng.
- Trước khi báo xong: chạy `make lint test` và nói rõ lệnh nào đã chạy, kết quả ra sao.