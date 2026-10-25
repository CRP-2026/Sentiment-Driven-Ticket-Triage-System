# Ticket Triage System (ABSA): Quy tắc chung

Hệ thống phân tích cảm xúc theo khía cạnh (ABSA) cho phản hồi khách hàng tiếng Anh, tính điểm ưu tiên
(0-100) để đẩy ticket khẩn cấp lên đầu hàng đợi. Đồ án nhóm, chạy bằng Docker Compose trên máy local,
không deploy lên server.

## Cấu trúc thư mục
- `ticket-triage-be/`  Python 3.11, FastAPI, SQLAlchemy 2.0, SQLite
- `ticket-triage-fe/`  React, Vite, TypeScript, pnpm, TailwindCSS
- `contracts/openapi.json`  Hợp đồng giao tiếp BE-FE, sinh từ backend
- `docs/`  Tài liệu quản lý (Charter, WBS, System Architecture Report, start.md)

## Pipeline toàn trình
`preprocess` -> `ABSA Zero-shot NLI` (aspects + sentiment từng khía cạnh + cảm xúc tổng thể)
-> `priority` (0-100, rule-based có breakdown) -> `queue` (max-heap heapq) + SQLite -> `dashboard`.

## Phạm vi mô hình (3 tầng, làm theo thứ tự)
1. **LÕI (Must Have):** Với mỗi ticket, phân loại cảm xúc cho từng khía cạnh trong taxonomy 5 khía cạnh cố định (`customer_service`, `refund_payment`, `product_quality`, `shipping`, `general`).
   Mỗi khía cạnh có 4 lớp: `not_mentioned`, `negative`, `neutral`, `positive`.
2. **DỰ PHÒNG (Luôn chạy được):** Mô hình cảm xúc cấp văn bản (`MODEL_TASK=document`), trả `AbsaResult` với aspects rỗng.
3. **MỞ RỘNG (Could Have, chỉ làm khi tầng 1 xong và được nhóm đồng ý):** ABTE, trích xuất cụm từ nêu khía cạnh,
   bật bằng `ENABLE_ABTE=true`. Không được làm hỏng hợp đồng của tầng 1.

## Quy tắc xuyên suốt
1. **Backend là nguồn sự thật của schema.** FE không tự định nghĩa lại kiểu response.
2. **Đổi schema API:** Chạy `make gen-api`, commit `openapi.json` và `schema.d.ts` trong cùng PR.
3. **Danh mục khía cạnh (taxonomy) nằm ở MỘT nơi:** `ticket-triage-be/configs/aspects.yaml`. FE lấy qua
   `GET /api/v1/meta/aspects`, không hard-code. Đổi taxonomy sau khi đã gán nhãn nghĩa là gán lại dữ liệu,
   nên chỉ đổi khi có quyết định của nhóm và ghi vào change log.
4. **Trạng thái ticket (đúng thứ tự):** "Mới tiếp nhận" (`new`) -> "Đã phân công" (`assigned`) -> "Đang xử lý" (`in_progress`) -> "Đã giải quyết" (`resolved`).
5. **Ngưỡng ưu tiên:** $\ge 70$ Cao (đỏ), $30-69$ Trung bình (vàng), $< 30$ Thấp (xanh).
6. **Priority Engine là rule-based có chủ đích** (minh bạch, kiểm toán được). Trọng số khía cạnh nằm trong YAML.
   Tuyệt đối không thay bằng ML.
7. **Phạm vi ngôn ngữ:** Chuyên biệt tiếng Anh (English-only). Ngoại ngữ khác gắn cờ `needs_manual_review = True`.
8. **Ngoài phạm vi, không làm:** RBAC, Kafka/RabbitMQ, tích hợp API Zendesk/Gmail, deploy lên cloud/server.
9. **Không commit:** Dữ liệu lớn, checkpoint model, file `.db`, `.env`, `node_modules`, `.venv`, `__pycache__`.
10. Dữ liệu huấn luyện ABSA đến từ bộ công khai tiếng Anh (Amazon Reviews / Customer Support) và ticket kiểm thử là dữ liệu mô phỏng. Luôn ghi rõ điều này trong báo cáo, không trình bày như dữ liệu CSKH thật.

## Docker
- Môi trường chuẩn là Docker Compose. Mọi lệnh test/lint/seed chạy qua `make` hoặc Docker CLI (bên trong container).
- `make up` (dev, hot reload), `make demo` (bản đóng gói cho bảo vệ), `make reset-db` (xóa SQLite).
- Không đóng gói dữ liệu, checkpoint, `.env` vào image. Model được mount từ `ticket-triage-be/models`.
- Huấn luyện chạy ngoài Docker (Colab/Kaggle T4 GPU); Docker chỉ dùng cho suy luận.
- Thêm biến môi trường hoặc cổng mới phải cập nhật `docker.yaml`, `.env.example` và `README.md`.

## Quy trình
- Nhánh: `feat/<module>-<mô tả>`, `fix/...`, `docs/...`. Không push thẳng vào `main` hay `dev`.
- Commit: Conventional Commits, scope: `core`, `api`, `db`, `training`, `web`, `docs`, `ci`. Ví dụ: `feat(core): add aspect weights`.
- PR: Một việc, gắn `Fixes #<issue>`, CI xanh, có test, ít nhất 1 approval. PR đổi hợp đồng cần người của cả BE và FE review.
- Chỉ làm đúng phạm vi yêu cầu. Thiếu thông tin thì nêu giả định trước khi code, không tự mở rộng tính năng.
- Trước khi báo xong: Chạy `make lint test` và nói rõ lệnh nào đã chạy, kết quả ra sao.