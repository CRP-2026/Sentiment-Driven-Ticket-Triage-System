import React, { useEffect, useState } from "react";
import { useTriageTicket } from "../api/hooks";
import { PriorityBadge } from "../components/tickets/PriorityBadge";
import { AspectChips } from "../components/tickets/AspectChips";
import { PriorityBreakdown } from "../components/tickets/PriorityBreakdown";
import { TicketOut } from "../api/schema";
import { Send, Sparkles, Clock, AlertCircle, CheckCircle2 } from "lucide-react";

const SAMPLE_PROMPTS = [
  {
    label: "Bị trừ tiền hai lần (Nghiêm trọng)",
    text: "I was charged twice for order #9921! Please refund immediately or I will dispute the chargeback with my bank!",
  },
  {
    label: "Giao trễ + Hỏng hóc (Nghiêm trọng)",
    text: "My package is 12 days late and the tracking number is broken. This is totally unacceptable!!!",
  },
  {
    label: "Chất lượng sản phẩm kém (Trung bình)",
    text: "The jacket material feels very cheap and the zipper broke on first use. Disappointed with the quality.",
  },
  {
    label: "Hỏi đáp thông thường (Thấp)",
    text: "Could you please help me check if this wireless headset is compatible with Windows 11?",
  },
  {
    label: "Ngoại ngữ tiếng Việt (Gắn cờ duyệt)",
    text: "Tôi muốn yêu cầu hỗ trợ đổi trả đơn hàng giao nhầm kích cỡ.",
  },
];

const MIN_SKELETON_MS = 450;

function useCountUp(target: number, durationMs = 420): number {
  const [count, setCount] = useState(target);
  const prefersReducedMotion =
    typeof window !== "undefined" &&
    typeof window.matchMedia === "function" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  useEffect(() => {
    if (prefersReducedMotion || target <= 0) {
      setCount(target);
      return;
    }

    let rafId = 0;
    const startTime = performance.now();
    setCount(0);

    const step = (now: number) => {
      const elapsed = now - startTime;
      const t = Math.min(1, elapsed / durationMs);
      const eased = 1 - Math.pow(1 - t, 3);
      setCount(Math.round(target * eased));

      if (t < 1) {
        rafId = window.requestAnimationFrame(step);
      } else {
        setCount(target);
      }
    };

    rafId = window.requestAnimationFrame(step);
    return () => window.cancelAnimationFrame(rafId);
  }, [target, durationMs, prefersReducedMotion]);

  return prefersReducedMotion ? target : count;
}

