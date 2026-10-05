# Frontend (React + Vite + TypeScript, ABSA)

## Lệnh (chạy qua Docker)
- Khởi động: `make up` (FE ở http://localhost:5173, proxy /api sang service backend)
- Kiểm tra đầy đủ: `docker compose exec frontend npm run check`
- Sinh kiểu từ backend: `make gen-api` (đọc /contracts/openapi.json)
- Chạy không cần backend: `VITE_USE_MOCK=true`
- Thêm thư viện: `docker compose exec frontend npm install <pkg>`, commit cả package.json và package-lock.json.

## Công nghệ
React, TypeScript (strict), Tailwind, shadcn/ui, TanStack Query, React Router, Recharts, Vitest + Testing Library.
Không thêm thư viện mới khi chưa hỏi.

## Cấu trúc `src/`
- `api/`: `client.ts` (ApiError tiếng Việt), `hooks.ts`, `queryKeys.ts`, `schema.d.ts` (SINH TỰ ĐỘNG, không sửa tay).
- `pages/`: InboxPage, TesterPage, AnalyticsPage, NotFoundPage. Trang chỉ ghép component và hook.
- `components/`: `layout/`, `tickets/` (TicketTable, PriorityBadge, StatusSelect, AspectChips, PriorityBreakdown),
  `charts/` (SentimentPie, PriorityHistogram, TrendLine, AspectHeatmap), `ui/` (shadcn).
- `lib/`: `constants.ts` (ngưỡng 70/30, STATUSES, màu, hằng số polling), `format.ts`, `utils.ts`.
- `mocks/`: dữ liệu giả đủ 3 mức ưu tiên và nhiều khía cạnh khác nhau.

## Quy tắc code
- Kiểu dữ liệu API lấy từ `schema.d.ts`; tuyệt đối không tự định nghĩa lại kiểu response.
- Mọi lời gọi API đi qua `api/client.ts` và hooks; component không gọi fetch trực tiếp.
- Danh sách khía cạnh (id, tên tiếng Việt, mô tả) lấy từ `GET /meta/aspects` qua hook `useAspects()`
  (staleTime dài). KHÔNG hard-code tên khía cạnh trong component. Khía cạnh lạ (id không có trong danh sách)
  hiển thị theo id gốc, không làm vỡ giao diện.
- Server là nguồn sắp xếp hàng đợi (priority_score giảm dần); FE không sắp xếp lại.
- Cập nhật dữ liệu:
  - Mọi mutation `invalidateQueries` cho queue và stats trong `onSuccess`.
  - Query `queue`: staleTime 2s, refetchInterval 3s, `refetchIntervalInBackground: false`, `placeholderData: keepPreviousData`.
  - Query `stats`: refetchInterval 10s. Query `health`: 30s. Query `aspects` meta: không polling.
  - Giữ refetchOnWindowFocus và refetchOnReconnect ở mặc định. Các hằng số này đặt ở `lib/constants.ts`.
  - Không dùng WebSocket. SSE chỉ khi nhóm quyết định (Could Have), vẫn kết thúc bằng `invalidateQueries`.
- Đổi trạng thái ticket dùng optimistic update và rollback khi lỗi.
- Màu ưu tiên: >=70 đỏ "Cao", 30-69 vàng "Trung bình", <30 xanh "Thấp"; luôn hiển thị chữ và số
  (không chỉ dựa vào màu), có `aria-label`.
- Mọi màn hình có đủ 3 trạng thái: loading (skeleton), rỗng, lỗi (có nút Thử lại).
- Giao diện và thông báo bằng tiếng Việt. Function component và hook; tránh `any`.

## Hiển thị ABSA
- Inbox: mỗi ticket có chip khía cạnh (tên + biểu tượng cảm xúc), tô màu theo cảm xúc (tiêu cực đỏ, trung tính xám,
  tích cực xanh) và không dựa vào màu đơn thuần (kèm nhãn chữ). Hiện tối đa 3 chip, phần dư "+N". Sắp chip: tiêu cực trước.
- Bộ lọc Inbox theo khía cạnh và cảm xúc, gửi lên server qua query params; FE không tự lọc dữ liệu đã phân trang.
- Ticket không có khía cạnh (mô hình dự phòng) hiển thị "Chưa phân tích khía cạnh", không để trống.
- Tester: hiển thị cảm xúc tổng thể, bảng khía cạnh (khía cạnh, cảm xúc, độ tin cậy) và `PriorityBreakdown`
  dựng từ `priority_breakdown.reasons` của API; FE không tự tính lại điểm.
- Nếu có `terms` (ABTE) thì làm nổi bật cụm từ trong nội dung; không có thì bỏ qua, không báo lỗi.
- Analytics: `AspectHeatmap` (khía cạnh x cảm xúc, số ticket) lấy từ `/stats/aspects`; ô có chú thích số liệu,
  thang màu có legend, hỗ trợ khi tất cả bằng 0.
- Ticket `low_confidence` hoặc `language_flag = "unsupported"` hiển thị cảnh báo "Cần xem lại thủ công".

## Test
Vitest + Testing Library. Cần test: PriorityBadge ở ranh giới 29/30/69/70, TicketTable, AspectChips
(nhiều chip, khía cạnh lạ, rỗng), đổi trạng thái, hooks (mock fetch), TesterPage (gửi và hiện bảng khía cạnh),
AspectHeatmap (dữ liệu rỗng).

## Hợp đồng với backend
Backend đổi schema thì chạy `npm run gen-api` và sửa lỗi biên dịch trong cùng PR. Cần field mới từ backend thì
ghi TODO và báo người phụ trách backend, không tự suy đoán cấu trúc dữ liệu. Luôn gọi API bằng đường dẫn
tương đối `/api/v1/...`, không hard-code localhost:8000.

## Không làm
Không đăng nhập/phân quyền, không SSR/Next.js, không lưu state quan trọng ở localStorage, không hard-code
taxonomy, không tự tính điểm ưu tiên ở FE.