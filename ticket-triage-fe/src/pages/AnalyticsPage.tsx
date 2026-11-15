import React from "react";
import {
  BarChart,
  Bar,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  Clock,
  Inbox,
  Layers,
  ShieldAlert,
  TrendingUp,
} from "lucide-react";
import { useAspects, useAspectsStats, useStatsOverview } from "../api/hooks";
import {
  buildAspectSentimentMatrix,
  getAspectDisplayName,
} from "../lib/ticketHelpers";

export const AnalyticsPage: React.FC = () => {
  const { data: stats, isLoading: isStatsLoading } = useStatsOverview();
  const { data: aspectStats, isLoading: isAspectsLoading } = useAspectsStats();
  const { data: aspectsMeta, isLoading: isMetaLoading } = useAspects();

  if (isStatsLoading || isAspectsLoading || isMetaLoading) {
    return (
      <div className="p-8 text-center text-slate-500 bg-white rounded-xl border border-slate-200">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent mb-3" />
        <p className="text-sm">Đang nạp dữ liệu phân tích thống kê...</p>
      </div>
    );
  }

  const totalTickets = stats?.total_tickets ?? 0;
  const criticalCount = stats?.priority_counts?.CRITICAL ?? 0;
  const criticalPct = totalTickets > 0 ? Math.round((criticalCount / totalTickets) * 100) : 0;
  const newCount = stats?.status_counts?.new ?? 0;
  const assignedCount = stats?.status_counts?.assigned ?? 0;
  const inProgressCount = stats?.status_counts?.in_progress ?? 0;
  const openCount = newCount + assignedCount + inProgressCount;
  const resolvedCount = stats?.status_counts?.resolved ?? 0;
  const resolvedPct = totalTickets > 0 ? Math.round((resolvedCount / totalTickets) * 100) : 0;

  const sentimentData = [
    { name: "Tiêu cực", value: stats?.sentiment_counts?.negative ?? 0, color: "#b94342" },
    { name: "Trung tính", value: stats?.sentiment_counts?.neutral ?? 0, color: "#7c8c91" },
    { name: "Tích cực", value: stats?.sentiment_counts?.positive ?? 0, color: "#168a73" },
  ].filter((d) => d.value > 0);

  const priorityData = [
    { name: "Nghiêm trọng", value: stats?.priority_counts?.CRITICAL ?? 0, color: "#a72729" },
    { name: "Trung bình", value: stats?.priority_counts?.MEDIUM ?? 0, color: "#a66a08" },
    { name: "Thấp", value: stats?.priority_counts?.LOW ?? 0, color: "#087443" },
  ].filter((d) => d.value > 0);

  const aspectDistributionData = Object.entries(stats?.aspect_counts ?? {})
    .map(([aspectId, count]) => ({
      aspect: getAspectDisplayName(aspectId, aspectsMeta),
      count,
    }))
    .sort((a, b) => b.count - a.count);

  const aspectMatrixData = buildAspectSentimentMatrix(aspectStats, aspectsMeta);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-blue-600" />
          <span>Phân tích thống kê cảm xúc theo khía cạnh</span>
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Trực quan hóa ma trận khía cạnh phàn nàn, tỷ lệ phân bố cảm xúc và cấp độ ưu tiên trong hệ thống
        </p>
      </div>

      {/* Thẻ KPI tổng quan */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
            <span>Tổng số ticket</span>
            <Inbox className="w-4 h-4 text-[#126B67]" aria-hidden="true" />
          </div>
          <p className="mt-2 font-mono text-2xl font-bold tabular-nums text-slate-900">
            {totalTickets}
          </p>
          <p className="mt-1 text-[11px] text-slate-500">Toàn bộ yêu cầu đã tiếp nhận</p>
        </div>

        <div className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
            <span>Ưu tiên Nghiêm trọng</span>
            <ShieldAlert className="w-4 h-4 text-[#a72729]" aria-hidden="true" />
          </div>
          <p className="mt-2 font-mono text-2xl font-bold tabular-nums text-[#a72729]">
            {criticalCount}
          </p>
          <p className="mt-1 text-[11px] text-slate-500">
            Chiếm {criticalPct}% tổng hàng đợi
          </p>
        </div>

        <div className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
            <span>Chưa đóng</span>
            <Clock className="w-4 h-4 text-[#a66a08]" aria-hidden="true" />
          </div>
          <p className="mt-2 font-mono text-2xl font-bold tabular-nums text-slate-900">
            {openCount}
          </p>
          <p className="mt-1 text-[11px] text-slate-500">
            Mới: {newCount} · Đã giao: {assignedCount} · Xử lý: {inProgressCount}
          </p>
        </div>

        <div className="bg-white p-4 sm:p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-500">
            <span>Đã giải quyết</span>
            <CheckCircle2 className="w-4 h-4 text-[#087443]" aria-hidden="true" />
          </div>
          <p className="mt-2 font-mono text-2xl font-bold tabular-nums text-[#087443]">
            {resolvedCount}
          </p>
          <p className="mt-1 text-[11px] text-slate-500">
            Tỷ lệ hoàn tất: {resolvedPct}%
          </p>
        </div>
      </div>

      {/* Grid biểu đồ tròn */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Biểu đồ Cảm xúc tổng thể */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <h3 className="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-blue-500" />
            <span>Phân bố cảm xúc tổng thể</span>
          </h3>
          <div className="h-64">
            {sentimentData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={sentimentData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    isAnimationActive={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {sentimentData.map((entry) => (
                      <Cell key={`cell-${entry.name}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">
                Chưa có dữ liệu cảm xúc
              </div>
            )}
          </div>
        </div>

        {/* Biểu đồ Cấp độ ưu tiên */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <h3 className="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-500" />
            <span>Phân bố mức độ ưu tiên</span>
          </h3>
          <div className="h-64">
            {priorityData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={priorityData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    isAnimationActive={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {priorityData.map((entry) => (
                      <Cell key={`cell-prio-${entry.name}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">
                Chưa có dữ liệu mức ưu tiên
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Ma trận Khía cạnh x Cảm xúc (Stacked Bar Chart) */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <h3 className="text-sm font-bold text-slate-800 mb-1 flex items-center gap-2">
          <Layers className="w-4 h-4 text-[#126B67]" />
          <span>Ma trận Khía cạnh × Cảm xúc</span>
        </h3>
        <p className="text-xs text-slate-500 mb-4">
          Tương quan số lượt phản hồi tiêu cực, trung tính và tích cực trên từng khía cạnh
        </p>
        <div className="h-72">
          {aspectMatrixData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={aspectMatrixData} margin={{ top: 10, right: 30, left: 0, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="aspectName" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Legend />
                <Bar
                  dataKey="negative"
                  stackId="sentiment"
                  fill="#b94342"
                  name="Tiêu cực"
                  isAnimationActive={false}
                />
                <Bar
                  dataKey="neutral"
                  stackId="sentiment"
                  fill="#7c8c91"
                  name="Trung tính"
                  isAnimationActive={false}
                />
                <Bar
                  dataKey="positive"
                  stackId="sentiment"
                  fill="#168a73"
                  name="Tích cực"
                  isAnimationActive={false}
                />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-xs text-slate-400">
              Chưa có dữ liệu ma trận khía cạnh × cảm xúc
            </div>
          )}
        </div>
      </div>

      {/* Biểu đồ thanh Khía cạnh phàn nàn */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <h3 className="text-sm font-bold text-slate-800 mb-4">
          Tần suất xuất hiện theo khía cạnh chăm sóc khách hàng
        </h3>
        <div className="h-72">
          {aspectDistributionData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={aspectDistributionData} margin={{ top: 10, right: 30, left: 0, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="aspect" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar
                  dataKey="count"
                  fill="#126B67"
                  radius={[6, 6, 0, 0]}
                  name="Số lượng ticket"
                  isAnimationActive={false}
                />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-xs text-slate-400">
              Chưa có dữ liệu khía cạnh
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
