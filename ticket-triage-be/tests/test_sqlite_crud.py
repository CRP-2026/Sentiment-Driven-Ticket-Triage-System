from ticket_triage.db.repository import TicketRepository
from ticket_triage.db.models import Ticket

def test_create_ticket_with_aspects(in_memory_db):
    aspects = [
        {"aspect": "shipping", "sentiment": "negative", "confidence": 0.90},
        {"aspect": "refund_payment", "sentiment": "negative", "confidence": 0.85},
    ]
    ticket = TicketRepository.create_ticket(
        db=in_memory_db,
        content="Package lost and no refund.",
        processed_content="Package lost and no refund.",
        language_flag="en",
        priority_score=75.0,
        priority_level="CRITICAL",
        aspects_data=aspects,
    )

    assert ticket.id is not None
    assert len(ticket.aspects) == 2
    assert ticket.aspects[0].aspect in ["shipping", "refund_payment"]

def test_cascade_delete(in_memory_db):
    ticket = TicketRepository.create_ticket(
        db=in_memory_db,
        content="Test delete cascade",
        aspects_data=[{"aspect": "general", "sentiment": "neutral", "confidence": 0.80}],
    )
    t_id = ticket.id

    in_memory_db.delete(ticket)
    in_memory_db.commit()

    reloaded = TicketRepository.get_by_id(in_memory_db, t_id)
    assert reloaded is None
