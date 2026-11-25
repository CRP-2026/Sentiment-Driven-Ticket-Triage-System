import React from "react";
import { QueryClient, QueryClientProvider, UseQueryResult } from "@tanstack/react-query";
import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as hooks from "../../api/hooks";
import { AspectMetaItem } from "../../api/schema";
import { MOCK_ASPECTS, MOCK_TICKETS } from "../../mocks/tickets";
import { AspectChips } from "./AspectChips";
import { PriorityBadge } from "./PriorityBadge";
import { PriorityBreakdown } from "./PriorityBreakdown";
import { StatusSelect } from "./StatusSelect";
import { TicketTable } from "./TicketTable";

vi.mock("../../api/hooks", () => ({
  useAspects: vi.fn(),
  useUpdateStatus: vi.fn(),
}));

const mockedUseAspects = vi.mocked(hooks.useAspects);
const mockedUseUpdateStatus = vi.mocked(hooks.useUpdateStatus);

type UpdateStatusReturn = ReturnType<typeof hooks.useUpdateStatus>;

function makeQueryResult<T>(data: T): UseQueryResult<T, Error> {
  return { data, isLoading: false, isError: false } as unknown as UseQueryResult<T, Error>;
}

function makeMutationResult(overrides: Partial<UpdateStatusReturn> = {}): UpdateStatusReturn {
  return {
    mutate: vi.fn(),
    isPending: false,
    isError: false,
    error: null,
    ...overrides,
  } as unknown as UpdateStatusReturn;
}

function renderWithQuery(node: React.ReactNode): string {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return renderToStaticMarkup(<QueryClientProvider client={queryClient}>{node}</QueryClientProvider>);
}

