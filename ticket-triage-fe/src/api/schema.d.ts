export interface AspectOut {
  aspect: string;
  sentiment: "negative" | "neutral" | "positive";
  confidence: number;
  terms?: string[];
}

export interface PriorityBreakdownOut {
  score: number;
  base: number;
  urgency_bonus: number;
  intensity_bonus: number;
  aspect_bonus: number;
  reasons: string[];
}

export interface TicketOut {
  id: number;
  content: string;
  processed_content?: string | null;
  language_flag: string;
  needs_manual_review: boolean;
  sentiment_label?: "negative" | "neutral" | "positive" | null;
  confidence?: number | null;
  low_confidence: boolean;
  priority_score: number;
  priority_level: "CRITICAL" | "MEDIUM" | "LOW";
  dominant_aspect?: string | null;
  priority_breakdown?: PriorityBreakdownOut | null;
  status: "new" | "assigned" | "in_progress" | "resolved";
  assigned_to?: string | null;
  aspects: AspectOut[];
  created_at: string;
  updated_at: string;
}

export interface TicketListResponse {
  items: TicketOut[];
  total: number;
  limit: number;
  offset: number;
}

export interface TicketCreateIn {
  content: string;
}

export interface StatusUpdateIn {
  status: "new" | "assigned" | "in_progress" | "resolved";
  assigned_to?: string | null;
}

export interface AspectMetaItem {
  id: string;
  name_vi: string;
  description: string;
  department: string;
  weight: number;
}

export interface HealthResponse {
  status: string;
  version: string;
  model_name: string;
  queue_size: number;
}

export interface StatsOverview {
  total_tickets: number;
  sentiment_counts: Record<string, number>;
  priority_counts: Record<string, number>;
  status_counts: Record<string, number>;
  aspect_counts: Record<string, number>;
}
