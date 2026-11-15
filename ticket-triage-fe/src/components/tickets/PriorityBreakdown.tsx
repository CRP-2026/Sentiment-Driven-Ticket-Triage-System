import React from "react";
import { AlertCircle, CheckCircle2 } from "lucide-react";
import { useAspects } from "../../api/hooks";
import { AspectMetaItem, PriorityBreakdownOut } from "../../api/schema";
import { formatScore } from "../../lib/format";
import {
  getAspectDisplayName,
  getEvidenceLevel,
  getEvidenceTone,
} from "../../lib/ticketHelpers";

interface PriorityBreakdownProps {
  breakdown?: PriorityBreakdownOut | null;
  dominantAspect?: string | null;
  needsManualReview?: boolean;
  aspectsMeta?: readonly AspectMetaItem[];
}

const renderEvidenceText = (reason: string) =>
  reason.split(/('[^']+')/g).map((part, index) => {
    if (part.startsWith("'") && part.endsWith("'") && part.length >= 2) {
      const phrase = part.slice(1, -1);
      const level = getEvidenceLevel(phrase);
      return (
        <mark className={`audit-evidence-highlight audit-evidence-level-${level}`} key={index}>
          {part}
        </mark>
      );
    }
    return part;
  });

export const PriorityBreakdown: React.FC<PriorityBreakdownProps> = ({
  breakdown,
  dominantAspect,
  needsManualReview,
  aspectsMeta,
}) => {
  const { data: fetchedAspects } = useAspects();
  const resolvedMeta = aspectsMeta ?? fetchedAspects;

  if (!breakdown) {
    return (
      <div className="audit-breakdown-empty p-4 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-500 italic">
        Chưa có dữ liệu giải trình điểm ưu tiên.
      </div>
    );
  }

  return (
    <div className="audit-breakdown bg-white border border-slate-200 rounded-lg p-4 shadow-sm space-y-3">
      <div className="audit-breakdown-header flex items-center justify-between border-b pb-2">
        <div>
          <h4 className="text-sm font-semibold text-slate-900">Chi tiết chấm điểm ưu tiên</h4>
          <p className="text-xs text-slate-500">Minh bạch, kiểm toán được theo công thức nghiệp vụ</p>
        </div>
        <div className="text-right">
          <span className="text-2xl font-bold font-mono text-slate-900">{formatScore(breakdown.score)}</span>
          <span className="text-xs text-slate-500 block">/ 100 điểm</span>
        </div>
      </div>

      {needsManualReview && (
        <div className="audit-review-flag flex items-center gap-2 p-2.5 bg-amber-50 border border-amber-200 rounded text-xs text-amber-800">
          <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0" />
          <span>Ticket này được gắn cờ <strong>Cần kiểm tra thủ công</strong> (do ngoại ngữ hoặc độ tin cậy thấp).</span>
        </div>
      )}

      {/* Grid các thành phần điểm */}
      <div
        className="audit-contribution-track"
        role="img"
        aria-label={`Phân bổ thành phần điểm: điểm nền ${formatScore(breakdown.base)}, từ khóa khẩn cấp ${formatScore(breakdown.urgency_bonus)}, cường độ ${formatScore(breakdown.intensity_bonus)}, khía cạnh ${formatScore(breakdown.aspect_bonus)}`}
      >
        <span className="audit-segment-base" style={{ flexGrow: breakdown.base }} />
        <span className="audit-segment-urgency" style={{ flexGrow: breakdown.urgency_bonus }} />
        <span className="audit-segment-intensity" style={{ flexGrow: breakdown.intensity_bonus }} />
        <span className="audit-segment-aspect" style={{ flexGrow: breakdown.aspect_bonus }} />
      </div>

      <div className="audit-component-grid grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
        <div className="bg-slate-50 p-2 rounded border border-slate-100">
          <span className="text-slate-500 block">Điểm nền:</span>
          <span className="font-semibold text-slate-800 font-mono text-sm">{formatScore(breakdown.base)}</span>
        </div>
        <div className="bg-slate-50 p-2 rounded border border-slate-100">
          <span className="text-slate-500 block">Từ khóa khẩn cấp:</span>
          <span className="font-semibold text-slate-800 font-mono text-sm">+{formatScore(breakdown.urgency_bonus)}</span>
        </div>
        <div className="bg-slate-50 p-2 rounded border border-slate-100">
          <span className="text-slate-500 block">Cường độ câu (!!!):</span>
          <span className="font-semibold text-slate-800 font-mono text-sm">+{formatScore(breakdown.intensity_bonus)}</span>
        </div>
        <div className="bg-slate-50 p-2 rounded border border-slate-100">
          <span className="text-slate-500 block">Khía cạnh tiêu cực:</span>
          <span className="font-semibold text-slate-800 font-mono text-sm">+{formatScore(breakdown.aspect_bonus)}</span>
        </div>
      </div>

      {dominantAspect && (
        <div className="audit-dominant-aspect text-xs text-slate-600">
          Khía cạnh quyết định:{" "}
          <strong className="text-slate-900">
            {getAspectDisplayName(dominantAspect, resolvedMeta)}
          </strong>
        </div>
      )}

      {/* Danh sách lý do minh chứng */}
      <details className="audit-evidence">
        <summary className="audit-evidence-summary">
          <span className="text-xs font-medium text-slate-700 block mb-1">Căn cứ giải trình cụ thể:</span>
        </summary>
        <ul className="audit-evidence-list space-y-1">
          {breakdown.reasons.map((reason, idx) => {
            const tone = getEvidenceTone(reason);
            return (
              <li key={idx} className={`audit-evidence-row audit-evidence-${tone}`}>
                <CheckCircle2 aria-hidden="true" />
                <span>{renderEvidenceText(reason)}</span>
              </li>
            );
          })}
        </ul>
      </details>
    </div>
  );
};
