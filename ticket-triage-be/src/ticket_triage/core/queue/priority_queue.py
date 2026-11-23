import heapq
import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


def _normalize_utc(dt: datetime) -> datetime:
    """Chuẩn hóa datetime sang UTC-aware để so sánh heap an toàn giữa naive và aware."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


@dataclass(order=True)
class _HeapEntry:
    neg_score: float
    sort_dt: datetime
    ticket_id: int
    created_at: datetime = field(compare=False)
    data: Any = field(compare=False, default=None)


@dataclass(frozen=True)
class QueueItem:
    ticket_id: int
    priority_score: float
    created_at: datetime
    data: Any = None


def _to_queue_item(entry: _HeapEntry) -> QueueItem:
    return QueueItem(
        ticket_id=entry.ticket_id,
        priority_score=-entry.neg_score,
        created_at=entry.created_at,
        data=entry.data,
    )


class TicketPriorityQueue:
    """Hàng đợi ưu tiên In-memory (Max-Heap) sử dụng heapq và RLock:
    - Sắp xếp theo priority_score giảm dần.
    - Tie-break FIFO: nếu đồng điểm, ticket đến trước (created_at nhỏ hơn) đứng trước.
    - Chống trùng lặp ticket_id khi push cập nhật và an toàn luồng với sync workers.
    """

    def __init__(self) -> None:
        self._heap: list[_HeapEntry] = []
        self._item_map: dict[int, _HeapEntry] = {}
        self._lock = threading.RLock()

    def _remove_unlocked(self, ticket_id: int) -> bool:
        if ticket_id not in self._item_map:
            return False
        del self._item_map[ticket_id]
        self._heap = [e for e in self._heap if e.ticket_id != ticket_id]
        heapq.heapify(self._heap)
        return True

    def push(
        self,
        ticket_id: int,
        priority_score: float,
        created_at: datetime,
        data: Any = None,
    ) -> None:
        with self._lock:
            if ticket_id in self._item_map:
                self._remove_unlocked(ticket_id)
            entry = _HeapEntry(
                neg_score=-float(priority_score),
                sort_dt=_normalize_utc(created_at),
                ticket_id=ticket_id,
                created_at=created_at,
                data=data,
            )
            heapq.heappush(self._heap, entry)
            self._item_map[ticket_id] = entry

    def pop(self) -> QueueItem | None:
        with self._lock:
            if not self._heap:
                return None
            entry = heapq.heappop(self._heap)
            self._item_map.pop(entry.ticket_id, None)
            return _to_queue_item(entry)

    def peek(self) -> QueueItem | None:
        with self._lock:
            if not self._heap:
                return None
            return _to_queue_item(self._heap[0])

    def to_sorted_list(self) -> list[QueueItem]:
        with self._lock:
            sorted_entries = sorted(self._heap)
            return [_to_queue_item(e) for e in sorted_entries]

    def size(self) -> int:
        with self._lock:
            return len(self._heap)

    def is_empty(self) -> bool:
        with self._lock:
            return len(self._heap) == 0

    def remove(self, ticket_id: int) -> bool:
        """Loại bỏ một ticket khỏi hàng đợi ưu tiên (ví dụ khi ticket đã resolved)."""
        with self._lock:
            return self._remove_unlocked(ticket_id)

    def clear(self) -> None:
        with self._lock:
            self._heap.clear()
            self._item_map.clear()