export const TesterPage: React.FC = () => {
  const [content, setContent] = useState("");
  const [result, setResult] = useState<TicketOut | null>(null);
  const [completedSubmittedAt, setCompletedSubmittedAt] = useState(0);
  const [executionTime, setExecutionTime] = useState<number>(0);

  const triageMutation = useTriageTicket();

  useEffect(() => {
    const submittedAt = triageMutation.submittedAt;
    if (!submittedAt) return;

    const elapsed = Date.now() - submittedAt;
    const remaining = Math.max(0, MIN_SKELETON_MS - elapsed);
    const timer = window.setTimeout(() => {
      setCompletedSubmittedAt(submittedAt);
    }, remaining);

    return () => window.clearTimeout(timer);
  }, [triageMutation.submittedAt]);

  const isVisualLoading =
    triageMutation.isPending ||
    (triageMutation.submittedAt > 0 &&
      triageMutation.submittedAt !== completedSubmittedAt &&
      !triageMutation.isError);

  const animatedConfidence = useCountUp(
    !isVisualLoading && result?.confidence ? Math.round(result.confidence * 100) : 0
  );

  const handleAnalyze = (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim() || triageMutation.isPending) return;

    const startTime = performance.now();
    triageMutation.mutate(
      { content },
      {
        onSuccess: (data) => {
          setResult(data);
        },
        onSettled: () => {
          setExecutionTime(performance.now() - startTime);
        },
      }
    );
  };

  return (
    <div className="inbox-page tester-page space-y-6 p-4 pb-8 sm:p-5 sm:pb-8 lg:p-6 lg:pb-8">
      <div className="tester-header flex flex-col gap-4 border-b border-slate-200 pb-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <span className="mb-1 block text-[11px] font-bold uppercase tracking-[0.15em] text-teal-600">
            Kiểm thử quy trình
          </span>
          <h1 className="text-3xl font-bold tracking-tight text-slate-800">
            Mô phỏng kiểm thử trực tiếp
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-slate-600">
            Nhập nội dung phản hồi để kiểm tra quy trình phân tích cảm xúc và tính điểm ưu tiên.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 self-start sm:self-auto">
          <div className="flex items-center gap-2.5 rounded-xl border border-slate-200 bg-white px-3 py-2 shadow-sm">
            <span
              className="flex h-8 w-8 items-center justify-center rounded-lg bg-teal-50 text-teal-600"
              aria-hidden="true"
            >
              <Sparkles className="h-4 w-4" />
            </span>
            <div>
              <span className="block text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                MÔ HÌNH PHÂN TÍCH
              </span>
              <span className="block text-sm font-bold leading-tight text-slate-700">
                ABSA · English
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2.5 rounded-xl border border-slate-200 bg-white px-3 py-2 shadow-sm">
            <span
              className="flex h-8 w-8 items-center justify-center rounded-lg bg-teal-50 text-teal-600"
              aria-hidden="true"
            >
              <Clock className="h-4 w-4" />
            </span>
            <div>
              <span className="block text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                THỜI GIAN PHÂN TÍCH
              </span>
              <span className="block font-mono text-sm font-bold leading-tight tabular-nums text-slate-700">
                {executionTime > 1000
                  ? `~ ${(executionTime / 1000).toFixed(1)} giây`
                  : `~ ${Math.round(executionTime)} ms`}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Biểu mẫu nhập liệu */}
      <div className="tester-workbench-grid grid grid-cols-1 items-stretch gap-5 lg:grid-cols-[minmax(0,1.35fr)_minmax(340px,1fr)]">
        <div className="tester-composer-panel flex flex-col justify-between p-6 sm:p-7">
          <div className="mb-4">
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="h-5 w-1.5 rounded-full bg-teal-600" aria-hidden="true"></div>
                <h3 className="text-base font-bold text-slate-800">
                  Nội dung phản hồi khách hàng
                </h3>
              </div>
              <span className="rounded bg-slate-100 px-2 py-0.5 text-[10px] text-slate-400">
                INPUT
              </span>
            </div>
            <p className="mt-1.5 text-[13px] font-medium text-slate-500">
              Nhập văn bản tiếng Anh hoặc nạp nhanh từ danh sách kịch bản mẫu
            </p>
          </div>

          <form onSubmit={handleAnalyze} className="flex flex-1 flex-col gap-4">
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={6}
              style={{ resize: "none" }}
              aria-label="Nội dung phản hồi của khách hàng"
              placeholder="Nhập nội dung phản hồi của khách hàng bằng tiếng Anh (ví dụ: 'My order hasn't arrived after 2 weeks and I want my money back!')..."
              className="tester-textarea min-h-[176px] w-full flex-1 resize-none rounded-xl border border-slate-200 bg-slate-50/50 p-4 font-sans text-sm leading-6 text-slate-900 shadow-inner transition focus:border-teal-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-500/20"
              required
            />

            <div className="flex flex-wrap items-center justify-between gap-4 border-t border-slate-100 pt-3.5">
              <span className="tester-char-counter bg-transparent font-mono text-xs tabular-nums text-slate-400">
                {content.length} ký tự
              </span>
              <button
                type="submit"
                disabled={!content.trim() || triageMutation.isPending}
                className="tester-submit-btn inline-flex min-h-10 items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#126B67] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-55"
              >
                <svg
                  className={`tester-spin mr-0.5 h-4 w-4 animate-spin text-white ${
                    triageMutation.isPending ? "inline-block" : "hidden"
                  }`}
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="3.5"
                  />
                  <path
                    className="opacity-90"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                <Send
                  className={`tester-send-icon h-4 w-4 ${
                    triageMutation.isPending ? "hidden" : "inline-block"
                  }`}
                  aria-hidden="true"
                />
                <span>{triageMutation.isPending ? "Đang phân tích..." : "Phân tích ngay"}</span>
              </button>
            </div>
          </form>

          {triageMutation.isError && (
            <div
              role="alert"
              className="tester-error-alert mt-3.5 flex items-center gap-2.5 rounded-xl border border-[#d88479] bg-[#fff3f1] px-3.5 py-3 text-xs font-medium text-[#7f292d]"
            >
              <AlertCircle className="h-4 w-4 flex-shrink-0 text-[#a72729]" aria-hidden="true" />
              <span>Có lỗi khi gọi API triage: {triageMutation.error?.message}</span>
            </div>
          )}
        </div>

        {/* Tình huống mẫu */}
        <div className="tester-presets-panel flex flex-col p-6 sm:p-7">
          <div className="mb-4">
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="h-5 w-1.5 rounded-full bg-teal-600" aria-hidden="true"></div>
                <h3 className="text-base font-bold text-slate-800">
                  Thử nhanh tình huống mẫu
                </h3>
              </div>
              <span className="rounded bg-slate-100 px-2 py-0.5 text-[10px] text-slate-400">
                05 MẪU
              </span>
            </div>
            <p className="mt-1.5 text-[13px] font-medium text-slate-500">
              Chọn một kịch bản để điền nhanh vào khung kiểm thử
            </p>
          </div>

          <div className="tester-presets-list flex flex-1 flex-col justify-between gap-2">
            {SAMPLE_PROMPTS.map((sample, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => setContent(sample.text)}
                className={`tester-sample-btn flex items-center justify-between text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#126B67] focus-visible:ring-offset-1 ${
                  content === sample.text ? "is-active" : ""
                }`}
              >
                <span className="flex flex-1 items-center justify-between gap-2">
                  <span
                    className={`tester-sample-label text-[13px] ${
                      content === sample.text
                        ? "font-semibold text-teal-950"
                        : "font-medium text-slate-700"
                    }`}
                  >
                    {sample.label.replace(/\s*\([^)]+\)\s*$/, "")}
                  </span>
                  {sample.label.match(/\(([^)]+)\)/) && (
                    <span className="shrink-0 rounded bg-teal-50/50 px-2 py-0.5 text-[11px] text-teal-700">
                      {sample.label.match(/\(([^)]+)\)/)?.[0]}
                    </span>
                  )}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Kết quả phân tích */}
      {isVisualLoading && (
        <div
          className="tester-result-ledger tester-skeleton-ledger space-y-5"
          aria-hidden="true"
          data-testid="tester-loading-skeleton"
        >
          <div className="tester-result-header flex flex-wrap items-center justify-between gap-3 border-b border-[#dce6e4] pb-4">
            <div className="flex items-center gap-3">
              <span className="tester-sk-block h-9 w-9 rounded-[11px]" />
              <span className="tester-sk-block h-6 w-64 max-w-[70vw] rounded-lg" />
            </div>
            <span className="tester-sk-block h-7 w-20 rounded-full" />
          </div>

          <div className="tester-metric-grid grid grid-cols-1 gap-3.5 lg:grid-cols-3">
            <div className="tester-metric-card tester-skeleton-card relative flex min-h-[96px] flex-col justify-between p-5">
              <span className="tester-sk-block h-3.5 w-32 rounded-md" />
              <div className="mt-4 flex items-end justify-start">
                <span className="tester-sk-block h-7 w-36 rounded-full" />
              </div>
            </div>

            <div className="tester-metric-card tester-skeleton-card relative flex min-h-[96px] flex-col justify-between p-5">
              <span className="tester-sk-block h-3.5 w-28 rounded-md" />
              <div className="mt-4 flex items-end justify-between">
                <span className="tester-sk-block h-7 w-24 rounded-full" />
                <span className="tester-sk-block h-7 w-14 rounded-md opacity-60" />
              </div>
            </div>

            <div className="tester-metric-card tester-skeleton-card relative flex min-h-[96px] flex-col justify-between p-5">
              <span className="tester-sk-block h-3.5 w-32 rounded-md" />
              <div className="mt-4 flex items-end justify-between">
                <span className="tester-sk-block h-7 w-20 rounded-full" />
                <span className="tester-sk-block h-7 w-10 rounded-md opacity-60" />
              </div>
            </div>
          </div>

          <div className="tester-aspects-box queue-aspect-panel">
            <span className="tester-sk-block mb-3 block h-3.5 w-48 rounded-md" />
            <div className="flex flex-wrap gap-2">
              <span className="tester-sk-block h-7 w-36 rounded-full" />
              <span className="tester-sk-block h-7 w-28 rounded-full" />
              <span className="tester-sk-block h-7 w-32 rounded-full" />
            </div>
          </div>

          <div className="audit-breakdown space-y-3 border border-slate-200 bg-white p-4 shadow-sm">
            <div className="audit-breakdown-header flex items-center justify-between border-b pb-2">
              <div className="space-y-2">
                <span className="tester-sk-block block h-4 w-56 max-w-[60vw] rounded-md" />
                <span className="tester-sk-block block h-3 w-44 max-w-[50vw] rounded-md" />
              </div>
              <div className="flex flex-col items-end justify-center">
                <span className="tester-sk-block block h-7 w-16 rounded-md" />
                <span className="tester-sk-block mt-1.5 block h-3 w-14 rounded-md" />
              </div>
            </div>

            <div className="audit-contribution-track">
              <span className="tester-sk-block h-full w-full rounded-full" />
            </div>

            <div className="audit-component-grid grid grid-cols-2 gap-2 text-xs sm:grid-cols-4">
              <div>
                <span className="tester-sk-block block h-3 w-20 rounded-md" />
                <span className="tester-sk-block block h-5 w-14 rounded-md" />
              </div>
              <div>
                <span className="tester-sk-block block h-3 w-24 rounded-md" />
                <span className="tester-sk-block block h-5 w-14 rounded-md" />
              </div>
              <div>
                <span className="tester-sk-block block h-3 w-24 rounded-md" />
                <span className="tester-sk-block block h-5 w-14 rounded-md" />
              </div>
              <div>
                <span className="tester-sk-block block h-3 w-24 rounded-md" />
                <span className="tester-sk-block block h-5 w-14 rounded-md" />
              </div>
            </div>

            <div className="audit-dominant-aspect">
              <span className="tester-sk-block block h-4 w-52 rounded-md" />
            </div>

            <div className="audit-evidence">
              <div className="audit-evidence-summary">
                <span className="tester-sk-block block h-4 w-44 rounded-md" />
              </div>
            </div>
          </div>
        </div>
      )}

      {!isVisualLoading && result && (
        <div className="tester-result-ledger space-y-5">
          <div className="tester-result-header flex flex-wrap items-center justify-between gap-3 border-b border-[#dce6e4] pb-4">
            <div className="flex items-center gap-3">
              <span className="tester-result-icon" aria-hidden="true">
                <CheckCircle2 className="h-5 w-5" />
              </span>
              <h3 className="text-lg font-semibold tracking-tight text-slate-950">
                Kết quả phân tích toàn trình thành công
              </h3>
            </div>
            <span className="tester-ticket-id font-mono text-xs font-semibold tabular-nums">
              ID #{result.id}
            </span>
          </div>

          {/* Cards overview */}
          <div className="tester-metric-grid grid grid-cols-1 gap-3.5 lg:grid-cols-3">
            <div className="tester-metric-card tester-metric-priority relative flex min-h-[96px] flex-col justify-between p-5">
              <span className="block pr-8 text-xs font-semibold uppercase tracking-wider text-slate-500">
                Mức ưu tiên tính toán
              </span>
              <div className="mt-4 flex items-end justify-start">
                <PriorityBadge score={result.priority_score} />
              </div>
            </div>

            <div className="tester-metric-card tester-metric-sentiment relative flex min-h-[96px] flex-col justify-between p-5">
              <span className="block pr-8 text-xs font-semibold uppercase tracking-wider text-slate-500">
                Cảm xúc tổng thể
              </span>
              <div className="tester-metric-value mt-4 flex items-end justify-between pr-20">
                <span className="tester-value-pill rounded-full px-2.5 py-1 text-sm font-medium capitalize">
                  {result.sentiment_label || "Chưa xác định"}
                </span>
              </div>
              <span className="tester-value-mono pointer-events-none absolute bottom-4 right-5 select-none font-mono text-2xl font-black leading-none tabular-nums text-slate-700/80">
                {result.confidence && `${animatedConfidence}%`}
              </span>
            </div>

            <div className="tester-metric-card tester-metric-lang relative flex min-h-[96px] flex-col justify-between p-5">
              <span className="block pr-8 text-xs font-semibold uppercase tracking-wider text-slate-500">
                Ngôn ngữ & Cờ duyệt
              </span>
              <div className="tester-metric-value mt-4 flex items-end justify-between pr-16">
                <span className="tester-value-pill rounded-full px-2.5 py-1 text-sm font-medium">
                  {result.needs_manual_review ? "(Cần duyệt)" : "(Hợp lệ)"}
                </span>
              </div>
              <span className="tester-lang-code pointer-events-none absolute bottom-4 right-5 select-none font-mono text-2xl font-black leading-none tracking-tight text-slate-700/80">
                {result.language_flag.toUpperCase()}
              </span>
            </div>
          </div>

          {/* Aspects list */}
          <div className="tester-aspects-box queue-aspect-panel">
            <h4 className="mb-2.5 text-xs font-bold uppercase tracking-wider text-[#126B67]">
              Các khía cạnh được phát hiện:
            </h4>
            <div className="tester-aspects-chips">
              <AspectChips aspects={result.aspects} maxDisplay={10} />
            </div>
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
