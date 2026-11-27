"""In-process TriageGatewayPort adapter for Modular Monolith deployments."""

from ...application.triage_service import TriageService
from ...domain.entities import (
    AspectObservation,
    TriageDispatchRequest,
    TriageDispatchResult,
)


class LocalTriageGateway:
    """Dispatches storefront review content directly to TriageService in-process."""

    def __init__(self, triage_service: TriageService) -> None:
        self._triage_service = triage_service

    def dispatch_ticket(self, request: TriageDispatchRequest) -> TriageDispatchResult:
        ticket = self._triage_service.process_ticket(
            raw_text=request.content,
            source=request.source,
            product_id=request.product_id,
            product_name=request.product_name,
            product_slug=request.product_slug,
            user_id=request.user_id,
            author_name=request.author_name,
        )
        aspects = tuple(
            AspectObservation(
                aspect=asp.aspect,
                sentiment=asp.sentiment,
                confidence=float(asp.confidence),
                terms=tuple(asp.terms or ()),
            )
            for asp in getattr(ticket, "aspects", [])
        )
        return TriageDispatchResult(
            ticket_id=int(ticket.id),
            sentiment_label=ticket.sentiment_label,
            confidence=float(ticket.confidence) if ticket.confidence is not None else None,
            priority_score=float(ticket.priority_score),
            priority_level=str(ticket.priority_level),
            dominant_aspect=ticket.dominant_aspect,
            needs_manual_review=bool(ticket.needs_manual_review),
            aspects=aspects,
        )
