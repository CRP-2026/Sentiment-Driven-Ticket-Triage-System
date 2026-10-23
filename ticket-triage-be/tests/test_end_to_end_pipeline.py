from ticket_triage.api.services.pipeline import process_ticket_pipeline
from ticket_triage.core.sentiment.mock import MockSentimentModel
from ticket_triage.core.queue.priority_queue import TicketPriorityQueue
from ticket_triage.core.taxonomy import Taxonomy

def test_full_e2e_pipeline_english(in_memory_db, sample_taxonomy):
    model = MockSentimentModel()
    queue = TicketPriorityQueue()
    raw = "My delivery is 15 days late and package is damaged! Urgent help needed."

    ticket = process_ticket_pipeline(
        raw_text=raw,
        db=in_memory_db,
        sentiment_model=model,
        priority_queue=queue,
        taxonomy=sample_taxonomy,
    )

    assert ticket.id is not None
    assert ticket.language_flag == "en"
    assert ticket.needs_manual_review is False
    assert ticket.priority_score > 0
    assert queue.size() == 1
    top = queue.peek()
    assert top.ticket_id == ticket.id

def test_full_e2e_pipeline_non_english(in_memory_db, sample_taxonomy):
    model = MockSentimentModel()
    queue = TicketPriorityQueue()
    raw = "Tôi cần trợ giúp đổi sản phẩm bị lỗi."

    ticket = process_ticket_pipeline(
        raw_text=raw,
        db=in_memory_db,
        sentiment_model=model,
        priority_queue=queue,
        taxonomy=sample_taxonomy,
    )

    assert ticket.language_flag != "en"
    assert ticket.needs_manual_review is True
    assert ticket.priority_score == 50.0
    assert queue.size() == 1
