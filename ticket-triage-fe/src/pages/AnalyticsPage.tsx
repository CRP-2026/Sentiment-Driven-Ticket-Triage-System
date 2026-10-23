import React from "react";
import { useStatsOverview, useAspectsStats } from "../api/hooks";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from "recharts";
import { BarChart3, TrendingUp, AlertTriangle } from "lucide-react";

const SENTIMENT_COLORS = ["#EF4444", "#64748B", "#10B981"];
const PRIORITY_COLORS = ["#EF4444", "#F59E0B", "#10B981"];

export const AnalyticsPage: React.FC = () => {
  const { data: stats, isLoading: isStatsLoading } = useStatsOverview();
  const { isLoading: isAspectsLoading } = useAspectsStats();

  if (isStatsLoading || isAspectsLoading) {
    return (
      <div className="p-8 text-center text-slate-500 bg-white rounded-xl border border-slate-200">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent mb-3" />
        <p className="text-sm">Đang nạp dữ liệu phân tích thống kê...</p>
      </div>
    );
  }

  // Chuẩn bị dữ liệu cho biểu đồ Cảm xúc
  const sentimentData = [
    { name: "Tiêu cực", value: stats?.sentiment_counts?.negative ?? 0 },
    { name: "Trung tính", value: stats?.sentiment_counts?.neutral ?? 0 },
    { name: "Tích cực", value: stats?.sentiment_counts?.positive ?? 0 },
  ].filter((d) => d.value > 0);

  // Chuẩn bị dữ liệu cho biểu đồ Mức ưu tiên
  const priorityData = [
    { name: "Cao (Critical)", value: stats?.priority_counts?.CRITICAL ?? 0 },
    { name: "Trung bình", value: stats?.priority_counts?.MEDIUM ?? 0 },
    { name: "Thấp", value: stats?.priority_counts?.LOW ?? 0 },
  ].filter((d) => d.value > 0);

  // Chuẩn bị dữ liệu cho phân bố Khía cạnh
  const aspectDistributionData = Object.entries(stats?.aspect_counts ?? {}).map(
    ([aspect, count]) => ({
      aspect: aspect.replace("_", " "),
      count,
    })
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-blue-600" />
          <span>Bảng phân tích thống kê khía cạnh cảm xúc (Analytics)</span>
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Trực quan hóa ma trận khía cạnh phàn nàn, tỷ lệ phân bố cảm xúc và cấp độ ưu tiên trong hệ thống
        </p>
      </div>

      {/* Grid biểu đồ */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Biểu đồ Cảm xúc tổng thể */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <h3 className="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-blue-500" />
            <span>Phân bố Cảm xúc tổng thể</span>
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
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {sentimentData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={SENTIMENT_COLORS[index % SENTIMENT_COLORS.length]} />
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
            <span>Phân bố Cấp độ ưu tiên (Rule-based)</span>
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
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  >
                    {priorityData.map((_, index) => (
                      <Cell key={`cell-prio-${index}`} fill={PRIORITY_COLORS[index % PRIORITY_COLORS.length]} />
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

      {/* Biểu đồ thanh Khía cạnh phàn nàn */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <h3 className="text-sm font-bold text-slate-800 mb-4">
          Tần suất xuất hiện theo Khía cạnh CSKH (Aspect Distribution)
        </h3>
        <div className="h-72">
          {aspectDistributionData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={aspectDistributionData} margin={{ top: 10, right: 30, left: 0, bottom: 20 }}>
                <XAxis dataKey="aspect" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#3B82F6" radius={[6, 6, 0, 0]} name="Số lượng ticket" />
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
