import React, { useState } from "react";
import { useTickets, useAspects, useStatsOverview } from "../api/hooks";
import { TicketTable } from "../components/tickets/TicketTable";
import { STATUSES, SENTIMENT_CONFIG } from "../lib/constants";
import { Filter, RefreshCw, ShieldAlert } from "lucide-react";

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

  return (
    <div className="space-y-6">
      {/* Header and Quick Stats */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Hộp thư phân loại ưu tiên (Triage Inbox)</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Các ticket được sắp xếp tự động theo điểm ưu tiên giảm dần từ cao xuống thấp (Max-Heap + FIFO)
          </p>
        </div>

        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-xs font-medium text-slate-700 shadow-sm transition-all"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? "animate-spin text-blue-600" : "text-slate-500"}`} />
          <span>Làm mới</span>
        </button>
      </div>

      {/* KPI Stats Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-sm">
          <span className="text-xs text-slate-500 block">Tổng số ticket:</span>
          <span className="text-2xl font-bold text-slate-900 font-mono">{stats?.total_tickets ?? data?.total ?? 0}</span>
        </div>
        <div className="bg-white p-3.5 rounded-xl border border-red-200 bg-red-50/30 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs text-red-600 font-medium">Khẩn cấp (CRITICAL):</span>
            <ShieldAlert className="w-4 h-4 text-red-500" />
          </div>
          <span className="text-2xl font-bold text-red-700 font-mono mt-1 block">
            {stats?.priority_counts?.CRITICAL ?? 0}
          </span>
        </div>
        <div className="bg-white p-3.5 rounded-xl border border-amber-200 bg-amber-50/30 shadow-sm">
          <span className="text-xs text-amber-600 font-medium block">Trung bình (MEDIUM):</span>
          <span className="text-2xl font-bold text-amber-700 font-mono mt-1 block">
            {stats?.priority_counts?.MEDIUM ?? 0}
          </span>
        </div>
        <div className="bg-white p-3.5 rounded-xl border border-emerald-200 bg-emerald-50/30 shadow-sm">
          <span className="text-xs text-emerald-600 font-medium block">Thấp (LOW):</span>
          <span className="text-2xl font-bold text-emerald-700 font-mono mt-1 block">
            {stats?.priority_counts?.LOW ?? 0}
          </span>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-700 mr-1">
          <Filter className="w-3.5 h-3.5 text-slate-500" />
          <span>Bộ lọc:</span>
        </div>

        {/* Trạng thái */}
        <select
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value)}
          className="text-xs rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
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
          className="text-xs rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500 capitalize"
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
          className="text-xs rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Tất cả cảm xúc</option>
          {Object.entries(SENTIMENT_CONFIG).map(([key, cfg]) => (
            <option key={key} value={key}>
              {cfg.label}
            </option>
          ))}
        </select>

        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="text-xs text-blue-600 hover:text-blue-800 font-medium ml-auto"
          >
            Xóa bộ lọc
          </button>
        )}
      </div>

      {/* Ticket List Table */}
      <TicketTable tickets={data?.items ?? []} isLoading={isLoading} />
    </div>
  );
};
