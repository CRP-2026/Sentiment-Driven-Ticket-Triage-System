import React from "react";
import { QueryClient, QueryClientProvider, UseQueryResult } from "@tanstack/react-query";
import { renderToStaticMarkup } from "react-dom/server";
import { StaticRouter } from "react-router-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as hooks from "../api/hooks";
import {
  AspectMetaItem,
  AspectStatItem,
  HealthResponse,
  StatsOverview,
  TicketListResponse,
} from "../api/schema";
import { Navigation } from "../components/layout/Navigation";
import { MOCK_ASPECTS, MOCK_STATS, MOCK_TICKETS } from "../mocks/tickets";
import { AnalyticsPage, percentageFromCounts } from "./AnalyticsPage";
import { InboxPage } from "./InboxPage";
import { TesterPage } from "./TesterPage";

vi.mock("../api/hooks", () => ({
  useAspects: vi.fn(),
  useAspectsStats: vi.fn(),
  useHealth: vi.fn(),
  useStatsOverview: vi.fn(),
  useTickets: vi.fn(),
  useTriageTicket: vi.fn(),
  useUpdateStatus: vi.fn(),
}));

vi.mock("recharts", () => ({
  ResponsiveContainer: ({ children }: { children?: React.ReactNode }) => (
    <div data-testid="recharts-responsive">{children}</div>
  ),
  PieChart: ({ children }: { children?: React.ReactNode }) => (
    <svg data-testid="recharts-piechart">{children}</svg>
  ),
  Pie: ({
    data,
    children,
  }: {
    data?: Array<{ name: string; value: number }>;
    children?: React.ReactNode;
  }) => (
    <g data-testid="recharts-pie" data-slices={JSON.stringify(data ?? [])}>
      {children}
    </g>
  ),
  Cell: ({ "data-analytics-category": category }: { "data-analytics-category"?: string }) => (
    <path data-testid="recharts-cell" data-category={category} />
  ),
  BarChart: ({
    data,
    children,
    layout,
  }: {
    data?: unknown[];
    children?: React.ReactNode;
    layout?: string;
  }) => (
    <svg data-testid="recharts-barchart" data-rows={JSON.stringify(data ?? [])} data-layout={layout}>
      {children}
    </svg>
  ),
  Bar: ({ dataKey, name, className }: { dataKey?: string; name?: string; className?: string }) => (
    <g data-testid="recharts-bar" data-key={dataKey} data-name={name} data-class={className} />
  ),
  CartesianGrid: () => null,
  Legend: () => null,
  Tooltip: () => null,
  XAxis: () => null,
  YAxis: () => null,
}));

const mockedHooks = vi.mocked(hooks);

function makeQuery<T>(data: T, extra: Partial<UseQueryResult<T, Error>> = {}): UseQueryResult<T, Error> {
  return {
    data,
    isLoading: false,
    isFetching: false,
    isError: false,
    refetch: vi.fn(),
    ...extra,
  } as unknown as UseQueryResult<T, Error>;
}

function renderInApp(node: React.ReactNode, initialEntry = "/"): string {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return renderToStaticMarkup(
    <QueryClientProvider client={queryClient}>
      <StaticRouter location={initialEntry}>{node}</StaticRouter>
    </QueryClientProvider>,
  );
}

