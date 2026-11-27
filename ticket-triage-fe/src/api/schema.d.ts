import type { components } from "./generated";

type Schemas = components["schemas"];

export type Sentiment = "negative" | "neutral" | "positive";
export type SentimentSummary = "positive" | "mixed" | "negative";
export type PriorityLevel = "CRITICAL" | "MEDIUM" | "LOW";
export type TicketStatus = Schemas["StatusEnum"];
export type UserRole = Schemas["UserRoleEnum"];

export type AspectOut = Omit<Schemas["AspectOut"], "sentiment"> & {
  sentiment: Sentiment;
};

export type PriorityBreakdownOut = Schemas["PriorityBreakdownOut"];

export type TicketOut = Omit<
  Schemas["TicketOut"],
  "sentiment_label" | "priority_level" | "aspects"
> & {
  sentiment_label?: Sentiment | null;
  priority_level: PriorityLevel;
  aspects: AspectOut[];
};

export type TicketListResponse = Omit<Schemas["TicketListResponse"], "items"> & {
  items: TicketOut[];
};

export type TicketCreateIn = Schemas["TicketCreateIn"];
export type StatusUpdateIn = Schemas["StatusUpdateIn"];
export type AspectMetaItem = Schemas["AspectMetaItem"];
export type HealthResponse = Required<
  Omit<Schemas["HealthResponse"], "triage_gateway_mode">
> &
  Pick<Schemas["HealthResponse"], "triage_gateway_mode">;
export type StatsOverview = Schemas["StatsOverviewResponse"];

export type AspectStatItem = Omit<Schemas["AspectStatItem"], "sentiment"> & {
  sentiment: Sentiment;
};

// ==============================================================================
// Auth & Storefront Schemas (auto-derived from OpenAPI generated.ts)
// ==============================================================================
export type RegisterIn = Schemas["RegisterIn"];
export type LoginIn = Schemas["LoginIn"];
export type UserOut = Schemas["UserOut"];
export type AuthResponse = Omit<Schemas["AuthResponse"], "token_type"> & {
  token_type: string;
};

export type CategoryOut = Omit<Schemas["CategoryOut"], "product_count"> & {
  product_count: number;
};

export type AspectInsightOut = Omit<
  Schemas["AspectInsightOut"],
  "sentiment_summary" | "top_terms"
> & {
  sentiment_summary: SentimentSummary;
  top_terms: string[];
};

export type ProductInsightsOut = Omit<
  Schemas["ProductInsightsOut"],
  "aspects" | "top_ranked_aspects"
> & {
  aspects: AspectInsightOut[];
  top_ranked_aspects: AspectInsightOut[];
};

export type ProductOut = Schemas["ProductOut"];

export type ProductSummaryOut = Omit<
  Schemas["ProductSummaryOut"],
  "total_reviews" | "satisfaction_rate" | "top_ranked_aspects"
> & {
  total_reviews: number;
  satisfaction_rate: number;
  top_ranked_aspects: AspectInsightOut[];
};

export type ProductListResponse = Omit<Schemas["ProductListResponse"], "items"> & {
  items: ProductSummaryOut[];
};

export type ReviewOut = Omit<
  Schemas["ReviewOut"],
  "sentiment_label" | "priority_level" | "aspects"
> & {
  sentiment_label?: Sentiment | null;
  priority_level: PriorityLevel;
  aspects: AspectOut[];
};

export type ProductDetailResponse = Omit<
  Schemas["ProductDetailResponse"],
  "insights" | "reviews"
> & {
  insights: ProductInsightsOut;
  reviews: ReviewOut[];
};

export type ReviewCreateIn = Schemas["ReviewCreateIn"];

export type ReviewTriageSummaryOut = Omit<
  Schemas["ReviewTriageSummaryOut"],
  "sentiment_label" | "priority_level" | "aspects"
> & {
  sentiment_label?: Sentiment | null;
  priority_level: PriorityLevel;
  aspects: AspectOut[];
};

export type ReviewCreateResponse = Omit<
  Schemas["ReviewCreateResponse"],
  "review" | "triage" | "insights"
> & {
  review: ReviewOut;
  triage: ReviewTriageSummaryOut;
  insights: ProductInsightsOut;
};

export type ImageUploadResponse = Schemas["ImageUploadResponse"];
