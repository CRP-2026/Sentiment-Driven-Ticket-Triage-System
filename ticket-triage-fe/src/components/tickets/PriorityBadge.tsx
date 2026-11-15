import React from "react";
import { AlertCircle, AlertTriangle, CheckCircle2 } from "lucide-react";
import { PriorityLevel, TicketOut } from "../../api/schema";
import { formatScore } from "../../lib/format";
import { resolvePriorityLevel } from "../../lib/ticketHelpers";

interface PriorityBadgeProps {
  score: number;
  level?: TicketOut["priority_level"];
  showIcon?: boolean;
}

const PRIORITY_BADGE_CONFIG: Record<
  PriorityLevel,
  { label: string; colorClass: string; icon: React.ReactNode }
> = {
  CRITICAL: {
    label: "Nghiêm trọng",
    colorClass: "border-l-4 border-red-800 border-y-red-200 border-r-red-200 bg-red-50 text-red-950",
    icon: <AlertCircle className="h-3.5 w-3.5 text-red-800" />,
  },
  MEDIUM: {
    label: "Trung bình",
    colorClass: "border-l-4 border-amber-700 border-y-amber-200 border-r-amber-200 bg-amber-50 text-amber-950",
    icon: <AlertTriangle className="h-3.5 w-3.5 text-amber-700" />,
  },
  LOW: {
    label: "Thấp",
    colorClass: "border-l-4 border-emerald-700 border-y-emerald-100 border-r-emerald-100 bg-emerald-50 text-emerald-900",
    icon: <CheckCircle2 className="h-3.5 w-3.5 text-emerald-700" />,
  },
};

export const PriorityBadge: React.FC<PriorityBadgeProps> = ({ score, level, showIcon = true }) => {
  const effectiveLevel = resolvePriorityLevel(score, level);
  const { label, colorClass, icon } = PRIORITY_BADGE_CONFIG[effectiveLevel];

  return (
    <span
      className={`queue-priority-pill inline-flex h-8 whitespace-nowrap items-center justify-center gap-1.5 rounded-full border px-3 text-xs font-semibold ${colorClass}`}
      aria-label={`Mức ưu tiên: ${label}, điểm số ${formatScore(score)}`}
    >
      {showIcon && icon}
      <span>{label}</span>
      <span className="font-mono tabular-nums">{formatScore(score)}</span>
    </span>
  );
};
