import type { components } from "./generated";

type Schemas = components["schemas"];

export type Sentiment = "negative" | "neutral" | "positive";
export type PriorityLevel = "CRITICAL" | "MEDIUM" | "LOW";
export type TicketStatus = Schemas["StatusEnum"];

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
export type HealthResponse = Required<Schemas["HealthResponse"]>;
export type StatsOverview = Schemas["StatsOverviewResponse"];

export type AspectStatItem = Omit<Schemas["AspectStatItem"], "sentiment"> & {
  sentiment: Sentiment;
};
