# Hướng Dẫn Review Code Cho AI Bot (AI Review Guidelines)

Tài liệu này định nghĩa bộ tiêu chí và barem chấm điểm mà AI Code Reviewer bắt buộc phải đối chiếu khi review các Pull Request trong dự án **Sentiment-Driven Ticket Triage System**.

---

## 1. Nguyên Tắc Cốt Lõi Dự Án (Tham chiếu `AGENT.md`)

1. **Hợp đồng API (Schema Contract)**:
   - Backend là nguồn sự thật duy nhất (`ticket-triage-be/contracts/openapi.json`).
   - Mọi thay đổi schema API phải đi kèm việc cập nhật `contracts/openapi.json` và sinh lại `ticket-triage-fe/src/api/schema.d.ts` trong cùng PR.
   - Frontend **tuyệt đối không** tự định nghĩa lại các kiểu dữ liệu response đã có trong `schema.d.ts`.

2. **Quản lý Taxonomy & Khía cạnh (ABSA)**:
   - Danh mục khía cạnh duy nhất đặt tại `ticket-triage-be/configs/aspects.yaml`.
   - Frontend lấy danh mục qua API `GET /api/v1/meta/aspects`, không được hardcode danh sách tên khía cạnh trong component.

3. **Luật Đánh Điểm Ưu Tiên (Priority Engine)**:
   - Phải là Rule-based minh bạch, không được thay thế bằng Machine Learning.
   - Ngưỡng điểm chuẩn:
     - $\ge 70.0$: Cao / Khẩn cấp (`CRITICAL` - Đỏ)
     - $30.0 - 69.9$: Trung bình (`MEDIUM` - Vàng)
     - $< 30.0$: Thấp (`LOW` - Xanh)

4. **Trật tự Trạng thái Ticket**:
   - Thứ tự chuẩn: `new` -> `assigned` -> `in_progress` -> `resolved`.

5. **Phạm vi Ngôn ngữ**:
   - Model ABSA chỉ xử lý tiếng Anh (English-only). Nếu phát hiện ngôn ngữ khác phải gắn cờ `needs_manual_review = True`.
   - Giao diện người dùng và thông báo hiển thị cho người dùng phải dùng **tiếng Việt**.

---

## 2. Tiêu Chuẩn Kỹ Thuật (Tech Stack & Code Quality)

### Backend (Python / FastAPI)
- Tuân thủ Python 3.11, bắt buộc dùng Type Annotations đầy đủ.
- Dùng SQLAlchemy 2.0 style (`select(...)`, `scalars(...)`), không dùng query syntax cũ của SQLAlchemy 1.x.
- Xử lý ngoại lệ rõ ràng, trả về HTTP status code phù hợp.
- Có test tương ứng (`pytest`) cho các hàm / endpoint mới hoặc đã sửa đổi.

### Frontend (React / TypeScript / Vite / TailwindCSS)
- Tuân thủ TypeScript Strict Mode. **Không dùng `any`** (dùng `unknown`, `never`, hoặc định nghĩa type/interface cụ thể).
- Gọi API phải bọc qua `src/api/client.ts` và custom hooks (`TanStack Query`), không dùng `fetch`/`axios` trực tiếp trong component.
- Không commit file cấu hình monorepo nếu làm hỏng cấu trúc pnpm đơn lẻ.

---

## 3. An Toàn & Bảo Mật (Security & Anti-patterns)
- **Tuyệt đối KHÔNG commit**:
  - File môi trường / bí mật: `.env`, `.env.local`, API keys, tokens.
  - File dữ liệu local: SQLite `.db`, `.db-wal`, checkpoints mô hình `.pt`, `.safetensors`.
  - Thư mục build: `node_modules/`, `dist/`, `.venv/`, `__pycache__/`.
- Kiểm tra validation đầu vào (Pydantic / Zod) để tránh lỗi injection và tràn dữ liệu.

---

## 4. Định Dạng Báo Cáo Của Bot (Review Output Format)

Khi gửi nhận xét trên PR, Bot phải trình bày bằng **tiếng Việt** theo cấu trúc sau:

```markdown
## 🤖 Đánh Giá Code Tự Động (AI Code Review)

### 📊 Đánh Giá Chung
*(Tóm tắt ngắn gọn 2-3 câu về nội dung PR, mức độ rủi ro và chất lượng tổng thể)*

---

### ✅ Điểm Đạt (Strengths)
- *(Những điểm làm tốt, tuân thủ đúng kiến trúc AGENT.md)*

---

### ⚠️ Điểm Cần Cải Thiện / Lỗi Vi Phạm (Findings & Issues)
*(Nếu có, ghi rõ file, vị trí dòng và đề xuất code sửa đổi cụ thể)*
- **[Tên file / Vấn đề]**:
  - **Lý do**:
  - **Đề xuất khắc phục**:
    ```language
    // code gợi ý
    ```

---

### 📋 Đối Chiếu Hướng Dẫn (`AGENT.md`)
| Tiêu chí | Trạng thái | Ghi chú |
| :--- | :---: | :--- |
| API Schema Contract Sync | ✅ / ❌ / ➖ | |
| Taxonomy Not Hardcoded | ✅ / ❌ / ➖ | |
| Rule-based Priority Logic | ✅ / ❌ / ➖ | |
| No Sensitive / Big Files | ✅ / ❌ / ➖ | |
| Unit Test Included | ✅ / ❌ / ➖ | |

---

### 🎯 Kết Luận
- **Khuyến nghị**: `APPROVE` / `REQUEST CHANGES` / `COMMENT`
```
