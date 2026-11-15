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
import { AnalyticsPage } from "./AnalyticsPage";
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
    <div data-testid="recharts-piechart">{children}</div>
  ),
  Pie: ({
    data,
    children,
  }: {
    data?: Array<{ name: string; value: number; color: string }>;
    children?: React.ReactNode;
  }) => (
    <div data-testid="recharts-pie" data-slices={JSON.stringify(data ?? [])}>
      {children}
    </div>
  ),
  Cell: ({ fill }: { fill?: string }) => <span data-testid="recharts-cell" data-fill={fill} />,
  BarChart: ({
    data,
    children,
  }: {
    data?: unknown[];
    children?: React.ReactNode;
  }) => (
    <div data-testid="recharts-barchart" data-rows={JSON.stringify(data ?? [])}>
      {children}
    </div>
  ),
  Bar: ({ dataKey, name, fill }: { dataKey?: string; name?: string; fill?: string }) => (
    <span data-testid="recharts-bar" data-key={dataKey} data-name={name} data-fill={fill} />
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

  it("AnalyticsPage renders 4 KPIs, Stacked Bar matrix with name_vi, and preserves Pie colors when zero entries exist", () => {
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
    expect(html).toContain("Chưa đóng");
    expect(html).toContain("Mới: 2 · Đã giao: 1 · Xử lý: 1");
    expect(html).toContain("Tỷ lệ hoàn tất: 33%");
    expect(html).toContain("Ma trận Khía cạnh × Cảm xúc");
    expect(html).toContain("Hoàn tiền &amp; Thanh toán");

    // Neutral (#7c8c91) and Positive (#168a73) must keep their own colors instead of shifting to Negative (#b94342)
    expect(html).toContain('data-fill="#7c8c91"');
    expect(html).toContain('data-fill="#168a73"');
    expect(html).not.toContain('<span data-testid="recharts-cell" data-fill="#b94342"');

    // Priority Pie without CRITICAL must keep MEDIUM (#a66a08) and LOW (#087443)
    expect(html).toContain('data-fill="#a66a08"');
    expect(html).toContain('data-fill="#087443"');
    expect(html).not.toContain('<span data-testid="recharts-cell" data-fill="#a72729"');

    mockedHooks.useStatsOverview.mockReturnValue(makeQuery<StatsOverview>(MOCK_STATS, { isLoading: true }));
    expect(renderInApp(<AnalyticsPage />, "/analytics")).toContain("Đang nạp dữ liệu phân tích thống kê...");
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
