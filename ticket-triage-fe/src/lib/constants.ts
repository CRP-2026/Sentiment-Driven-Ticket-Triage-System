export const PRIORITY_HIGH = 70.0;
export const PRIORITY_MED = 30.0;

export const POLL_QUEUE_MS = 3_000;
export const POLL_STATS_MS = 10_000;
export const POLL_HEALTH_MS = 30_000;

export const STATUSES = [
  { value: "new", label: "Mới tiếp nhận", colorClass: "bg-blue-50 text-blue-700 border-blue-200" },
  { value: "assigned", label: "Đã phân công", colorClass: "bg-purple-50 text-purple-700 border-purple-200" },
  { value: "in_progress", label: "Đang xử lý", colorClass: "bg-amber-50 text-amber-700 border-amber-200" },
  { value: "resolved", label: "Đã giải quyết", colorClass: "bg-emerald-50 text-emerald-700 border-emerald-200" },
] as const;

export const SENTIMENT_CONFIG = {
  negative: { label: "Tiêu cực", color: "#EF4444", bgClass: "bg-red-50 text-red-700 border-red-200" },
  neutral:  { label: "Trung tính", color: "#64748B", bgClass: "bg-slate-100 text-slate-700 border-slate-200" },
  positive: { label: "Tích cực", color: "#10B981", bgClass: "bg-emerald-50 text-emerald-700 border-emerald-200" },
} as const;
