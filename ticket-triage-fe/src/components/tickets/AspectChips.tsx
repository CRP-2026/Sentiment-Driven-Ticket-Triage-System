import React from "react";
import { useAspects } from "../../api/hooks";
import { AspectMetaItem, AspectOut, Sentiment } from "../../api/schema";
import { SENTIMENT_CONFIG } from "../../lib/constants";
import { getAspectDisplayName } from "../../lib/ticketHelpers";

interface AspectChipsProps {
  aspects: AspectOut[];
  maxDisplay?: number;
  aspectsMeta?: readonly AspectMetaItem[];
}

const SENTIMENT_SORT_ORDER: Record<Sentiment, number> = {
  negative: 0,
  neutral: 1,
  positive: 2,
};

export const AspectChips: React.FC<AspectChipsProps> = ({
  aspects,
  maxDisplay = 3,
  aspectsMeta,
}) => {
  const { data: fetchedAspects } = useAspects();
  const resolvedMeta = aspectsMeta ?? fetchedAspects;

  if (!aspects || aspects.length === 0) {
    return <span className="whitespace-nowrap text-xs italic text-slate-400">Chưa phân tích khía cạnh</span>;
  }

  // Sắp xếp: Tiêu cực đứng trước, sau đó trung tính, rồi tích cực
  const sorted = [...aspects].sort((a, b) => {
    const orderDiff = (SENTIMENT_SORT_ORDER[a.sentiment] ?? 3) - (SENTIMENT_SORT_ORDER[b.sentiment] ?? 3);
    return orderDiff !== 0 ? orderDiff : b.confidence - a.confidence;
  });

  const displayed = sorted.slice(0, maxDisplay);
  const remainingCount = sorted.length - maxDisplay;

  return (
    <div className="flex flex-wrap items-center gap-1.5">
      {displayed.map((item, index) => {
        const config = SENTIMENT_CONFIG[item.sentiment] || SENTIMENT_CONFIG.neutral;
        const aspectName = getAspectDisplayName(item.aspect, resolvedMeta);

        return (
          <span
            key={`${item.aspect}-${index}`}
            className={`inline-flex shrink-0 whitespace-nowrap items-center gap-1 rounded border px-2 py-0.5 text-[11px] font-medium ${config.bgClass}`}
            title={`Độ tin cậy: ${(item.confidence * 100).toFixed(0)}%`}
          >
            <span>{aspectName}</span>
            <span className="opacity-75 text-[10px]">({config.label})</span>
          </span>
        );
      })}

      {remainingCount > 0 && (
        <span className="whitespace-nowrap rounded border border-slate-200 bg-slate-100 px-1.5 py-0.5 text-xs text-slate-500">
          +{remainingCount}
        </span>
      )}
    </div>
  );
};
