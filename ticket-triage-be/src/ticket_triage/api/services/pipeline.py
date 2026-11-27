"""Backward-compatible façade delegating to Application TriageService."""

from sqlalchemy.orm import Session

from ...adapters.persistence.sqlalchemy_repos import SqlAlchemyTicketRepository
from ...application.triage_service import TriageService, ticket_queue_metadata
from ...core.priority.priority_engine import PriorityRules
from ...core.queue.priority_queue import TicketPriorityQueue
from ...core.sentiment.base import BaseSentimentModel
from ...core.taxonomy import Taxonomy
from ...db.models import Ticket

__all__ = ["process_ticket_pipeline", "ticket_queue_metadata"]


def process_ticket_pipeline(
    raw_text: str,
    db: Session,
    sentiment_model: BaseSentimentModel,
    priority_queue: TicketPriorityQueue | None = None,
    taxonomy: Taxonomy | None = None,
    priority_rules: PriorityRules | None = None,
    model_task: str = "absa",
    aspect_keywords: dict[str, list[str]] | None = None,
    enable_abte: bool = False,
    source: str = "direct_api",
    product_id: int | None = None,
    product_name: str | None = None,
    product_slug: str | None = None,
    user_id: int | None = None,
    author_name: str | None = None,
) -> Ticket:
    """Điều phối toàn trình qua TriageService (giữ tương thích ngược cho tests & scripts)."""
    service = TriageService(
        ticket_repo=SqlAlchemyTicketRepository(db),
        sentiment_model=sentiment_model,
        priority_queue=priority_queue,
        taxonomy=taxonomy,
        priority_rules=priority_rules,
        model_task=model_task,
        aspect_keywords=aspect_keywords,
        enable_abte=enable_abte,
    )
    return service.process_ticket(
        raw_text=raw_text,
        source=source,
        product_id=product_id,
        product_name=product_name,
        product_slug=product_slug,
        user_id=user_id,
        author_name=author_name,
    )
