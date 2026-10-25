import React from "react";
import { AspectOut } from "../../api/schema";
import { SENTIMENT_CONFIG } from "../../lib/constants";

interface AspectChipsProps {
  aspects: AspectOut[];
  maxDisplay?: number;
}

export const AspectChips: React.FC<AspectChipsProps> = ({ aspects, maxDisplay = 3 }) => {
  if (!aspects || aspects.length === 0) {
    return <span className="text-xs text-slate-400 italic">Chưa phân tích khía cạnh</span>;
  }

  // Sắp xếp: Tiêu cực đứng trước, sau đó trung tính, rồi tích cực
  const sorted = [...aspects].sort((a, b) => {
    const priorityMap = { negative: 0, neutral: 1, positive: 2 };
    return priorityMap[a.sentiment] - priorityMap[b.sentiment];
  });

  const displayed = sorted.slice(0, maxDisplay);
  const remainingCount = sorted.length - maxDisplay;

  return (
    <div className="flex flex-wrap items-center gap-1.5">
      {displayed.map((item, index) => {
        const config = SENTIMENT_CONFIG[item.sentiment] || SENTIMENT_CONFIG.neutral;
        const aspectName = item.aspect.replace("_", " ");

        return (
          <span
            key={`${item.aspect}-${index}`}
            className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs border ${config.bgClass}`}
            title={`Độ tin cậy: ${(item.confidence * 100).toFixed(0)}%`}
          >
            <span className="capitalize">{aspectName}</span>
            <span className="opacity-75 text-[10px]">({config.label})</span>
          </span>
        );
      })}

      {remainingCount > 0 && (
        <span className="px-1.5 py-0.5 text-xs text-slate-500 bg-slate-100 rounded border border-slate-200">
          +{remainingCount}
        </span>
      )}
    </div>
  );
};
