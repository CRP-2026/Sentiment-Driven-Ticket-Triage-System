from datetime import UTC, datetime

from ticket_triage.core.queue.priority_queue import TicketPriorityQueue


def test_priority_queue_highest_score_first():
    q = TicketPriorityQueue()
    now = datetime.now(UTC)

    q.push(ticket_id=1, priority_score=45.0, created_at=now)
    q.push(ticket_id=2, priority_score=85.0, created_at=now)
    q.push(ticket_id=3, priority_score=20.0, created_at=now)

    top = q.pop()
    assert top is not None
    assert top.ticket_id == 2
    assert top.priority_score == 85.0

    second = q.pop()
    assert second is not None
    assert second.ticket_id == 1

def test_priority_queue_fifo_tie_break():
    q = TicketPriorityQueue()
    t1 = datetime(2026, 10, 24, 10, 0, 0)
    t2 = datetime(2026, 10, 24, 10, 5, 0) # 5 mins later

    # Both have the same priority_score = 75.0
    q.push(ticket_id=10, priority_score=75.0, created_at=t2)
    q.push(ticket_id=20, priority_score=75.0, created_at=t1) # arrived earlier

    top = q.pop()
    assert top is not None
    assert top.ticket_id == 20 # Earliest ticket wins tie-break

    second = q.pop()
    assert second is not None
    assert second.ticket_id == 10


def test_priority_queue_deduplicates_duplicate_ticket_id():
    from datetime import UTC, datetime

    from ticket_triage.core.queue.priority_queue import TicketPriorityQueue

    queue = TicketPriorityQueue()
    ts = datetime(2026, 1, 1, 10, 0, tzinfo=UTC)

    queue.push(1, 40.0, ts, data={"status": "open"})
    queue.push(2, 70.0, ts, data={"status": "open"})
    queue.push(1, 90.0, ts, data={"status": "escalated"})

    assert queue.size() == 2
    items = queue.to_sorted_list()
    assert [item.ticket_id for item in items] == [1, 2]
    assert items[0].priority_score == 90.0
    assert items[0].data == {"status": "escalated"}


def test_priority_queue_mixed_naive_and_utc_aware_datetimes():
    from datetime import UTC, datetime, timedelta, timezone

    from ticket_triage.core.queue.priority_queue import TicketPriorityQueue

    queue = TicketPriorityQueue()
    naive_dt = datetime(2026, 1, 1, 10, 0, 0)
    offset_dt = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone(timedelta(hours=2)))
    earlier_utc_dt = datetime(2026, 1, 1, 9, 59, 0, tzinfo=UTC)

    queue.push(1, 50.0, naive_dt)
    queue.push(2, 50.0, offset_dt)
    queue.push(3, 50.0, earlier_utc_dt)

    sorted_items = queue.to_sorted_list()
    assert [item.ticket_id for item in sorted_items] == [3, 1, 2]
    assert queue.pop().created_at.tzinfo == UTC
    assert queue.pop().created_at.tzinfo is None
    assert queue.pop().created_at.tzinfo == timezone(timedelta(hours=2))


def test_priority_queue_thread_safety():
    from concurrent.futures import ThreadPoolExecutor
    from datetime import UTC, datetime

    from ticket_triage.core.queue.priority_queue import TicketPriorityQueue

    queue = TicketPriorityQueue()

    def worker(worker_idx: int) -> None:
        base_id = worker_idx * 100
        for offset in range(40):
            tid = base_id + offset
            ts = datetime(2026, 1, 1, 12, offset % 60, tzinfo=UTC)
            queue.push(tid, float(offset % 10), ts, data={"id": tid})
            if offset % 4 == 0:
                queue.remove(tid)
            elif offset % 5 == 0:
                queue.peek()
                queue.to_sorted_list()

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(worker, i) for i in range(4)]
        for future in futures:
            future.result()

    # Each of 4 workers inserts 40 ids and removes multiples of 4 (10 ids) => 120 remaining
    assert queue.size() == 120
    scores = [item.priority_score for item in queue.to_sorted_list()]
    assert scores == sorted(scores, reverse=True)
