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
