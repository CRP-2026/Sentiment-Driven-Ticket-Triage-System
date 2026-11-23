# Frontend (React + Vite + TypeScript + pnpm, ABSA)

## Lệnh (chạy qua Docker hoặc Local)
- Khởi động: `make up` (hoặc `pnpm run dev` tại `ticket-triage-fe/`, proxy `/api` sang backend)
- Kiểm tra toàn diện (Lint + Types): `pnpm run check` (hoặc qua Docker: `docker compose -f docker.yaml exec frontend pnpm run check`)
- Sinh kiểu từ backend: `make gen-api` (hoặc `pnpm run gen-api`)
- Chạy kiểm thử: `pnpm run test` (Vitest)
- Thêm thư viện: `pnpm add <pkg>`, commit cả `package.json` và `pnpm-lock.yaml`. Tuyệt đối không dùng `npm`.

## Công nghệ
React 18, TypeScript (strict mode), TailwindCSS, TanStack Query v5, React Router v6, Recharts, Lucide Icons, Vitest + Testing Library.
Không tự ý thêm thư viện mới khi chưa hỏi nhóm.

## Cấu trúc thư mục `src/`
- `api/`: `client.ts` (Fetch wrapper, `ApiError` tiếng Việt), `hooks.ts`, `queryKeys.ts`, `schema.d.ts` (SINH TỰ ĐỘNG từ `openapi.json` – KHÔNG sửa tay).
- `pages/`: `InboxPage.tsx` (Hộp thư ưu tiên), `TesterPage.tsx` (Live Tester), `AnalyticsPage.tsx` (Thống kê biểu đồ), `NotFoundPage.tsx`. Trang chỉ ghép component và hook.
- `components/`: `layout/` (`AppShell.tsx`, `Navigation.tsx`), `tickets/` (`TicketTable.tsx`, `PriorityBadge.tsx`, `StatusSelect.tsx`, `AspectChips.tsx`, `PriorityBreakdown.tsx`).
- `lib/`: `constants.ts` (ngưỡng 70/30, STATUSES, mã màu, hằng số polling), `format.ts`, `utils.ts` (`cn`).
- `mocks/`: `tickets.ts` (dữ liệu giả lập đủ 3 mức ưu tiên và nhiều khía cạnh).

## Quy tắc code
- Kiểu dữ liệu API lấy từ `schema.d.ts`; tuyệt đối không tự định nghĩa lại kiểu response.
- Mọi lời gọi API đi qua `api/client.ts` và hooks; component không gọi `fetch` trực tiếp.
- Danh sách khía cạnh (id, tên tiếng Việt, mô tả) lấy từ `GET /api/v1/meta/aspects` qua hook `useAspects()` (staleTime 5 phút). KHÔNG hard-code tên khía cạnh trong component.
- Server là nguồn sắp xếp hàng đợi (theo `priority_score` giảm dần); FE không tự sắp xếp lại.
- Cập nhật dữ liệu:
  - Mọi mutation `invalidateQueries` cho danh sách `tickets` và `stats` trong `onSuccess`.
  - Query `tickets`: staleTime 2s, refetchInterval 3s (Polling 3s).
  - Query `stats`: refetchInterval 10s. Query `health`: 30s.
- Đổi trạng thái ticket dùng optimistic update và rollback khi lỗi.
- Màu ưu tiên:
  - $\ge 70.0$ Đỏ "Cao" (`#EF4444`, `CRITICAL`),
  - $30.0 - 69.9$ Vàng "Trung bình" (`#F59E0B`, `MEDIUM`),
  - $< 30.0$ Xanh "Thấp" (`#10B981`, `LOW`).
  - Luôn hiển thị chữ kèm số điểm và có `aria-label`.
- Giao diện và thông báo bằng tiếng Việt. Function components và custom hooks; tránh dùng kiểu `any`.

## Hiển thị ABSA
- **Inbox:** Mỗi ticket hiển thị chip khía cạnh (tên khía cạnh + cảm xúc), tô màu theo cảm xúc (tiêu cực đỏ, trung tính xám, tích cực xanh). Hiển thị tối đa 3 chip, phần dư "+N". Sắp xếp chip: tiêu cực lên trước.
- Bộ lọc Inbox theo khía cạnh và cảm xúc gửi lên server qua query params; FE không tự lọc client-side dữ liệu đã phân trang.
- Ticket không có khía cạnh hiển thị "Chưa phân tích khía cạnh", không để trống.
- **Tester:** Hiển thị cảm xúc tổng thể, danh sách chip khía cạnh và `PriorityBreakdown` dựng từ `priority_breakdown.reasons` trả về từ API; FE không tự tính lại điểm.
- **Analytics:** Biểu đồ tròn cảm xúc, biểu đồ phân cấp ưu tiên và biểu đồ tần suất khía cạnh từ `/stats/overview` và `/stats/aspects`.
- Ticket có `needs_manual_review = true` hoặc `low_confidence = true` hiển thị huy hiệu cảnh báo nổi bật.

## Hợp đồng với Backend
Backend đổi schema thì chạy `make gen-api` (hoặc `pnpm run gen-api`) và sửa lỗi biên dịch TypeScript trong cùng PR.
Luôn gọi API bằng đường dẫn tương đối `/api/v1/...`, không hard-code `localhost:8000`.

## Không làm
Không làm đăng nhập/phân quyền phức tạp (RBAC), không dùng SSR/Next.js, không lưu state quan trọng ở localStorage, không hard-code taxonomy, không tự tính điểm ưu tiên ở FE, không dùng `npm`.