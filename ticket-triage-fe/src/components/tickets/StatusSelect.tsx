import React from "react";
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
    <div className="relative inline-block">
      <select
        value={currentStatus}
        onChange={handleChange}
        disabled={updateMutation.isPending}
        className={`text-xs rounded-md px-2.5 py-1 border font-medium cursor-pointer transition-colors focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-blue-500 ${currentConfig.colorClass}`}
        aria-label="Cập nhật trạng thái xử lý"
      >
        {STATUSES.map((s) => (
          <option key={s.value} value={s.value} className="bg-white text-slate-800">
            {s.label}
          </option>
        ))}
      </select>
    </div>
  );
};
