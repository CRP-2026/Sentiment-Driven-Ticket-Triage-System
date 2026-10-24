import React from "react";
import { PriorityBreakdownOut } from "../../api/schema";
import { formatScore } from "../../lib/format";
import { AlertCircle, CheckCircle2 } from "lucide-react";

interface PriorityBreakdownProps {
  breakdown?: PriorityBreakdownOut | null;
  dominantAspect?: string | null;
  needsManualReview?: boolean;
}

export const PriorityBreakdown: React.FC<PriorityBreakdownProps> = ({
  breakdown,
  dominantAspect,
  needsManualReview,
}) => {
  if (!breakdown) {
    return (
      <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-500 italic">
        Chưa có dữ liệu giải trình điểm ưu tiên.
      </div>
    );
  }

  return (
    <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm space-y-3">
      <div className="flex items-center justify-between border-b pb-2">
        <div>
          <h4 className="text-sm font-semibold text-slate-900">Chi tiết chấm điểm ưu tiên (Rule-based)</h4>
          <p className="text-xs text-slate-500">Minh bạch, kiểm toán được theo công thức nghiệp vụ</p>
        </div>
        <div className="text-right">
          <span className="text-2xl font-bold font-mono text-slate-900">{formatScore(breakdown.score)}</span>
          <span className="text-xs text-slate-500 block">/ 100 điểm</span>
        </div>
      </div>

      {needsManualReview && (
        <div className="flex items-center gap-2 p-2.5 bg-amber-50 border border-amber-200 rounded text-xs text-amber-800">
          <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0" />
          <span>Ticket này được gắn cờ <strong>Cần kiểm tra thủ công</strong> (do ngoại ngữ hoặc độ tin cậy thấp).</span>
        </div>
      )}

      {/* Grid các thành phần điểm */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
        <div className="bg-slate-50 p-2 rounded border border-slate-100">
          <span className="text-slate-500 block">Điểm nền (Base):</span>
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
        <div className="text-xs text-slate-600">
          Khía cạnh quyết định (Dominant): <strong className="capitalize text-slate-900">{dominantAspect.replace("_", " ")}</strong>
        </div>
      )}

      {/* Danh sách lý do minh chứng */}
      <div>
        <span className="text-xs font-medium text-slate-700 block mb-1">Căn cứ giải trình cụ thể:</span>
        <ul className="space-y-1">
          {breakdown.reasons.map((reason, idx) => (
            <li key={idx} className="flex items-start gap-1.5 text-xs text-slate-600">
              <CheckCircle2 className="w-3.5 h-3.5 text-blue-500 flex-shrink-0 mt-0.5" />
              <span>{reason}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};
