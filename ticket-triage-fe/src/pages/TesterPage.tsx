import React, { useState } from "react";
import { useTriageTicket } from "../api/hooks";
import { PriorityBadge } from "../components/tickets/PriorityBadge";
import { AspectChips } from "../components/tickets/AspectChips";
import { PriorityBreakdown } from "../components/tickets/PriorityBreakdown";
import { TicketOut } from "../api/schema";
import { Send, Sparkles, AlertCircle, CheckCircle2 } from "lucide-react";

const SAMPLE_PROMPTS = [
  {
    label: "Bị trừ tiền hai lần (Critical)",
    text: "I was charged twice for order #9921! Please refund immediately or I will dispute the chargeback with my bank!",
  },
  {
    label: "Giao trễ + Hỏng hóc (Critical)",
    text: "My package is 12 days late and the tracking number is broken. This is totally unacceptable!!!",
  },
  {
    label: "Chất lượng sản phẩm kém (Medium)",
    text: "The jacket material feels very cheap and the zipper broke on first use. Disappointed with the quality.",
  },
  {
    label: "Hỏi đáp thông thường (Low)",
    text: "Could you please help me check if this wireless headset is compatible with Windows 11?",
  },
  {
    label: "Ngoại ngữ tiếng Việt (Gắn cờ duyệt)",
    text: "Tôi muốn yêu cầu hỗ trợ đổi trả đơn hàng giao nhầm kích cỡ.",
  },
];

export const TesterPage: React.FC = () => {
  const [content, setContent] = useState("");
  const [result, setResult] = useState<TicketOut | null>(null);

  const triageMutation = useTriageTicket();

  const handleAnalyze = (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim() || triageMutation.isPending) return;

    triageMutation.mutate(
      { content },
      {
        onSuccess: (data) => {
          setResult(data);
        },
      }
    );
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-blue-600" />
          <span>Khung mô phỏng kiểm thử thời gian thực (Live Tester)</span>
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Nhập bất kỳ đoạn văn bản ticket phản hồi nào để kiểm chứng toàn trình 2 bài toán (ABSA NLI + Priority Engine)
        </p>
      </div>

      {/* Input Form */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        {/* Sample Buttons */}
        <div>
          <span className="text-xs font-semibold text-slate-500 uppercase block mb-2">Thử nhanh tình huống mẫu:</span>
          <div className="flex flex-wrap gap-2">
            {SAMPLE_PROMPTS.map((sample, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => setContent(sample.text)}
                className="text-xs px-2.5 py-1.5 rounded-lg border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-700 transition-colors"
              >
                {sample.label}
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleAnalyze} className="space-y-3">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={4}
            placeholder="Nhập nội dung phản hồi của khách hàng bằng tiếng Anh (ví dụ: 'My order hasn't arrived after 2 weeks and I want my money back!')..."
            className="w-full text-sm rounded-xl border border-slate-200 p-3 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all font-sans"
            required
          />

          <div className="flex justify-between items-center">
            <span className="text-xs text-slate-400">
              {content.length} ký tự
            </span>
            <button
              type="submit"
              disabled={!content.trim() || triageMutation.isPending}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-semibold shadow-md shadow-blue-500/20 transition-all"
            >
              <Send className="w-4 h-4" />
              <span>{triageMutation.isPending ? "Đang phân tích..." : "Phân tích & Triage ngay"}</span>
            </button>
          </div>
        </form>

        {triageMutation.isError && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0" />
            <span>Có lỗi khi gọi API triage: {triageMutation.error?.message}</span>
          </div>
        )}
      </div>

      {/* Analysis Output Result */}
      {result && (
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-5 animate-in fade-in duration-300">
          <div className="flex items-center justify-between border-b pb-3">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-600" />
              <h3 className="text-base font-bold text-slate-900">Kết quả phân tích toàn trình thành công</h3>
            </div>
            <span className="text-xs font-mono text-slate-400">ID #{result.id}</span>
          </div>

          {/* Cards overview */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-xs text-slate-500 block mb-1">Mức ưu tiên tính toán:</span>
              <PriorityBadge score={result.priority_score} />
            </div>

            <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-xs text-slate-500 block mb-1">Cảm xúc tổng thể (ABSA):</span>
              <span className="text-sm font-semibold capitalize text-slate-800">
                {result.sentiment_label || "Chưa xác định"}{" "}
                {result.confidence && `(${(result.confidence * 100).toFixed(0)}%)`}
              </span>
            </div>

            <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-xs text-slate-500 block mb-1">Ngôn ngữ & Cờ duyệt:</span>
              <span className="text-sm font-semibold text-slate-800">
                {result.language_flag.toUpperCase()}{" "}
                {result.needs_manual_review ? "(Cần duyệt)" : "(Hợp lệ)"}
              </span>
            </div>
          </div>

          {/* Aspects list */}
          <div>
            <h4 className="text-xs font-semibold text-slate-500 uppercase mb-2">Các khía cạnh phát hiện được (ABSA):</h4>
            <AspectChips aspects={result.aspects} maxDisplay={10} />
          </div>

          {/* Detailed Priority Breakdown */}
          <PriorityBreakdown
            breakdown={result.priority_breakdown}
            dominantAspect={result.dominant_aspect}
            needsManualReview={result.needs_manual_review}
          />
        </div>
      )}
    </div>
  );
};
