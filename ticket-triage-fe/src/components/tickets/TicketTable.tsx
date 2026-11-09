import React, { useEffect, useRef, useState } from "react";
import { TicketOut } from "../../api/schema";
import { PriorityBadge } from "./PriorityBadge";
import { AspectChips } from "./AspectChips";
import { StatusSelect } from "./StatusSelect";
import { PriorityBreakdown } from "./PriorityBreakdown";
import { formatDate } from "../../lib/format";
import { AlertCircle, AlertTriangle, ChevronRight, Globe } from "lucide-react";

const criticalPhrases = ["urgent", "immediately", "asap", "lawsuit", "sue", "lawyer", "fraud", "scam", "chargeback", "stolen"];
const highPhrases = ["broken", "refund", "cancel", "not working", "never received", "dispute", "charged twice", "missing", "damaged", "overcharged"];

const renderHighlightedContent = (content: string, reasons: string[] = []) => {
  const phrases = reasons.flatMap((reason) => Array.from(reason.matchAll(/'([^']+)'/g), (match) => match[1]));
  const ranges: { start: number; end: number; phrase: string; level: string }[] = [];
  const normalizedContent = content.toLowerCase();

  phrases.forEach((phrase) => {
    const normalizedPhrase = phrase.toLowerCase();
    let start = normalizedContent.indexOf(normalizedPhrase);
    while (start !== -1) {
      const level = criticalPhrases.includes(normalizedPhrase)
        ? "critical"
        : highPhrases.includes(normalizedPhrase)
          ? "high"
          : "aspect";
      ranges.push({ start, end: start + phrase.length, phrase: content.slice(start, start + phrase.length), level });
      start = normalizedContent.indexOf(normalizedPhrase, start + phrase.length);
    }
  });

  ranges.sort((a, b) => a.start - b.start || b.end - a.end);
  const nonOverlapping = ranges.reduce<typeof ranges>((accepted, range) => {
    if (accepted.length === 0 || range.start >= accepted[accepted.length - 1].end) accepted.push(range);
    return accepted;
  }, []);
  if (nonOverlapping.length === 0) return content;

  const nodes: React.ReactNode[] = [];
  let cursor = 0;
  nonOverlapping.forEach((range, index) => {
    if (range.start > cursor) nodes.push(content.slice(cursor, range.start));
    nodes.push(<mark className={`ticket-content-highlight ticket-content-${range.level}`} key={`${range.start}-${index}`}>{range.phrase}</mark>);
    cursor = range.end;
  });
  if (cursor < content.length) nodes.push(content.slice(cursor));
  return nodes;
};

interface TicketTableProps {
  tickets: TicketOut[];
  isLoading?: boolean;
  isFetching?: boolean;
}

export const TicketTable: React.FC<TicketTableProps> = ({ tickets, isLoading, isFetching = false }) => {
  const [selectedTicket, setSelectedTicket] = useState<TicketOut | null>(null);
  const dialogRef = useRef<HTMLDivElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const triggerRef = useRef<HTMLButtonElement | null>(null);

  useEffect(() => {
    if (!selectedTicket) {
      triggerRef.current?.focus();
      return;
    }

    const dialog = dialogRef.current;
    closeButtonRef.current?.focus();

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        setSelectedTicket(null);
        return;
      }

      if (event.key === "Tab" && dialog) {
        const focusable = dialog.querySelectorAll<HTMLElement>(
          'button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
        );
        if (focusable.length === 0) return;

        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [selectedTicket]);

  const openTicket = (ticket: TicketOut, trigger: HTMLButtonElement) => {
    triggerRef.current = trigger;
    setSelectedTicket(ticket);
  };

  const closeTicket = () => setSelectedTicket(null);

  if (isLoading) {
    return (
      <div className="border-y border-slate-300 bg-white px-6 py-14 text-center">
        <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-[3px] border-slate-700 border-t-transparent" />
        <p className="text-sm font-medium text-slate-600">Đang tải danh sách hàng đợi ưu tiên...</p>
      </div>
    );
  }

  if (tickets.length === 0) {
    return (
      <div className="border-y border-slate-300 bg-white px-6 py-14 text-center">
        <AlertCircle className="mx-auto mb-3 h-8 w-8 text-slate-400" />
        <h3 className="text-base font-semibold text-slate-800">Không có ticket nào trong hàng đợi</h3>
        <p className="mt-1.5 text-sm text-slate-500">Hãy thử đổi bộ lọc hoặc thêm yêu cầu mới từ trang Kiểm thử trực tiếp.</p>
      </div>
    );
  }

  return (
    <>
      <div className={`queue-table-frame overflow-hidden ${isFetching ? "queue-refresh" : ""}`}>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left text-sm text-slate-700">
            <caption className="sr-only">Danh sách yêu cầu được sắp xếp theo điểm ưu tiên, cao nhất trước</caption>
            <thead className="border-b border-slate-300 bg-slate-100 text-xs font-semibold text-slate-700">
              <tr>
                <th scope="col" className="w-20 px-4 py-3">Mã</th>
                <th scope="col" className="w-52 px-4 py-3">Ưu tiên</th>
                <th scope="col" className="min-w-[280px] px-4 py-3">Nội dung khách hàng</th>
                <th scope="col" className="w-48 px-4 py-3">Khía cạnh</th>
                <th scope="col" className="w-44 px-4 py-3">Trạng thái</th>
                <th scope="col" className="w-36 px-4 py-3">Thời gian</th>
                <th scope="col" className="w-14 px-4 py-3 text-center"><span className="sr-only">Chi tiết</span></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#e8eeef]">
              {tickets.map((t) => (
                <tr
                  key={t.id}
                  data-priority={t.priority_level}
                  tabIndex={0}
                  aria-label={`Ticket số ${t.id}, nhấn Enter để xem chi tiết`}
                  onClick={(event) => {
                    if ((event.target as HTMLElement).closest("button, select")) return;
                    const trigger = event.currentTarget.querySelector("button");
                    if (trigger) openTicket(t, trigger);
                  }}
                  onKeyDown={(event) => {
                    if (event.target !== event.currentTarget) return;
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      const trigger = event.currentTarget.querySelector("button");
                      if (trigger) openTicket(t, trigger);
                    }
                  }}
                  className="group cursor-pointer transition-colors duration-150 hover:bg-slate-50 focus-visible:bg-slate-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-[#126B67]"
                >
                  <td className="whitespace-nowrap px-4 py-3 align-top font-mono text-xs tabular-nums text-slate-500">#{t.id}</td>
                  <td className="px-4 py-3 align-top">
                    <PriorityBadge score={t.priority_score} />
                  </td>
                  <td className="px-4 py-3 align-top">
                    <div className="flex flex-wrap items-start gap-1.5">
                      {t.language_flag !== "en" && (
                        <span className="inline-flex shrink-0 items-center gap-1 rounded-sm border border-slate-300 bg-slate-100 px-1.5 py-0.5 text-[10px] font-medium text-slate-700">
                          <Globe className="h-3 w-3" />
                          {t.language_flag.toUpperCase()}
                        </span>
                      )}
                      {t.needs_manual_review && (
                        <span className="inline-flex shrink-0 items-center gap-1 rounded-sm border border-amber-300 bg-amber-50 px-1.5 py-0.5 text-[10px] font-medium text-amber-900">
                          <AlertCircle className="h-3 w-3" />
                          Cần duyệt
                        </span>
                      )}
                      {t.low_confidence && (
                        <span className="inline-flex shrink-0 items-center gap-1 rounded-sm border border-orange-300 bg-orange-50 px-1.5 py-0.5 text-[10px] font-medium text-orange-900">
                          <AlertTriangle className="h-3 w-3" />
                          Độ tin cậy thấp
                        </span>
                      )}
                    </div>
                    <p className="mt-1 line-clamp-2 text-[13px] font-medium leading-5 text-slate-900">{t.content}</p>
                  </td>
                  <td className="px-4 py-3 align-top"><AspectChips aspects={t.aspects} /></td>
                  <td className="px-4 py-3 align-top"><StatusSelect ticketId={t.id} currentStatus={t.status} /></td>
                  <td className="whitespace-nowrap px-4 py-3 align-top text-xs tabular-nums text-slate-500">{formatDate(t.created_at)}</td>
                  <td className="px-4 py-3 text-center align-top">
                    <button
                      type="button"
                      onClick={(event) => openTicket(t, event.currentTarget)}
                      aria-label={`Xem chi tiết ticket số ${t.id}`}
                      className="inline-flex h-8 w-8 items-center justify-center rounded-md text-slate-500 transition-colors duration-150 hover:bg-slate-200 hover:text-slate-950 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#126B67] focus-visible:ring-offset-2"
                    >
                      <ChevronRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {selectedTicket && (
        <div
          className="ticket-dialog-overlay fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) closeTicket();
          }}
        >
          <div
            ref={dialogRef}
            role="dialog"
            aria-modal="true"
            aria-labelledby="ticket-dialog-title"
            tabIndex={-1}
            className="ticket-dialog max-h-[min(90vh,900px)] w-full max-w-2xl space-y-5 overflow-y-auto border border-slate-300 bg-white p-5 shadow-2xl outline-none sm:p-6"
          >
            <div className="ticket-dialog-header flex items-start justify-between gap-4 border-b border-slate-300 pb-4">
              <div>
                <span className="ticket-dialog-id font-mono text-xs font-medium text-slate-500">Yêu cầu #{selectedTicket.id}</span>
                <h2 id="ticket-dialog-title" className="mt-1 text-lg font-semibold text-slate-950">Chi tiết ticket và phân tích</h2>
              </div>
              <button
                ref={closeButtonRef}
                type="button"
                onClick={closeTicket}
                aria-label="Đóng chi tiết ticket"
                className="ticket-dialog-close inline-flex h-9 w-9 shrink-0 items-center justify-center rounded text-slate-600 hover:bg-slate-100 hover:text-slate-950 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#126B67]"
              >
                <span aria-hidden="true" className="text-xl leading-none">×</span>
              </button>
            </div>

            <div className="ticket-original border-l-2 border-slate-400 bg-slate-50 px-4 py-3">
              <span className="mb-2 block text-xs font-semibold text-slate-600">Nội dung gốc của khách hàng</span>
              <p className="ticket-original-content whitespace-pre-wrap text-sm leading-6 text-slate-900">
                {renderHighlightedContent(selectedTicket.content, selectedTicket.priority_breakdown?.reasons)}
              </p>
            </div>

            <div className="ticket-dialog-metadata flex flex-wrap items-center gap-3">
              <PriorityBadge score={selectedTicket.priority_score} />
              <AspectChips aspects={selectedTicket.aspects} maxDisplay={5} />
            </div>

            <PriorityBreakdown
              breakdown={selectedTicket.priority_breakdown}
              dominantAspect={selectedTicket.dominant_aspect}
              needsManualReview={selectedTicket.needs_manual_review}
            />

            <div className="ticket-dialog-footer flex justify-end border-t border-slate-300 pt-4">
              <button
                type="button"
                onClick={closeTicket}
                className="rounded-lg bg-[#126B67] px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#0d514e] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#126B67] focus-visible:ring-offset-2"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
