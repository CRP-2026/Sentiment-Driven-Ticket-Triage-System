import React from "react";
import { ChevronDown, LoaderCircle } from "lucide-react";
import { STATUSES } from "../../lib/constants";
import { useUpdateStatus } from "../../api/hooks";
import { StatusUpdateIn } from "../../api/schema";

interface StatusSelectProps {
  ticketId: number;
  currentStatus: string;
}

export const StatusSelect: React.FC<StatusSelectProps> = ({ ticketId, currentStatus }) => {
  const updateMutation = useUpdateStatus();

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const nextStatus = e.target.value as StatusUpdateIn["status"];
    if (nextStatus === currentStatus) return;

    updateMutation.mutate({
      id: ticketId,
      payload: { status: nextStatus },
    });
  };

  const currentConfig = STATUSES.find((s) => s.value === currentStatus) || STATUSES[0];

  return (
    <div className="min-w-36 space-y-1.5">
      <div className="queue-status-control relative inline-flex max-w-full items-center">
        <span className={`ticket-status-dot ticket-status-dot-${currentStatus}`} aria-hidden="true" />
        <select
          value={currentStatus}
          onChange={handleChange}
          disabled={updateMutation.isPending}
          className={`queue-status-pill queue-status-select h-8 max-w-full appearance-none rounded-full border py-1 pl-8 pr-8 text-xs font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#126B67] focus-visible:ring-offset-2 disabled:cursor-wait disabled:opacity-65 ${currentConfig.colorClass}`}
          aria-label="Cập nhật trạng thái xử lý"
          aria-describedby={updateMutation.isError ? `status-error-${ticketId}` : undefined}
          aria-busy={updateMutation.isPending}
        >
          {STATUSES.map((s) => (
            <option key={s.value} value={s.value} className="bg-white text-stone-800">
              {s.label}
            </option>
          ))}
        </select>
        <ChevronDown aria-hidden="true" className="pointer-events-none absolute right-2.5 h-3 w-3 text-current opacity-70" />
        {updateMutation.isPending && (
          <LoaderCircle className="ml-2 h-3.5 w-3.5 shrink-0 animate-spin text-slate-700" aria-hidden="true" />
        )}
      </div>
      {updateMutation.isError && (
        <p id={`status-error-${ticketId}`} role="alert" className="max-w-48 text-[11px] leading-4 text-red-700">
          Không thể cập nhật trạng thái. {updateMutation.error.message}
        </p>
      )}
    </div>
  );
};