describe("ticket components (renderToStaticMarkup)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockedUseAspects.mockReturnValue(makeQueryResult<AspectMetaItem[]>(MOCK_ASPECTS));
    mockedUseUpdateStatus.mockReturnValue(makeMutationResult());
  });

  it("PriorityBadge honors priority_level from API and includes accessible label", () => {
    const html = renderToStaticMarkup(<PriorityBadge score={42.5} level="CRITICAL" />);
    expect(html).toContain("Nghiêm trọng");
    expect(html).toContain("42.5");
    expect(html).toContain('aria-label="Mức ưu tiên: Nghiêm trọng, điểm số 42.5"');

    const fallbackHtml = renderToStaticMarkup(<PriorityBadge score={18.0} />);
    expect(fallbackHtml).toContain("Thấp");
    expect(fallbackHtml).toContain("18.0");
  });

  it("StatusSelect disables invalid FSM options and keeps spinner outside .queue-status-control", () => {
    const html = renderWithQuery(<StatusSelect ticketId={101} currentStatus="new" />);

    expect(html).toMatch(/<option value="new"[^>]*selected=""[^>]*>Mới tiếp nhận<\/option>/);
    expect(html).not.toMatch(/<option value="assigned"[^>]*disabled=""/);
    expect(html).not.toMatch(/<option value="in_progress"[^>]*disabled=""/);
    expect(html).toMatch(/<option value="resolved"[^>]*disabled=""/);
    expect(html).toContain('Không thể chuyển trực tiếp từ &quot;Mới tiếp nhận&quot; sang &quot;Đã giải quyết&quot;');

    mockedUseUpdateStatus.mockReturnValue(makeMutationResult({ isPending: true }));
    const pendingHtml = renderWithQuery(<StatusSelect ticketId={101} currentStatus="assigned" />);
    expect(pendingHtml).toContain('aria-busy="true"');
    const controlEnd = pendingHtml.indexOf("</div><svg");
    expect(controlEnd).toBeGreaterThan(-1);

    mockedUseUpdateStatus.mockReturnValue(
      makeMutationResult({ isError: true, error: new Error("FSM rejected") }),
    );
    const errorHtml = renderWithQuery(<StatusSelect ticketId={101} currentStatus="assigned" />);
    expect(errorHtml).toContain('role="alert"');
    expect(errorHtml).toContain("FSM rejected");
  });

  it("AspectChips sorts negative first, maps name_vi, caps at maxDisplay with +N, and handles empty list", () => {
    const emptyHtml = renderWithQuery(<AspectChips aspects={[]} />);
    expect(emptyHtml).toContain("Chưa phân tích khía cạnh");

    const html = renderWithQuery(
      <AspectChips
        maxDisplay={2}
        aspects={[
          { aspect: "shipping", sentiment: "positive", confidence: 0.91, terms: ["delivery"] },
          { aspect: "general", sentiment: "neutral", confidence: 0.8, terms: ["account"] },
          { aspect: "refund_payment", sentiment: "negative", confidence: 0.95, terms: ["refund"] },
        ]}
      />,
    );

    const idxRefund = html.indexOf("Hoàn tiền &amp; Thanh toán");
    const idxGeneral = html.indexOf("Thắc mắc chung");
    expect(idxRefund).toBeGreaterThan(-1);
    expect(idxGeneral).toBeGreaterThan(idxRefund);
    expect(html).not.toContain("Vận chuyển &amp; Giao hàng");
    expect(html).toContain("+1");
    expect(html).not.toContain('["refund"]');
  });

  it("PriorityBreakdown renders empty state, dominantAspect name_vi, Vietnamese evidence tones and <mark>", () => {
    const emptyHtml = renderWithQuery(<PriorityBreakdown breakdown={null} />);
    expect(emptyHtml).toContain("Chưa có dữ liệu giải trình điểm ưu tiên.");

    const html = renderWithQuery(
      <PriorityBreakdown
        dominantAspect="refund_payment"
        needsManualReview
        breakdown={{
          score: 84.7,
          base: 57.0,
          urgency_bonus: 20.0,
          intensity_bonus: 5.0,
          aspect_bonus: 7.7,
          reasons: [
            "Cảm xúc tổng thể tiêu cực (0.95): base = 57.0",
            "Từ khóa CRITICAL 'charged 5 times' ở câu #1: +20.0",
            "Từ khóa HIGH 'delayed for 3 weeks' ở câu #2: +10.0",
            "Cú pháp câu chứa '!!!' (+5.0)",
            "Khía cạnh nghiêm trọng nhất 'refund_payment': +7.7",
          ],
        }}
      />,
    );

    expect(html).toContain("84.7");
    expect(html).toContain("Cần kiểm tra thủ công");
    expect(html).toContain("Hoàn tiền &amp; Thanh toán");
    expect(html).toContain("audit-evidence-row audit-evidence-sentiment");
    expect(html).toContain("audit-evidence-row audit-evidence-urgency");
    expect(html).toContain("audit-evidence-row audit-evidence-intensity");
    expect(html).toContain("audit-evidence-row audit-evidence-aspect");
    expect(html).toContain('<mark class="audit-evidence-highlight audit-evidence-level-critical">&#x27;charged 5 times&#x27;</mark>');
    expect(html).toContain('<mark class="audit-evidence-highlight audit-evidence-level-high">&#x27;delayed for 3 weeks&#x27;</mark>');
  });

  it("TicketTable renders loading, empty, and row badges cleanly", () => {
    expect(renderWithQuery(<TicketTable tickets={[]} isLoading />)).toContain(
      "Đang tải danh sách hàng đợi ưu tiên...",
    );
    expect(renderWithQuery(<TicketTable tickets={[]} />)).toContain("Không có ticket nào trong hàng đợi");

    const html = renderWithQuery(<TicketTable tickets={MOCK_TICKETS} />);
    expect(html).toContain("#101");
    expect(html).toContain("#105");
    expect(html).toContain("Cần duyệt");
    expect(html).toContain("VI");
    expect(html).toContain("Nghiêm trọng");
  });
});
