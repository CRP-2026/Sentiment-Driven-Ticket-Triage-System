import { afterEach, describe, expect, it, vi } from "vitest";
import { MOCK_ASPECTS, MOCK_STATS, MOCK_TICKETS } from "../mocks/tickets";
import { ApiError, api } from "./client";
import { queryKeys } from "./queryKeys";

describe("api client, queryKeys and mocks", () => {
  const originalFetch = globalThis.fetch;

  afterEach(() => {
    globalThis.fetch = originalFetch;
    vi.restoreAllMocks();
  });

  it("defines structured query keys matching endpoint scopes", () => {
    expect(queryKeys.health).toEqual(["health"]);
    expect(queryKeys.aspects).toEqual(["meta", "aspects"]);
    expect(queryKeys.stats.overview).toEqual(["stats", "overview"]);
    expect(queryKeys.stats.aspects).toEqual(["stats", "aspects"]);
    expect(queryKeys.tickets.list({ status: "new", offset: 50, limit: 50 })).toEqual([
      "tickets",
      "list",
      { status: "new", offset: 50, limit: 50 },
    ]);
    expect(queryKeys.tickets.detail(42)).toEqual(["tickets", "detail", 42]);
  });

  it("prefixes /api/v1 on api.get/post/patch and wraps backend errors in ApiError", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url === "/api/v1/health") {
        return new Response(JSON.stringify({ status: "ok" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        });
      }
      return new Response(JSON.stringify({ detail: "Chuyển trạng thái không hợp lệ", code: "FSM_ERR" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    });
    globalThis.fetch = fetchMock as typeof globalThis.fetch;

    const ok = await api.get<{ status: string }>("/health");
    expect(ok).toEqual({ status: "ok" });
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/health",
      expect.objectContaining({ headers: { "Content-Type": "application/json" } }),
    );

    await expect(api.patch("/tickets/1/status", { status: "resolved" })).rejects.toMatchObject({
      name: "ApiError",
      status: 400,
      detail: "Chuyển trạng thái không hợp lệ",
      code: "FSM_ERR",
    });

    globalThis.fetch = vi.fn(
      async () => new Response("Internal Error", { status: 500 }),
    ) as typeof globalThis.fetch;

    await expect(api.post("/tickets", { content: "test" })).rejects.toThrow(ApiError);
  });

  it("keeps MOCK_TICKETS scores and MOCK_STATS mathematically consistent", () => {
    const t103 = MOCK_TICKETS.find((t) => t.id === 103);
    expect(t103).toBeDefined();
    expect(t103?.confidence).toBe(0.8);
    expect(t103?.priority_breakdown?.base).toBe(48.0);
    expect(t103?.priority_breakdown?.score).toBe(54.8);

    expect(MOCK_ASPECTS.map((a) => a.id)).toEqual([
      "customer_service",
      "refund_payment",
      "product_quality",
      "shipping",
      "general",
    ]);
    expect(MOCK_STATS.total_tickets).toBe(MOCK_TICKETS.length);
  });
});
