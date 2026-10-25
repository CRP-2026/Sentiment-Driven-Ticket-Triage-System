import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "./client";
import { queryKeys } from "./queryKeys";
import {
  TicketOut,
  TicketListResponse,
  TicketCreateIn,
  StatusUpdateIn,
  AspectMetaItem,
  StatsOverview,
} from "./schema";
import { POLL_QUEUE_MS, POLL_STATS_MS } from "../lib/constants";
import { MOCK_TICKETS, MOCK_ASPECTS, MOCK_STATS } from "../mocks/tickets";

const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

export function useTickets(filters: {
  status?: string;
  aspect?: string;
  sentiment?: string;
  limit?: number;
  offset?: number;
}) {
  return useQuery<TicketListResponse>({
    queryKey: queryKeys.tickets.list(filters),
    queryFn: async () => {
      if (USE_MOCK) {
        let items = [...MOCK_TICKETS];
        if (filters.status) items = items.filter((t) => t.status === filters.status);
        if (filters.aspect) items = items.filter((t) => t.aspects.some((a) => a.aspect === filters.aspect));
        if (filters.sentiment) items = items.filter((t) => t.sentiment_label === filters.sentiment);
        return { items, total: items.length, limit: filters.limit ?? 50, offset: filters.offset ?? 0 };
      }

      const params = new URLSearchParams();
      if (filters.limit) params.set("limit", filters.limit.toString());
      if (filters.offset) params.set("offset", filters.offset.toString());
      if (filters.status) params.set("status", filters.status);
      if (filters.aspect) params.set("aspect", filters.aspect);
      if (filters.sentiment) params.set("sentiment", filters.sentiment);

      return api.get<TicketListResponse>(`/tickets?${params.toString()}`);
    },
    refetchInterval: POLL_QUEUE_MS,
    staleTime: 2_000,
  });
}

export function useTicketDetail(id: number | null) {
  return useQuery<TicketOut>({
    queryKey: queryKeys.tickets.detail(id ?? 0),
    queryFn: async () => {
      if (USE_MOCK) {
        const found = MOCK_TICKETS.find((t) => t.id === id);
        if (!found) throw new Error("Ticket not found in mock");
        return found;
      }
      return api.get<TicketOut>(`/tickets/${id}`);
    },
    enabled: Boolean(id),
  });
}

export function useAspects() {
  return useQuery<AspectMetaItem[]>({
    queryKey: queryKeys.aspects,
    queryFn: async () => {
      if (USE_MOCK) return MOCK_ASPECTS;
      return api.get<AspectMetaItem[]>("/meta/aspects");
    },
    staleTime: 60_000 * 5, // 5 mins
  });
}

export function useStatsOverview() {
  return useQuery<StatsOverview>({
    queryKey: queryKeys.stats.overview,
    queryFn: async () => {
      if (USE_MOCK) return MOCK_STATS;
      return api.get<StatsOverview>("/stats/overview");
    },
    refetchInterval: POLL_STATS_MS,
  });
}

export function useAspectsStats() {
  return useQuery<Array<{ aspect: string; sentiment: string; count: number }>>({
    queryKey: queryKeys.stats.aspects,
    queryFn: async () => {
      if (USE_MOCK) {
        return [
          { aspect: "customer_service", sentiment: "negative", count: 12 },
          { aspect: "refund_payment", sentiment: "negative", count: 18 },
          { aspect: "product_quality", sentiment: "negative", count: 14 },
          { aspect: "shipping", sentiment: "negative", count: 16 },
          { aspect: "general", sentiment: "neutral", count: 20 },
        ];
      }
      return api.get<Array<{ aspect: string; sentiment: string; count: number }>>("/stats/aspects");
    },
    refetchInterval: POLL_STATS_MS,
  });
}

export function useTriageTicket() {
  const queryClient = useQueryClient();
  return useMutation<TicketOut, Error, TicketCreateIn>({
    mutationFn: async (payload) => {
      if (USE_MOCK) {
        const newTicket: TicketOut = {
          id: Date.now(),
          content: payload.content,
          language_flag: "en",
          needs_manual_review: false,
          sentiment_label: "negative",
          confidence: 0.92,
          low_confidence: false,
          priority_score: 82.5,
          priority_level: "CRITICAL",
          dominant_aspect: "refund_payment",
          priority_breakdown: {
            score: 82.5,
            base: 55.2,
            urgency_bonus: 20.0,
            intensity_bonus: 0.0,
            aspect_bonus: 7.3,
            reasons: ["Base score: 55.2", "Urgent keyword: +20.0"],
          },
          status: "new",
          aspects: [{ aspect: "refund_payment", sentiment: "negative", confidence: 0.92 }],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
        MOCK_TICKETS.unshift(newTicket);
        return newTicket;
      }
      return api.post<TicketOut>("/tickets", payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tickets.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.stats.overview });
    },
  });
}

export function useUpdateStatus() {
  const queryClient = useQueryClient();
  return useMutation<TicketOut, Error, { id: number; payload: StatusUpdateIn }>({
    mutationFn: async ({ id, payload }) => {
      if (USE_MOCK) {
        const t = MOCK_TICKETS.find((item) => item.id === id);
        if (t) {
          t.status = payload.status;
          if (payload.assigned_to !== undefined) t.assigned_to = payload.assigned_to;
          t.updated_at = new Date().toISOString();
        }
        return t!;
      }
      return api.patch<TicketOut>(`/tickets/${id}/status`, payload);
    },
    onSuccess: (_, vars) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tickets.detail(vars.id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.tickets.all });
      queryClient.invalidateQueries({ queryKey: queryKeys.stats.overview });
    },
  });
}
