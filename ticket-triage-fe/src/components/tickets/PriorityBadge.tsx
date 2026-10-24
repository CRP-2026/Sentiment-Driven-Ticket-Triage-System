import React from "react";
import { AlertCircle, AlertTriangle, CheckCircle2 } from "lucide-react";
import { PRIORITY_HIGH, PRIORITY_MED } from "../../lib/constants";
import { formatScore } from "../../lib/format";

interface PriorityBadgeProps {
  score: number;
  showIcon?: boolean;
}

export const PriorityBadge: React.FC<PriorityBadgeProps> = ({ score, showIcon = true }) => {
  let label = "Thấp";
  let colorClass = "bg-emerald-50 text-emerald-700 border-emerald-200";
  let icon = <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />;

  if (score >= PRIORITY_HIGH) {
    label = "Cao";
    colorClass = "bg-red-50 text-red-700 border-red-200 font-semibold";
    icon = <AlertCircle className="w-3.5 h-3.5 text-red-600" />;
  } else if (score >= PRIORITY_MED) {
    label = "Trung bình";
    colorClass = "bg-amber-50 text-amber-700 border-amber-200 font-medium";
    icon = <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />;
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs border ${colorClass}`}
      aria-label={`Mức ưu tiên: ${label}, điểm số ${formatScore(score)}`}
    >
      {showIcon && icon}
      <span>{label}</span>
      <span className="opacity-75 font-mono">({formatScore(score)})</span>
    </span>
  );
};
