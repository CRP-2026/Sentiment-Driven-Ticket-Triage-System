export const queryKeys = {
  tickets: {
    all: ["tickets"] as const,
    list: (filters: { status?: string; aspect?: string; sentiment?: string; offset?: number; limit?: number }) =>
      ["tickets", "list", filters] as const,
    detail: (id: number) => ["tickets", "detail", id] as const,
  },
  aspects: ["meta", "aspects"] as const,
  stats: {
    overview: ["stats", "overview"] as const,
    aspects: ["stats", "aspects"] as const,
  },
  health: ["health"] as const,
};
