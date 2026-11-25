import {
  AspectMetaItem,
  AspectStatItem,
  PriorityLevel,
  TicketStatus,
} from "../api/schema";
import { PRIORITY_HIGH, PRIORITY_MED } from "./constants";

export const ALLOWED_STATUS_TRANSITIONS: Record<TicketStatus, readonly TicketStatus[]> = {
  new: ["assigned", "in_progress"],
  assigned: ["in_progress", "new"],
  in_progress: ["resolved", "assigned"],
  resolved: ["new"],
};

export const CRITICAL_EVIDENCE_TERMS = [
  "urgent",
  "immediately",
  "asap",
  "lawsuit",
  "sue",
  "lawyer",
  "fraud",
  "scam",
  "chargeback",
  "stolen",
  "charged twice",
  "double charged",
  "billed twice",
  "unauthorized charge",
] as const;

export const HIGH_EVIDENCE_TERMS = [
  "broken",
  "refund",
  "cancel",
  "not working",
  "never received",
  "never arrived",
  "lost package",
  "stuck in transit",
  "hung up",
  "dispute",
  "missing",
  "damaged",
  "overcharged",
] as const;

const EVIDENCE_LEVEL_PRIORITY: Record<EvidenceLevel, number> = {
  critical: 3,
  high: 2,
  aspect: 1,
};

export type EvidenceLevel = "critical" | "high" | "aspect";
export type EvidenceTone = "urgency" | "intensity" | "aspect" | "sentiment";

export interface HighlightRange {
  start: number;
  end: number;
  phrase: string;
  level: EvidenceLevel;
}

export interface AspectSentimentMatrixRow {
  aspectId: string;
  aspectName: string;
  negative: number;
  neutral: number;
  positive: number;
  total: number;
}

/**
 * Ưu tiên dùng priority_level từ API (Server is Source of Truth);
 * chỉ fallback về ngưỡng điểm FE khi thiếu trường hợp lệ.
 */
export function resolvePriorityLevel(
  score: number,
  apiLevel?: PriorityLevel | string | null,
): PriorityLevel {
  if (apiLevel === "CRITICAL" || apiLevel === "MEDIUM" || apiLevel === "LOW") {
    return apiLevel;
  }
  if (score >= PRIORITY_HIGH) return "CRITICAL";
  if (score >= PRIORITY_MED) return "MEDIUM";
  return "LOW";
}

/**
 * UX guard phản chiếu FSM của Backend (StateManager).
 * Backend vẫn thực hiện validation cuối cùng và có thể từ chối qua HTTP 400.
 */
export function canTransitionStatus(currentStatus: string, nextStatus: string): boolean {
  if (currentStatus === nextStatus) return true;
  const allowed = ALLOWED_STATUS_TRANSITIONS[currentStatus as TicketStatus];
  if (!allowed) return false;
  return allowed.includes(nextStatus as TicketStatus);
}

export function getEvidenceLevel(phrase: string, reason?: string): EvidenceLevel {
  if (reason) {
    if (/(?:từ khóa|keyword)\s+CRITICAL\b/i.test(reason)) {
      return "critical";
    }
    if (/(?:từ khóa|keyword)\s+HIGH\b/i.test(reason)) {
      return "high";
    }
  }

  const normalized = phrase.trim().toLowerCase();
  if ((CRITICAL_EVIDENCE_TERMS as readonly string[]).includes(normalized)) {
    return "critical";
  }
  if ((HIGH_EVIDENCE_TERMS as readonly string[]).includes(normalized)) {
    return "high";
  }
  return "aspect";
}

export function getEvidenceTone(reason: string): EvidenceTone {
  const normalized = reason.trim();
  if (
    /^(?:khía cạnh|aspect|dominant)/i.test(normalized) ||
    /trọng số|weight=|'[^']+_[a-z]+'/i.test(normalized)
  ) {
    return "aspect";
  }
  if (/cú pháp câu|bức xúc|cường độ|intensity|caps lock|!{3,}|\?{3,}/i.test(normalized)) {
    return "intensity";
  }
  if (
    /từ khóa|keyword|khẩn cấp|khủng hoảng|urgent|immediately|asap|lawsuit|fraud|scam|chargeback|stolen|dispute|charged twice|double charged|billed twice|unauthorized charge|broken|refund|cancel|never received|never arrived|lost package|stuck in transit|hung up|not working|missing|damaged|overcharged/i.test(
      normalized,
    )
  ) {
    return "urgency";
  }
  return "sentiment";
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export function findEvidenceRanges(
  content: string,
  reasons: readonly string[] = [],
): HighlightRange[] {
  if (!content || reasons.length === 0) return [];

  const phraseEntries = new Map<string, { phrase: string; level: EvidenceLevel }>();
  for (const reason of reasons) {
    for (const match of reason.matchAll(/'([^']+)'/g)) {
      const phrase = match[1].trim();
      if (!phrase) continue;

      const key = phrase.toLowerCase();
      const level = getEvidenceLevel(phrase, reason);
      const existing = phraseEntries.get(key);
      if (!existing || EVIDENCE_LEVEL_PRIORITY[level] > EVIDENCE_LEVEL_PRIORITY[existing.level]) {
        phraseEntries.set(key, { phrase, level });
      }
    }
  }

  const ranges: HighlightRange[] = [];
  for (const { phrase, level } of phraseEntries.values()) {
    const escaped = escapeRegExp(phrase);
    const startsWord = /^\w/.test(phrase);
    const endsWord = /\w$/.test(phrase);
    const regex = new RegExp(
      `${startsWord ? "\\b" : ""}${escaped}${endsWord ? "\\b" : ""}`,
      "gi",
    );

    let match: RegExpExecArray | null;
    while ((match = regex.exec(content)) !== null) {
      if (match[0].length === 0) {
        regex.lastIndex += 1;
        continue;
      }
      ranges.push({
        start: match.index,
        end: match.index + match[0].length,
        phrase: match[0],
        level,
      });
    }
  }

  ranges.sort((a, b) => a.start - b.start || b.end - a.end);

  const accepted: HighlightRange[] = [];
  for (const range of ranges) {
    const prev = accepted[accepted.length - 1];
    if (!prev || range.start >= prev.end) {
      accepted.push(range);
    }
  }
  return accepted;
}

export function getAspectDisplayName(
  aspectId: string,
  aspectsMeta?: readonly AspectMetaItem[],
): string {
  const found = aspectsMeta?.find((item) => item.id === aspectId);
  if (found?.name_vi) return found.name_vi;
  return aspectId.replace(/_/g, " ");
}

export function buildAspectSentimentMatrix(
  aspectStats: readonly AspectStatItem[] | undefined,
  aspectsMeta?: readonly AspectMetaItem[],
): AspectSentimentMatrixRow[] {
  if (!aspectStats || aspectStats.length === 0) return [];

  const rowsByAspect = new Map<string, AspectSentimentMatrixRow>();
  for (const item of aspectStats) {
    let row = rowsByAspect.get(item.aspect);
    if (!row) {
      row = {
        aspectId: item.aspect,
        aspectName: getAspectDisplayName(item.aspect, aspectsMeta),
        negative: 0,
        neutral: 0,
        positive: 0,
        total: 0,
      };
      rowsByAspect.set(item.aspect, row);
    }

    if (item.sentiment === "negative" || item.sentiment === "neutral" || item.sentiment === "positive") {
      row[item.sentiment] += item.count;
      row.total += item.count;
    }
  }

  return Array.from(rowsByAspect.values()).sort(
    (a, b) => b.total - a.total || b.negative - a.negative || a.aspectId.localeCompare(b.aspectId),
  );
}
