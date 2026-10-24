import React, { useState } from "react";
import { TicketOut } from "../../api/schema";
import { PriorityBadge } from "./PriorityBadge";
import { AspectChips } from "./AspectChips";
import { StatusSelect } from "./StatusSelect";
import { PriorityBreakdown } from "./PriorityBreakdown";
import { formatDate } from "../../lib/format";
import { ChevronRight, Globe, AlertCircle } from "lucide-react";

interface TicketTableProps {
  tickets: TicketOut[];
  isLoading?: boolean;
}

export const TicketTable: React.FC<TicketTableProps> = ({ tickets, isLoading }) => {
  const [selectedTicket, setSelectedTicket] = useState<TicketOut | null>(null);

  if (isLoading) {
    return (
      <div className="p-8 text-center text-slate-500 bg-white rounded-xl border border-slate-200">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-500 border-t-transparent mb-3" />
        <p className="text-sm">Đang tải danh sách hàng đợi ưu tiên...</p>
      </div>
    );
  }

  if (tickets.length === 0) {
    return (
      <div className="p-12 text-center text-slate-500 bg-white rounded-xl border border-slate-200">
        <AlertCircle className="w-10 h-10 mx-auto text-slate-400 mb-2" />
        <h3 className="text-base font-semibold text-slate-800">Không có ticket nào trong hàng đợi</h3>
        <p className="text-sm text-slate-500 mt-1">Hãy thử đổi bộ lọc hoặc thêm ticket mới từ Live Tester.</p>
      </div>
    );
  }

  return (
    <>
      <div className="overflow-x-auto bg-white rounded-xl border border-slate-200 shadow-sm">
        <table className="w-full text-left text-sm text-slate-600 border-collapse">
          <thead className="bg-slate-50 border-b border-slate-200 text-xs text-slate-500 uppercase tracking-wider font-semibold">
            <tr>
              <th className="py-3 px-4 w-16">ID</th>
              <th className="py-3 px-4 w-36">Mức ưu tiên</th>
              <th className="py-3 px-4">Nội dung phản hồi CSKH</th>
              <th className="py-3 px-4 w-56">Khía cạnh (ABSA)</th>
              <th className="py-3 px-4 w-36">Trạng thái</th>
              <th className="py-3 px-4 w-32">Thời gian</th>
              <th className="py-3 px-4 w-12 text-center">Chi tiết</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {tickets.map((t) => (
              <tr
                key={t.id}
                onClick={() => setSelectedTicket(t)}
                className="hover:bg-slate-50/80 cursor-pointer transition-colors"
              >
                <td className="py-3 px-4 font-mono text-xs text-slate-400">#{t.id}</td>
                <td className="py-3 px-4">
                  <PriorityBadge score={t.priority_score} />
                </td>
                <td className="py-3 px-4">
                  <div className="flex items-center gap-2">
                    {t.language_flag !== "en" && (
                      <span className="flex-shrink-0 inline-flex items-center gap-1 text-[11px] px-1.5 py-0.5 rounded bg-purple-100 text-purple-700 font-medium">
                        <Globe className="w-3 h-3" />
                        {t.language_flag.toUpperCase()}
                      </span>
                    )}
                    {t.needs_manual_review && (
                      <span className="flex-shrink-0 inline-flex items-center gap-1 text-[11px] px-1.5 py-0.5 rounded bg-amber-100 text-amber-700 font-medium">
                        <AlertCircle className="w-3 h-3" />
                        Duyệt
                      </span>
                    )}
                    <span className="line-clamp-2 text-slate-800 text-xs sm:text-sm font-medium">
                      {t.content}
                    </span>
                  </div>
                </td>
                <td className="py-3 px-4">
                  <AspectChips aspects={t.aspects} />
                </td>
                <td className="py-3 px-4" onClick={(e) => e.stopPropagation()}>
                  <StatusSelect ticketId={t.id} currentStatus={t.status} />
                </td>
                <td className="py-3 px-4 text-xs text-slate-400 whitespace-nowrap">
                  {formatDate(t.created_at)}
                </td>
                <td className="py-3 px-4 text-center text-slate-400">
                  <ChevronRight className="w-4 h-4 inline" />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Modal chi tiết ticket và giải trình điểm */}
      {selectedTicket && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 shadow-xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between border-b pb-3">
              <div>
                <span className="text-xs font-mono text-slate-400">Ticket #{selectedTicket.id}</span>
                <h3 className="text-base font-semibold text-slate-900">Chi tiết phản hồi và Phân tích</h3>
              </div>
              <button
                onClick={() => setSelectedTicket(null)}
                className="text-slate-400 hover:text-slate-600 p-1 text-lg font-bold"
              >
                ✕
              </button>
            </div>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
              <span className="text-xs font-semibold text-slate-500 uppercase block mb-1">Nội dung thô của khách hàng:</span>
              <p className="text-sm text-slate-800 leading-relaxed">{selectedTicket.content}</p>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <PriorityBadge score={selectedTicket.priority_score} />
              <AspectChips aspects={selectedTicket.aspects} maxDisplay={5} />
            </div>

            <PriorityBreakdown
              breakdown={selectedTicket.priority_breakdown}
              dominantAspect={selectedTicket.dominant_aspect}
              needsManualReview={selectedTicket.needs_manual_review}
            />

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedTicket(null)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-medium rounded-lg transition-colors"
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
