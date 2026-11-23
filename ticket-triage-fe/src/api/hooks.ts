import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "./client";
import { queryKeys } from "./queryKeys";
import {
  TicketOut,
  TicketListResponse,
  TicketCreateIn,
  StatusUpdateIn,
  AspectMetaItem,
  AspectStatItem,
  HealthResponse,
  StatsOverview,
} from "./schema";
import { POLL_HEALTH_MS, POLL_QUEUE_MS, POLL_STATS_MS } from "../lib/constants";
import { MOCK_TICKETS, MOCK_ASPECTS, MOCK_STATS } from "../mocks/tickets";

const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

const TICKETS_LIST_QUERY_PREFIX = ["tickets", "list"] as const;

const MOCK_ASPECT_STATS: AspectStatItem[] = [
  { aspect: "customer_service", sentiment: "negative", count: 12 },
  { aspect: "customer_service", sentiment: "neutral", count: 4 },
  { aspect: "customer_service", sentiment: "positive", count: 3 },
  { aspect: "refund_payment", sentiment: "negative", count: 18 },
  { aspect: "refund_payment", sentiment: "neutral", count: 3 },
  { aspect: "refund_payment", sentiment: "positive", count: 1 },
  { aspect: "product_quality", sentiment: "negative", count: 14 },
  { aspect: "product_quality", sentiment: "neutral", count: 5 },
  { aspect: "product_quality", sentiment: "positive", count: 4 },
  { aspect: "shipping", sentiment: "negative", count: 16 },
  { aspect: "shipping", sentiment: "neutral", count: 6 },
  { aspect: "shipping", sentiment: "positive", count: 2 },
  { aspect: "general", sentiment: "negative", count: 3 },
  { aspect: "general", sentiment: "neutral", count: 20 },
  { aspect: "general", sentiment: "positive", count: 8 },
];

type UpdateStatusContext = {
  previousLists: Array<[readonly unknown[], TicketListResponse | undefined]>;
  previousDetail: TicketOut | undefined;
};

export function useHealth() {
  return useQuery<HealthResponse>({
    queryKey: queryKeys.health,
    queryFn: async () => {
      if (USE_MOCK) {
        return {
          status: "ok",
          version: "0.1.0",
          model_name: "mock",
          is_mock: true,
          model_loaded: true,
          queue_size: MOCK_TICKETS.filter((t) => t.status !== "resolved").length,
        };
      }
      return api.get<HealthResponse>("/health");
    },
    refetchInterval: POLL_HEALTH_MS,
  });
}

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
        const limit = filters.limit ?? 50;
        const offset = filters.offset ?? 0;
        return {
          items: items.slice(offset, offset + limit),
          total: items.length,
          limit,
          offset,
        };
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
  return useQuery<AspectStatItem[]>({
    queryKey: queryKeys.stats.aspects,
    queryFn: async () => {
      if (USE_MOCK) return MOCK_ASPECT_STATS;
      return api.get<AspectStatItem[]>("/stats/aspects");
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
      queryClient.invalidateQueries({ queryKey: queryKeys.stats.aspects });
      queryClient.invalidateQueries({ queryKey: queryKeys.health });
    },
  });
}

export function useUpdateStatus() {
  const queryClient = useQueryClient();
  return useMutation<TicketOut, Error, { id: number; payload: StatusUpdateIn }, UpdateStatusContext>({
    mutationFn: async ({ id, payload }) => {
      if (USE_MOCK) {
        const index = MOCK_TICKETS.findIndex((item) => item.id === id);
        if (index === -1) {
          throw new Error(`Không tìm thấy ticket #${id} trong dữ liệu mẫu`);
        }
        const updated: TicketOut = {
          ...MOCK_TICKETS[index],
          status: payload.status,
          assigned_to: payload.assigned_to !== undefined ? payload.assigned_to : MOCK_TICKETS[index].assigned_to,
          updated_at: new Date().toISOString(),
        };
        MOCK_TICKETS[index] = updated;
        return updated;
      }
      return api.patch<TicketOut>(`/tickets/${id}/status`, payload);
    },
    onMutate: async ({ id, payload }) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.tickets.all });

      const previousLists = queryClient.getQueriesData<TicketListResponse>({
        queryKey: TICKETS_LIST_QUERY_PREFIX,
      });
      const detailKey = queryKeys.tickets.detail(id);
      const previousDetail = queryClient.getQueryData<TicketOut>(detailKey);
      const nowIso = new Date().toISOString();

      queryClient.setQueriesData<TicketListResponse>(
        { queryKey: TICKETS_LIST_QUERY_PREFIX },
        (old) => {
          if (!old) return old;
          return {
            ...old,
            items: old.items.map((item) =>
              item.id === id
                ? {
                    ...item,
                    status: payload.status,
                    assigned_to: payload.assigned_to !== undefined ? payload.assigned_to : item.assigned_to,
                    updated_at: nowIso,
                  }
                : item
            ),
          };
        }
      );

      if (previousDetail) {
        queryClient.setQueryData<TicketOut>(detailKey, {
          ...previousDetail,
          status: payload.status,
          assigned_to: payload.assigned_to !== undefined ? payload.assigned_to : previousDetail.assigned_to,
          updated_at: nowIso,
        });
      }

      return { previousLists, previousDetail };
    },
    onError: (_err, vars, context) => {
      if (context?.previousLists) {
        for (const [key, data] of context.previousLists) {
          queryClient.setQueryData(key, data);
        }
      }
      if (context?.previousDetail !== undefined) {
        queryClient.setQueryData(queryKeys.tickets.detail(vars.id), context.previousDetail);
      }
    },
    onSuccess: (updatedTicket, vars) => {
      queryClient.setQueryData(queryKeys.tickets.detail(vars.id), updatedTicket);
      queryClient.invalidateQueries({ queryKey: queryKeys.tickets.detail(vars.id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.stats.overview });
      queryClient.invalidateQueries({ queryKey: queryKeys.stats.aspects });
      queryClient.invalidateQueries({ queryKey: queryKeys.health });
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.tickets.all });
    },
  });
}
