import React from "react";
import {
  BarChart,
  Bar,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  type PieLabelRenderProps,
} from "recharts";
import {
  AlertTriangle,
  BarChart3,
  CheckCircle2,
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

export const percentageFromCounts = (
  count: number,
  counts: readonly number[],
  chartRatio?: number,
): number => {
  const total = counts.reduce((sum, value) => sum + value, 0);
  const ratio = chartRatio ?? (total > 0 ? count / total : 0);
  return Math.round(ratio * 100);
};

const AnalyticsPieCallout: React.FC<Partial<PieLabelRenderProps>> = ({
  cx,
  cy,
  name,
  percent,
  innerRadius,
  outerRadius,
  x: labelX,
  y: labelY,
}) => {
  const centerX = Number(cx);
  const centerY = Number(cy);
  const calloutWidth = 76;
  const calloutHeight = 40;
  const radius = Number(outerRadius);
  const directionX = Number(labelX) - centerX;
  const directionY = Number(labelY) - centerY;
  const directionLength = Math.hypot(directionX, directionY) || 1;
  const directionUnitX = directionX / directionLength;
  const directionUnitY = directionY / directionLength;
  const calloutHalfExtent = Math.abs(directionUnitX) * calloutWidth / 2
    + Math.abs(directionUnitY) * calloutHeight / 2;
  const calloutCenterRadius = radius + 8 + calloutHalfExtent;
  const x = centerX + directionUnitX * calloutCenterRadius - calloutWidth / 2;
  const y = centerY + directionUnitY * calloutCenterRadius - calloutHeight / 2;
  const sliceCenterRadius = (Number(innerRadius) + radius) / 2;
  const targetX = centerX + directionUnitX * sliceCenterRadius;
  const targetY = centerY + directionUnitY * sliceCenterRadius;
  const share = percentageFromCounts(0, [], percent);

  return (
    <g
      className="analytics-pie-callout"
      data-analytics-category={String(name ?? "")}
      style={{
        "--analytics-callout-hover-x": `${targetX - (x + calloutWidth / 2)}px`,
        "--analytics-callout-hover-y": `${targetY - (y + calloutHeight / 2)}px`,
      } as React.CSSProperties}
    >
      <foreignObject x={x} y={y} width={calloutWidth} height={calloutHeight}>
        <div className="analytics-pie-callout-card">
          <span className="analytics-pie-callout-value">{share}%</span>
          <span className="analytics-pie-callout-category" title={String(name ?? "")}>{String(name ?? "")}</span>
        </div>
      </foreignObject>
    </g>
  );
};

const AnalyticsFrequencyTick: React.FC<{
  x?: number;
  y?: number;
  payload?: { value?: string | number };
}> = ({ x = 0, y = 0, payload }) => {
  const label = String(payload?.value ?? "");

  return (
    <foreignObject
      className="analytics-frequency-tick"
      x={x}
      y={y + 8}
      width={136}
      height={58}
    >
      <div className="analytics-frequency-tick-label">
        {label}
      </div>
    </foreignObject>
  );
};

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
  const mediumCount = stats?.priority_counts?.MEDIUM ?? 0;
  const lowCount = stats?.priority_counts?.LOW ?? 0;

  const sentimentData = [
    { name: "Tiêu cực", value: stats?.sentiment_counts?.negative ?? 0 },
    { name: "Trung tính", value: stats?.sentiment_counts?.neutral ?? 0 },
    { name: "Tích cực", value: stats?.sentiment_counts?.positive ?? 0 },
  ].filter((d) => d.value > 0);

  const priorityData = [
    { name: "Nghiêm trọng", value: stats?.priority_counts?.CRITICAL ?? 0 },
    { name: "Trung bình", value: stats?.priority_counts?.MEDIUM ?? 0 },
    { name: "Thấp", value: stats?.priority_counts?.LOW ?? 0 },
  ].filter((d) => d.value > 0);

  const aspectDistributionData = Object.entries(stats?.aspect_counts ?? {})
    .map(([aspectId, count]) => ({
      aspect: getAspectDisplayName(aspectId, aspectsMeta),
      count,
    }))
    .sort((a, b) => b.count - a.count);

  const aspectMatrixData = buildAspectSentimentMatrix(aspectStats, aspectsMeta);
  const highlightedAspect = aspectDistributionData[0];
  const highlightedMatrixRow = highlightedAspect
    ? aspectMatrixData.find((row) => row.aspectName === highlightedAspect.aspect)
    : undefined;
  const highlightedNegative = highlightedMatrixRow?.negative ?? 0;
  const highlightedNeutral = highlightedMatrixRow?.neutral ?? 0;
  const highlightedPositive = highlightedMatrixRow?.positive ?? 0;
  const highlightedNegativePercent = percentageFromCounts(
    highlightedNegative,
    [highlightedNegative, highlightedNeutral, highlightedPositive],
  );

  return (
    <div className="inbox-page analytics-page space-y-5 p-4 pb-8 sm:p-5 sm:pb-8 lg:p-6 lg:pb-8">
      <div className="analytics-header flex flex-col gap-4 border-b border-slate-200 pb-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <span className="analytics-kicker mb-1 block text-[11px] font-bold uppercase tracking-[0.15em] text-teal-600">Phân tích vận hành</span>
          <h1 className="flex items-center gap-2 text-[26px] font-semibold tracking-tight text-slate-900">
          <BarChart3 className="analytics-header-icon h-5 w-5" aria-hidden="true" />
          <span className="min-w-0">Phân tích thống kê cảm xúc theo khía cạnh</span>
          </h1>
        <p className="mt-1 max-w-2xl text-sm text-slate-600">
          Trực quan hóa ma trận khía cạnh phàn nàn, tỷ lệ phân bố cảm xúc và cấp độ ưu tiên trong hệ thống
        </p>
        </div>
      </div>

      {/* Thẻ KPI tổng quan */}
      <div className="analytics-kpi-grid grid grid-cols-2 gap-3 xl:grid-cols-4">
        <div className="queue-metric analytics-metric flex flex-col px-4 py-4">
          <span className="queue-stat-icon queue-stat-icon-total"><Inbox className="h-4 w-4" aria-hidden="true" /></span>
          <span className="analytics-kpi-share">{percentageFromCounts(totalTickets, [totalTickets])}%</span>
          <span className="queue-metric-label block pr-9 text-[11px] font-medium text-slate-500">Tổng số ticket</span>
          <span className="mt-2 block font-mono text-[38px] font-bold leading-none tabular-nums tracking-tight text-slate-950">
            {totalTickets}
          </span>
          <span className="analytics-metric-track" aria-hidden="true"><span className="analytics-metric-fill analytics-metric-fill-total" style={{ width: `${percentageFromCounts(totalTickets, [totalTickets])}%` }} /></span>
        </div>

        <div className="queue-metric analytics-metric flex flex-col px-4 py-4">
          <span className="queue-stat-icon queue-stat-icon-critical"><ShieldAlert className="h-4 w-4" aria-hidden="true" /></span>
          <span className="analytics-kpi-share analytics-kpi-share-critical">{percentageFromCounts(criticalCount, [totalTickets])}%</span>
          <span className="queue-metric-label block pr-9 text-[11px] font-medium text-slate-500">Ưu tiên Nghiêm trọng</span>
          <span className="queue-metric-critical-value mt-2 block font-mono text-[38px] font-bold leading-none tabular-nums tracking-tight">
            {criticalCount}
          </span>
          <span className="analytics-metric-track" aria-hidden="true"><span className="analytics-metric-fill analytics-metric-fill-critical" style={{ width: `${percentageFromCounts(criticalCount, [totalTickets])}%` }} /></span>
        </div>

        <div className="queue-metric analytics-metric flex flex-col px-4 py-4">
          <span className="queue-stat-icon queue-stat-icon-medium"><AlertTriangle className="h-4 w-4" aria-hidden="true" /></span>
          <span className="analytics-kpi-share analytics-kpi-share-medium">{percentageFromCounts(mediumCount, [totalTickets])}%</span>
          <span className="queue-metric-label block pr-9 text-[11px] font-medium text-slate-500">Ưu tiên Trung bình</span>
          <span className="queue-metric-medium-value mt-2 block font-mono font-bold leading-none tabular-nums tracking-tight">
            {mediumCount}
          </span>
          <span className="analytics-metric-track" aria-hidden="true"><span className="analytics-metric-fill analytics-metric-fill-medium" style={{ width: `${percentageFromCounts(mediumCount, [totalTickets])}%` }} /></span>
        </div>

        <div className="queue-metric analytics-metric flex flex-col px-4 py-4">
          <span className="queue-stat-icon queue-stat-icon-low"><CheckCircle2 className="h-4 w-4" aria-hidden="true" /></span>
          <span className="analytics-kpi-share analytics-kpi-share-low">{percentageFromCounts(lowCount, [totalTickets])}%</span>
          <span className="queue-metric-label block pr-9 text-[11px] font-medium text-slate-500">Ưu tiên Thấp</span>
          <span className="queue-metric-low-value mt-2 block font-mono text-[38px] font-bold leading-none tabular-nums tracking-tight">
            {lowCount}
          </span>
          <span className="analytics-metric-track" aria-hidden="true"><span className="analytics-metric-fill analytics-metric-fill-low" style={{ width: `${percentageFromCounts(lowCount, [totalTickets])}%` }} /></span>
        </div>
      </div>

      {/* Grid biểu đồ tròn */}
      <div className="analytics-pie-grid grid grid-cols-1 gap-6 md:grid-cols-2">
        {/* Biểu đồ Cảm xúc tổng thể */}
        <div className="analytics-chart-card analytics-donut-card bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <h3 className="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2">
            <TrendingUp className="analytics-sentiment-heading-icon h-4 w-4" />
            <span>Phân bố cảm xúc tổng thể</span>
          </h3>
          <div className="analytics-pie-stage h-64">
            {sentimentData.length > 0 ? (
              <>
              <div className="analytics-donut-content">
              <div className="analytics-donut-plot">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <defs>
                    <linearGradient id="analytics-sentiment-critical-gradient" x1="0" y1="0" x2="1" y2="1">
                      <stop className="analytics-gradient-critical-soft" offset="0%" />
                      <stop className="analytics-gradient-critical" offset="100%" />
                    </linearGradient>
                    <linearGradient id="analytics-sentiment-neutral-gradient" x1="0" y1="0" x2="1" y2="1">
                      <stop className="analytics-gradient-neutral-soft" offset="0%" />
                      <stop className="analytics-gradient-neutral" offset="100%" />
                    </linearGradient>
                    <linearGradient id="analytics-sentiment-positive-gradient" x1="0" y1="0" x2="1" y2="1">
                      <stop className="analytics-gradient-teal-soft" offset="0%" />
                      <stop className="analytics-gradient-teal" offset="100%" />
                    </linearGradient>
                  </defs>
                  <Pie
                    data={sentimentData}
                    cx="50%"
                    cy="50%"
                    innerRadius={38}
                    outerRadius={60}
                    cornerRadius={8}
                    paddingAngle={3}
                    dataKey="value"
                    isAnimationActive={false}
                    label={<AnalyticsPieCallout />}
                    labelLine={false}
                  >
                    {sentimentData.map((entry) => (
                      <Cell
                        key={`cell-${entry.name}`}
                        data-analytics-category={entry.name}
                      />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
              <div className="analytics-pie-center" aria-label={`Tổng số ticket: ${totalTickets}`}>
                <span>{totalTickets}</span>
              </div>
              </div>
              <ul className="analytics-donut-summary">
                {sentimentData.map((entry) => (
                  <li key={`sentiment-summary-${entry.name}`} className="analytics-donut-summary-item" data-analytics-category={entry.name}>
                    <span className="analytics-donut-summary-swatch" aria-hidden="true" />
                    <span className="analytics-donut-summary-name" title={entry.name}>{entry.name}</span>
                    <span className="analytics-donut-summary-count">{entry.value}</span>
                    <span className="analytics-donut-summary-percent">{percentageFromCounts(entry.value, sentimentData.map((item) => item.value))}%</span>
                  </li>
                ))}
              </ul>
              </div>
              <div className="analytics-donut-legend" aria-label="Chú giải cảm xúc">
                {sentimentData.map((entry) => (
                  <span key={`sentiment-legend-${entry.name}`} data-analytics-category={entry.name}>{entry.name}</span>
                ))}
              </div>
              </>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">
                Chưa có dữ liệu cảm xúc
              </div>
            )}
          </div>
        </div>

        {/* Biểu đồ Cấp độ ưu tiên */}
        <div className="analytics-chart-card analytics-donut-card bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <h3 className="text-sm font-bold text-slate-800 mb-4 flex items-center gap-2">
            <AlertTriangle className="analytics-priority-heading-icon h-4 w-4" />
            <span>Phân bố mức độ ưu tiên</span>
          </h3>
          <div className="analytics-pie-stage h-64">
            {priorityData.length > 0 ? (
              <>
              <div className="analytics-donut-content">
              <div className="analytics-donut-plot">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <defs>
                    <linearGradient id="analytics-priority-critical-gradient" x1="0" y1="0" x2="1" y2="1">
                      <stop className="analytics-gradient-critical-soft" offset="0%" />
                      <stop className="analytics-gradient-critical" offset="100%" />
                    </linearGradient>
                    <linearGradient id="analytics-priority-medium-gradient" x1="0" y1="0" x2="1" y2="1">
                      <stop className="analytics-gradient-medium-soft" offset="0%" />
                      <stop className="analytics-gradient-medium" offset="100%" />
                    </linearGradient>
                    <linearGradient id="analytics-priority-low-gradient" x1="0" y1="0" x2="1" y2="1">
                      <stop className="analytics-gradient-low-soft" offset="0%" />
                      <stop className="analytics-gradient-low" offset="100%" />
                    </linearGradient>
                  </defs>
                  <Pie
                    data={priorityData}
                    cx="50%"
                    cy="50%"
                    innerRadius={38}
                    outerRadius={60}
                    cornerRadius={8}
                    paddingAngle={3}
                    dataKey="value"
                    isAnimationActive={false}
                    label={<AnalyticsPieCallout />}
                    labelLine={false}
                  >
                    {priorityData.map((entry) => (
                      <Cell
                        key={`cell-prio-${entry.name}`}
                        data-analytics-category={entry.name}
                      />
                    ))}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
              <div className="analytics-pie-center" aria-label={`Tổng số ticket: ${totalTickets}`}>
                <span>{totalTickets}</span>
              </div>
              </div>
              <ul className="analytics-donut-summary">
                {priorityData.map((entry) => (
                  <li key={`priority-summary-${entry.name}`} className="analytics-donut-summary-item" data-analytics-category={entry.name}>
                    <span className="analytics-donut-summary-swatch" aria-hidden="true" />
                    <span className="analytics-donut-summary-name" title={entry.name}>{entry.name}</span>
                    <span className="analytics-donut-summary-count">{entry.value}</span>
                    <span className="analytics-donut-summary-percent">{percentageFromCounts(entry.value, priorityData.map((item) => item.value))}%</span>
                  </li>
                ))}
              </ul>
              </div>
              <div className="analytics-donut-legend" aria-label="Chú giải mức độ ưu tiên">
                {priorityData.map((entry) => (
                  <span key={`priority-legend-${entry.name}`} data-analytics-category={entry.name}>{entry.name}</span>
                ))}
              </div>
              </>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">
                Chưa có dữ liệu mức ưu tiên
              </div>
            )}
          </div>
        </div>
      </div>

      <section className="analytics-aspect-card analytics-chart-card bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <div className="analytics-aspect-heading">
          <div>
            <h3 className="flex items-center gap-2">
              <Layers className="analytics-aspect-heading-icon h-4 w-4" aria-hidden="true" />
              <span>Khía cạnh khách hàng quan tâm</span>
            </h3>
            <p className="analytics-aspect-description">Tương quan số lượt phản hồi tiêu cực, trung tính và tích cực trên từng khía cạnh</p>
          </div>
          <span className="analytics-aspect-count">{aspectDistributionData.length} chủ đề</span>
        </div>

        {highlightedAspect ? (
          <div className="analytics-aspect-overview">
            <article className="analytics-aspect-highlight">
              <span className="analytics-aspect-highlight-icon"><TrendingUp className="h-4 w-4" aria-hidden="true" /></span>
              <span className="analytics-aspect-eyebrow">Được nhắc nhiều nhất</span>
              <strong className="analytics-aspect-highlight-count">{highlightedAspect.count}</strong>
              <span className="analytics-aspect-highlight-unit">lượt nhắc</span>
              <span className="analytics-aspect-highlight-name" title={highlightedAspect.aspect}>{highlightedAspect.aspect}</span>
              <span className="analytics-aspect-highlight-ratio">{highlightedNegative} / {highlightedMatrixRow?.total ?? 0}</span>
              <div className="analytics-aspect-negative-track" aria-hidden="true">
                <span style={{ width: `${highlightedNegativePercent}%` }} />
              </div>
              <span className="analytics-aspect-negative-label">{highlightedNegativePercent}% tiêu cực</span>
            </article>

            <div className="analytics-aspect-table-wrap">
              <div className="analytics-aspect-table-header" aria-hidden="true">
                <span>Chủ đề</span>
                <span>Phân bố cảm xúc</span>
                <span>Lượt</span>
              </div>
              <div className="analytics-aspect-rows">
                {aspectDistributionData.slice(1).map((aspect, index) => {
                  const matrixRow = aspectMatrixData.find((row) => row.aspectName === aspect.aspect);
                  const negative = matrixRow?.negative ?? 0;
                  const neutral = matrixRow?.neutral ?? 0;
                  const positive = matrixRow?.positive ?? 0;
                  const matrixCounts = [negative, neutral, positive];
                  const negativePercent = percentageFromCounts(negative, matrixCounts);

                  return (
                    <div className="analytics-aspect-row" key={aspect.aspect}>
                      <span className="analytics-aspect-rank">{String(index + 2).padStart(2, "0")}</span>
                      <span className="analytics-aspect-row-name" title={aspect.aspect}>{aspect.aspect}</span>
                      <span className="analytics-aspect-row-percent">{negativePercent}% tiêu cực</span>
                      <div className="analytics-aspect-segment-track" aria-hidden="true">
                        <span className="analytics-aspect-segment analytics-aspect-segment-negative" style={{ width: `${percentageFromCounts(negative, matrixCounts)}%` }} />
                        <span className="analytics-aspect-segment analytics-aspect-segment-neutral" style={{ width: `${percentageFromCounts(neutral, matrixCounts)}%` }} />
                        <span className="analytics-aspect-segment analytics-aspect-segment-positive" style={{ width: `${percentageFromCounts(positive, matrixCounts)}%` }} />
                      </div>
                      <span className="analytics-aspect-row-total">{aspect.count}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        ) : (
          <div className="analytics-aspect-empty">Chưa có dữ liệu ma trận khía cạnh × cảm xúc</div>
        )}

        <div className="analytics-aspect-footer">
          <div className="analytics-aspect-legend">
            <span data-analytics-category="Tiêu cực">Tiêu cực</span>
            <span data-analytics-category="Trung tính">Trung tính</span>
            <span data-analytics-category="Tích cực">Tích cực</span>
          </div>
          <span className="analytics-aspect-note">Một ticket có thể đề cập nhiều chủ đề</span>
        </div>
      </section>

      <div className="analytics-chart-card analytics-frequency-card bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
        <h3 className="analytics-frequency-title text-sm font-bold text-slate-800 mb-4">
          <span className="analytics-frequency-icon" aria-hidden="true"><BarChart3 className="h-4 w-4" /></span>
          Tần suất xuất hiện theo khía cạnh chăm sóc khách hàng
        </h3>
        <div className="analytics-aspect-frequency-stage h-72">
          {aspectDistributionData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={aspectDistributionData} margin={{ top: 12, right: 12, left: 0, bottom: 22 }}>
                  <defs>
                    <linearGradient id="analytics-aspect-bar-gradient" x1="0" y1="1" x2="0" y2="0">
                      <stop className="analytics-gradient-teal-soft" offset="0%" />
                      <stop className="analytics-gradient-teal" offset="100%" />
                    </linearGradient>
                  </defs>
                  <CartesianGrid className="analytics-chart-grid" strokeDasharray="3 3" vertical={false} />
                <XAxis
                  dataKey="aspect"
                  tick={<AnalyticsFrequencyTick />}
                  height={72}
                  interval={0}
                  tickMargin={8}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis allowDecimals={false} axisLine={false} tickLine={false} tick={{ fontSize: 10, fontWeight: 500 }} />
                <Tooltip wrapperClassName="analytics-chart-tooltip" />
                <Bar
                  dataKey="count"
                  className="analytics-aspect-bars"
                  radius={[10, 10, 3, 3]}
                  maxBarSize={68}
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