describe("FE pages and layout (renderToStaticMarkup)", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    mockedHooks.useAspects.mockReturnValue(makeQuery<AspectMetaItem[]>(MOCK_ASPECTS));
    mockedHooks.useStatsOverview.mockReturnValue(makeQuery<StatsOverview>(MOCK_STATS));
    mockedHooks.useAspectsStats.mockReturnValue(
      makeQuery<AspectStatItem[]>([
        { aspect: "refund_payment", sentiment: "negative", count: 10 },
        { aspect: "refund_payment", sentiment: "positive", count: 2 },
        { aspect: "shipping", sentiment: "neutral", count: 4 },
      ]),
    );
    mockedHooks.useHealth.mockReturnValue(
      makeQuery<HealthResponse>({
        status: "ok",
        version: "0.1.0",
        model_name: "mock",
        is_mock: true,
        model_loaded: true,
        queue_size: 5,
      }),
    );
    mockedHooks.useTickets.mockReturnValue(
      makeQuery<TicketListResponse>({
        items: MOCK_TICKETS,
        total: MOCK_TICKETS.length,
        limit: 50,
        offset: 0,
      }),
    );
    mockedHooks.useTriageTicket.mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
      isError: false,
      submittedAt: 0,
      error: null,
    } as unknown as ReturnType<typeof hooks.useTriageTicket>);
    mockedHooks.useUpdateStatus.mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
      isError: false,
      error: null,
    } as unknown as ReturnType<typeof hooks.useUpdateStatus>);
  });

  it("percentageFromCounts handles empty totals, consistent rounding, and Recharts ratios", () => {
    expect(percentageFromCounts(1, [0])).toBe(0);
    expect(percentageFromCounts(0, [0, 0, 0])).toBe(0);
    expect(percentageFromCounts(2, [6])).toBe(33);
    expect(percentageFromCounts(1, [1, 1, 1], 1 / 3)).toBe(33);
    expect([1, 1, 1].reduce((sum, count) => sum + percentageFromCounts(count, [1, 1, 1]), 0)).toBe(99);
  });

  it("AnalyticsPage renders existing KPI counts, donut summaries, and API-sourced aspect rows", () => {
    mockedHooks.useStatsOverview.mockReturnValue(
      makeQuery<StatsOverview>({
        total_tickets: 6,
        sentiment_counts: { negative: 0, neutral: 4, positive: 2 },
        priority_counts: { CRITICAL: 0, MEDIUM: 4, LOW: 2 },
        status_counts: { new: 2, assigned: 1, in_progress: 1, resolved: 2 },
        aspect_counts: { refund_payment: 4, shipping: 2 },
      }),
    );

    const html = renderInApp(<AnalyticsPage />, "/analytics");

    expect(html).toContain("Tổng số ticket");
    expect(html).toContain("Ưu tiên Nghiêm trọng");
    expect(html).toContain("Ưu tiên Trung bình");
    expect(html).toContain("Ưu tiên Thấp");
    expect(html).not.toContain("Chưa đóng");
    expect(html).not.toContain("Tỷ lệ hoàn tất");
    expect(html).toContain("Khía cạnh khách hàng quan tâm");
    expect(html).toContain("2 chủ đề");
    expect(html).toContain("Hoàn tiền &amp; Thanh toán");
    expect(html).toContain("analytics-donut-summary-percent");
    expect(html).toContain("analytics-pie-center");
    expect(html).toContain("83% tiêu cực");

    // CSS token selectors keep the remaining pie categories tied to their labels after zero slices are filtered.
    expect(html).toContain('<path data-testid="recharts-cell" data-category="Trung tính"');
    expect(html).toContain('<path data-testid="recharts-cell" data-category="Tích cực"');
    expect(html).not.toContain('<path data-testid="recharts-cell" data-category="Tiêu cực"');

    // Priority CSS token selectors remain keyed to labels when CRITICAL is absent.
    expect(html).toContain('<path data-testid="recharts-cell" data-category="Trung bình"');
    expect(html).toContain('<path data-testid="recharts-cell" data-category="Thấp"');
    expect(html).not.toContain('<path data-testid="recharts-cell" data-category="Nghiêm trọng"');
    expect(html).toContain("analytics-aspect-segment-negative");

    mockedHooks.useStatsOverview.mockReturnValue(makeQuery<StatsOverview>(MOCK_STATS, { isLoading: true }));
    expect(renderInApp(<AnalyticsPage />, "/analytics")).toContain("Đang nạp dữ liệu phân tích thống kê...");
  });

  it("AnalyticsPage keeps empty states for zero tickets and zero aspects", () => {
    mockedHooks.useStatsOverview.mockReturnValue(makeQuery<StatsOverview>({
      ...MOCK_STATS,
      total_tickets: 0,
      sentiment_counts: { negative: 0, neutral: 0, positive: 0 },
      priority_counts: { CRITICAL: 0, MEDIUM: 0, LOW: 0 },
      aspect_counts: {},
    }));
    mockedHooks.useAspectsStats.mockReturnValue(makeQuery<AspectStatItem[]>([]));

    const html = renderInApp(<AnalyticsPage />, "/analytics");

    expect(html).toContain("analytics-aspect-count\">0 ");
    expect(html).toContain("analytics-aspect-empty");
    expect(html).toContain("analytics-frequency-card");
    expect(html).not.toContain('data-testid="recharts-piechart"');
  });

  it("AnalyticsPage renders one nonzero category and one API-sourced aspect", () => {
    const oneAspectCount = Object.fromEntries(Object.entries(MOCK_STATS.aspect_counts).slice(0, 1));
    mockedHooks.useStatsOverview.mockReturnValue(makeQuery<StatsOverview>({
      ...MOCK_STATS,
      total_tickets: 1,
      sentiment_counts: { negative: 1, neutral: 0, positive: 0 },
      priority_counts: { CRITICAL: 1, MEDIUM: 0, LOW: 0 },
      aspect_counts: oneAspectCount,
    }));
    mockedHooks.useAspectsStats.mockReturnValue(makeQuery<AspectStatItem[]>([]));

    const html = renderInApp(<AnalyticsPage />, "/analytics");

    expect(html).toContain("analytics-aspect-count\">1 ");
    expect(html.match(/data-testid="recharts-piechart"/g)).toHaveLength(2);
    expect(html.match(/data-testid="recharts-cell"/g)).toHaveLength(2);
  });

  it("TesterPage reflects /health model status badges accurately", () => {
    const mockHtml = renderInApp(<TesterPage />, "/tester");
    expect(mockHtml).toContain("Mô phỏng kiểm thử trực tiếp");
    expect(mockHtml).toContain("Mock");
    expect(mockHtml).toContain("Bị trừ tiền hai lần");

    mockedHooks.useHealth.mockReturnValue(
      makeQuery<HealthResponse>({
        status: "ok",
        version: "0.1.0",
        model_name: "MoritzLaurer/deberta-v3",
        is_mock: false,
        model_loaded: true,
        queue_size: 10,
      }),
    );
    const liveHtml = renderInApp(<TesterPage />, "/tester");
    expect(liveHtml).toContain("MoritzLaurer/deberta-v3");
    expect(liveHtml).toContain("AI thật");

    mockedHooks.useHealth.mockReturnValue(
      makeQuery<HealthResponse>({
        status: "ok",
        version: "0.1.0",
        model_name: "deberta",
        is_mock: false,
        model_loaded: false,
        queue_size: 10,
      }),
    );
    expect(renderInApp(<TesterPage />, "/tester")).toContain("Chưa nạp model");

    mockedHooks.useHealth.mockReturnValue(
      makeQuery<HealthResponse>(undefined as unknown as HealthResponse, { isError: true }),
    );
    const errorHtml = renderInApp(<TesterPage />, "/tester");
    expect(errorHtml).toContain("Không kết nối BE");
    expect(errorHtml).toContain("Mất kết nối");
  });

  it("InboxPage renders pagination controls (>50), fixed clear-filter header button, and server aspect counts", () => {
    mockedHooks.useTickets.mockReturnValue(
      makeQuery<TicketListResponse>({
        items: MOCK_TICKETS,
        total: 86,
        limit: 50,
        offset: 0,
      }),
    );

    const html = renderInApp(<InboxPage />, "/");
    expect(html).toContain("Hộp thư ưu tiên");
    expect(html).toContain("Trên toàn bộ 5 yêu cầu trong hệ thống");
    expect(html).toContain("Hoàn tiền &amp; Thanh toán");
    expect(html).toContain("queue-filter-header");
    expect(html).toMatch(/<button[^>]*disabled=""[^>]*>Xóa bộ lọc<\/button>/);
    expect(html).toContain("Trang 1 / 2");
    expect(html).toContain("86");
    expect(html).toContain('aria-label="Trang trước"');
    expect(html).toContain('aria-label="Trang sau"');
  });

  it("Navigation renders sidebar health states across mock, live, unloaded and offline", () => {
    expect(renderInApp(<Navigation />)).toContain("Chế độ Mock · Hàng đợi: 5");

    mockedHooks.useHealth.mockReturnValue(
      makeQuery<HealthResponse>({
        status: "ok",
        version: "0.1.0",
        model_name: "baseline",
        is_mock: false,
        model_loaded: true,
        queue_size: 3,
      }),
    );
    expect(renderInApp(<Navigation />)).toContain("Trực tuyến · Hàng đợi: 3");

    mockedHooks.useHealth.mockReturnValue(
      makeQuery<HealthResponse>(undefined as unknown as HealthResponse, { isError: true }),
    );
    expect(renderInApp(<Navigation />)).toContain("Mất kết nối máy chủ");
  });
});
