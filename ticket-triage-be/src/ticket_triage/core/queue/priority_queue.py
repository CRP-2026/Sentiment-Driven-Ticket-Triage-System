import heapq
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

@dataclass(order=True)
class _HeapEntry:
    neg_score: float
    created_at: datetime
    ticket_id: int
    data: Any = field(compare=False, default=None)

@dataclass(frozen=True)
class QueueItem:
    ticket_id: int
    priority_score: float
    created_at: datetime
    data: Any = None

class TicketPriorityQueue:
    """Hàng đợi ưu tiên In-memory (Max-Heap) sử dụng heapq:
    - Sắp xếp theo priority_score giảm dần.
    - Tie-break FIFO: nếu đồng điểm, ticket đến trước (created_at nhỏ hơn) đứng trước.
    """

    def __init__(self):
        self._heap: list[_HeapEntry] = []
        self._item_map: dict[int, _HeapEntry] = {}

    def push(self, ticket_id: int, priority_score: float, created_at: datetime, data: Any = None) -> None:
        entry = _HeapEntry(
            neg_score=-float(priority_score),
            created_at=created_at,
            ticket_id=ticket_id,
            data=data,
        )
        heapq.heappush(self._heap, entry)
        self._item_map[ticket_id] = entry

    def pop(self) -> QueueItem | None:
        if not self._heap:
            return None
        entry = heapq.heappop(self._heap)
        self._item_map.pop(entry.ticket_id, None)
        return QueueItem(
            ticket_id=entry.ticket_id,
            priority_score=-entry.neg_score,
            created_at=entry.created_at,
            data=entry.data,
        )

    def peek(self) -> QueueItem | None:
        if not self._heap:
            return None
        entry = self._heap[0]
        return QueueItem(
            ticket_id=entry.ticket_id,
            priority_score=-entry.neg_score,
            created_at=entry.created_at,
            data=entry.data,
        )

    def to_sorted_list(self) -> list[QueueItem]:
        sorted_entries = sorted(self._heap)
        return [
            QueueItem(
                ticket_id=e.ticket_id,
                priority_score=-e.neg_score,
                created_at=e.created_at,
                data=e.data,
            )
            for e in sorted_entries
        ]

    def size(self) -> int:
        return len(self._heap)

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def clear(self) -> None:
        self._heap.clear()
        self._item_map.clear()
