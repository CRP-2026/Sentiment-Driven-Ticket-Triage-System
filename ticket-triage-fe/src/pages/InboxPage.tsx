import React, { useState } from "react";
import { useTickets, useAspects, useStatsOverview } from "../api/hooks";
import { TicketTable } from "../components/tickets/TicketTable";
import { STATUSES, SENTIMENT_CONFIG } from "../lib/constants";
import { Circle, Filter, Inbox, Layers, RefreshCw, ShieldAlert, TriangleAlert } from "lucide-react";

export const InboxPage: React.FC = () => {
  const [selectedStatus, setSelectedStatus] = useState<string>("");
  const [selectedAspect, setSelectedAspect] = useState<string>("");
  const [selectedSentiment, setSelectedSentiment] = useState<string>("");

  const { data: aspects } = useAspects();
  const { data: stats } = useStatsOverview();
  const { data, isLoading, refetch, isFetching } = useTickets({
    status: selectedStatus || undefined,
    aspect: selectedAspect || undefined,
    sentiment: selectedSentiment || undefined,
    limit: 50,
  });

  const clearFilters = () => {
    setSelectedStatus("");
    setSelectedAspect("");
    setSelectedSentiment("");
  };

  const hasActiveFilters = Boolean(selectedStatus || selectedAspect || selectedSentiment);
  const aspectTally = (data?.items ?? []).reduce<Record<string, number>>((counts, ticket) => {
    ticket.aspects.forEach(({ aspect }) => {
      counts[aspect] = (counts[aspect] ?? 0) + 1;
    });
    return counts;
  }, {});
  const aspectDistribution = Object.entries(aspectTally).sort((a, b) => b[1] - a[1]);
  const maxAspectCount = Math.max(1, ...aspectDistribution.map(([, count]) => count));

  return (
    <div className="inbox-page space-y-6 p-4 pb-8 sm:p-5 sm:pb-8 lg:p-6 lg:pb-8">
      {/* Header and Quick Stats */}
      <div className="flex flex-col gap-4 border-b border-slate-300 pb-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-[26px] font-semibold tracking-tight text-slate-900">Hộp thư ưu tiên</h1>
          <p className="mt-1 max-w-2xl text-sm text-slate-600">
            Hàng đợi trực tiếp, sắp xếp theo mức độ khẩn cấp
          </p>
        </div>

        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="queue-action-button inline-flex min-h-10 items-center gap-2 self-start rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-700 transition-colors hover:border-[#126B67] hover:bg-[#e7f2f1] hover:text-[#126B67] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#126B67] focus-visible:ring-offset-2 disabled:cursor-wait disabled:opacity-60 sm:self-auto"
        >
          <RefreshCw className={`h-4 w-4 ${isFetching ? "animate-spin text-slate-800" : "text-slate-500"}`} />
          <span>Làm mới</span>
        </button>
      </div>

      {/* Queue counts */}
      <div className="queue-stat-grid grid grid-cols-2 items-stretch gap-3 md:grid-cols-4">
        <div className="queue-metric flex flex-col px-4 py-4">
          <span className="queue-stat-icon queue-stat-icon-total"><Inbox className="h-4 w-4" /></span>
          <span className="queue-metric-label block text-[11px] font-medium text-slate-500">Tổng yêu cầu</span>
          <span className="mt-2 block font-mono text-[38px] font-bold leading-none tabular-nums tracking-tight text-slate-950">{stats?.total_tickets ?? data?.total ?? 0}</span>
          <span className="queue-stat-support mb-1 mt-auto block pt-4 text-[10px] font-medium text-slate-500">Cơ cấu mức ưu tiên</span>
          <div
            className="queue-mix"
            role="img"
            aria-label={`Nghiêm trọng: ${stats?.priority_counts?.CRITICAL ?? 0}, Trung bình: ${stats?.priority_counts?.MEDIUM ?? 0}, Thấp: ${stats?.priority_counts?.LOW ?? 0}`}
          >
            <span style={{ flexGrow: stats?.priority_counts?.CRITICAL ?? 0 }} />
            <span style={{ flexGrow: stats?.priority_counts?.MEDIUM ?? 0 }} />
            <span style={{ flexGrow: stats?.priority_counts?.LOW ?? 0 }} />
          </div>
        </div>
        <div className="queue-metric-critical flex min-h-[154px] flex-col justify-between p-4 text-white">
          <div className="flex items-start justify-between">
            <div>
              <span className="queue-metric-label block text-xs font-semibold text-red-100">Cần xử lý ngay</span>
              <span className="mt-1 block text-lg font-semibold tracking-tight">Hàng đợi nghiêm trọng</span>
            </div>
            <span className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-white/25 bg-white/10 shadow-[inset_0_1px_0_rgba(255,255,255,0.25)]">
              <ShieldAlert className="h-5 w-5 text-white" />
            </span>
          </div>
          <div className="flex items-end justify-between gap-3">
            <span className="font-mono text-[54px] font-bold leading-[0.88] tracking-[-0.06em] tabular-nums drop-shadow-sm">
              {stats?.priority_counts?.CRITICAL ?? 0}
            </span>
            <span className="queue-critical-note max-w-36 pb-1 text-right text-xs font-medium leading-5 text-red-100">Cần được xử lý trước</span>
          </div>
        </div>
        <div className="queue-metric flex flex-col px-4 py-4">
          <span className="queue-stat-icon queue-stat-icon-medium"><TriangleAlert className="h-4 w-4" /></span>
          <span className="queue-metric-label block text-[11px] font-medium text-slate-500">Trung bình</span>
          <span className="queue-metric-medium-value mt-2 block font-mono text-[38px] font-bold leading-none tabular-nums tracking-tight">
            {stats?.priority_counts?.MEDIUM ?? 0}
          </span>
          <span className="mt-auto block pt-3 text-[10px] text-slate-500">Điểm từ 30 đến 69</span>
        </div>
        <div className="queue-metric flex flex-col px-4 py-4">
          <span className="queue-stat-icon queue-stat-icon-low"><Circle className="h-4 w-4" /></span>
          <span className="queue-metric-label block text-[11px] font-medium text-slate-500">Thấp</span>
          <span className="queue-metric-low-value mt-2 block font-mono text-[38px] font-bold leading-none tabular-nums tracking-tight">
            {stats?.priority_counts?.LOW ?? 0}
          </span>
          <span className="mt-auto block pt-3 text-[10px] text-slate-500">Điểm dưới 30</span>
        </div>
      </div>

      <div className="queue-control-band">
      <section className="queue-aspect-panel" aria-label="Phân bố khía cạnh của các ticket hiện được tải">
        <div className="queue-aspect-heading">
          <div>
            <h2>Phân bố khía cạnh</h2>
            <p className="queue-aspect-caption">Trong {data?.items.length ?? 0} yêu cầu hiện được tải</p>
          </div>
          <Layers className="h-5 w-5" aria-hidden="true" />
        </div>
        {aspectDistribution.length > 0 ? (
          <div className="queue-aspect-list">
            {aspectDistribution.map(([aspect, count]) => (
              <div className="queue-aspect-item" key={aspect}>
                <div className="queue-aspect-meta">
                  <span>{aspects?.find((item) => item.id === aspect)?.name_vi ?? aspect.replace(/_/g, " ")}</span>
                  <strong>{count}</strong>
                </div>
                <div className="queue-aspect-track" aria-hidden="true">
                  <span style={{ width: `${(count / maxAspectCount) * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="queue-aspect-empty">Chưa có dữ liệu khía cạnh trong danh sách ticket hiện tại.</p>
        )}
      </section>

      {/* Filters Bar */}
      <div className="queue-filter-surface queue-filter-panel flex flex-wrap items-center gap-2 px-3 py-3 sm:px-4">
        <div className="queue-filter-label mr-2 flex items-center gap-2 text-sm font-semibold text-slate-700">
          <Filter className="h-4 w-4 text-slate-500" />
          <span>Bộ lọc:</span>
        </div>

        {/* Trạng thái */}
        <div className="queue-filter-controls">
        <select
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value)}
          aria-label="Lọc theo trạng thái"
          className="queue-filter-select queue-filter-status min-h-9 rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-700 shadow-[inset_0_1px_2px_rgba(20,38,45,0.04)] transition-colors focus:border-[#126B67] focus:outline-none focus:ring-2 focus:ring-[#126B67]/20"
        >
          <option value="">Tất cả trạng thái</option>
          {STATUSES.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>

        {/* Khía cạnh */}
        <select
          value={selectedAspect}
          onChange={(e) => setSelectedAspect(e.target.value)}
          aria-label="Lọc theo khía cạnh"
          className="queue-filter-select queue-filter-aspect min-h-9 max-w-full rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-700 shadow-[inset_0_1px_2px_rgba(20,38,45,0.04)] transition-colors focus:border-[#126B67] focus:outline-none focus:ring-2 focus:ring-[#126B67]/20"
        >
          <option value="">Tất cả khía cạnh</option>
          {aspects?.map((a) => (
            <option key={a.id} value={a.id}>
              {a.name_vi} ({a.id})
            </option>
          ))}
        </select>

        {/* Cảm xúc */}
        <select
          value={selectedSentiment}
          onChange={(e) => setSelectedSentiment(e.target.value)}
          aria-label="Lọc theo cảm xúc"
          className="queue-filter-select queue-filter-sentiment min-h-9 rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-700 shadow-[inset_0_1px_2px_rgba(20,38,45,0.04)] transition-colors focus:border-[#126B67] focus:outline-none focus:ring-2 focus:ring-[#126B67]/20"
        >
          <option value="">Tất cả cảm xúc</option>
          {Object.entries(SENTIMENT_CONFIG).map(([key, cfg]) => (
            <option key={key} value={key}>
              {cfg.label}
            </option>
          ))}
        </select>
        </div>

        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="ml-auto min-h-9 rounded-lg px-3 text-sm font-semibold text-[#126B67] transition-colors hover:bg-[#e7f2f1] hover:text-[#0d514e] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#126B67]"
          >
            Xóa bộ lọc
          </button>
        )}
      </div>
      </div>

      {/* Ticket List Table */}
      <TicketTable tickets={data?.items ?? []} isLoading={isLoading} isFetching={isFetching} />
    </div>
  );
};
