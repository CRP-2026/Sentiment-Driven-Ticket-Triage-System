"""Core Ticket Triage orchestration service decoupled via DIP Ports."""

from typing import Any

from ..core.preprocessing.pipeline import preprocess_ticket
from ..core.priority.priority_engine import (
    PriorityBreakdown,
    PriorityRules,
    calculate_priority,
    classify_priority_level,
    load_priority_rules,
)
from ..core.queue.state_manager import InvalidStateTransitionError
from ..core.sentiment.abte import extract_aspect_terms
from ..core.sentiment.base import AbsaResult
from ..core.taxonomy import Taxonomy
from ..domain.exceptions import DomainError, EntityNotFoundError
from ..domain.ports.repositories import TicketRepositoryPort
from ..domain.ports.triage import PriorityQueuePort, SentimentAnalyzerPort


def ticket_queue_metadata(ticket: Any) -> dict[str, int | str | None]:
    """Build lightweight primitive metadata for priority heap storage (detached from ORM session)."""
    return {
        "id": ticket.id,
        "priority_level": ticket.priority_level,
        "status": ticket.status,
        "dominant_aspect": ticket.dominant_aspect,
    }


class TriageService:
    """Orchestrates Preprocess -> ABSA -> Priority Engine -> Persistence -> Priority Queue."""

    def __init__(
        self,
        ticket_repo: TicketRepositoryPort,
        sentiment_model: SentimentAnalyzerPort,
        priority_queue: PriorityQueuePort | None = None,
        taxonomy: Taxonomy | None = None,
        priority_rules: PriorityRules | None = None,
        model_task: str = "absa",
        aspect_keywords: dict[str, list[str]] | None = None,
        enable_abte: bool = False,
    ) -> None:
        self._ticket_repo = ticket_repo
        self._sentiment_model = sentiment_model
        self._priority_queue = priority_queue
        self._taxonomy = taxonomy
        self._priority_rules = priority_rules
        self._model_task = model_task
        self._aspect_keywords = aspect_keywords
        self._enable_abte = enable_abte

    def process_ticket(
        self,
        raw_text: str,
        *,
        source: str = "direct_api",
        product_id: int | None = None,
        product_name: str | None = None,
        product_slug: str | None = None,
        user_id: int | None = None,
        author_name: str | None = None,
    ) -> Any:
        # 1. Preprocessing + Language Guard + Keyword Prefilter
        pre = preprocess_ticket(raw_text, aspect_keywords=self._aspect_keywords)

        # 2. Non-English boundary -> skip AI model, assign safe floor 50.0 + manual review
        if not pre.is_english:
            breakdown_dict = {
                "score": 50.0,
                "base": 50.0,
                "urgency_bonus": 0.0,
                "intensity_bonus": 0.0,
                "aspect_bonus": 0.0,
                "reasons": [
                    f"Phát hiện ngoại ngữ ({pre.detected_lang}), gắn cờ xem xét thủ công: điểm sàn 50.0"
                ],
            }
            ticket = self._ticket_repo.create_ticket(
                content=raw_text,
                processed_content=pre.clean_text,
                language_flag=pre.detected_lang,
                needs_manual_review=True,
                sentiment_label="neutral",
                confidence=pre.lang_confidence,
                low_confidence=False,
                priority_score=50.0,
                priority_level=classify_priority_level(
                    50.0, self._priority_rules or load_priority_rules()
                ),
                priority_breakdown=breakdown_dict,
                dominant_aspect="general",
                status="new",
                source=source,
                product_id=product_id,
                product_name=product_name,
                product_slug=product_slug,
                user_id=user_id,
                author_name=author_name,
                aspects_data=[],
            )
            if self._priority_queue is not None:
                self._priority_queue.push(
                    ticket.id,
                    ticket.priority_score,
                    ticket.created_at,
                    ticket_queue_metadata(ticket),
                )
            return ticket

        # 3. English valid -> ABSA (or document-level fallback)
        task_mode = (self._model_task or "absa").strip().lower()
        if task_mode == "document":
            raw_res = self._sentiment_model.predict(pre.clean_text, candidates=[])
            absa_res = AbsaResult(overall=raw_res.overall, aspects=[])
        else:
            absa_res = self._sentiment_model.predict(
                pre.clean_text, candidates=pre.candidate_aspects
            )
        is_low_conf = absa_res.overall.confidence < 0.50

        # 4. Aspect weights from Taxonomy
        aspect_weights = (
            {a.id: a.weight for a in self._taxonomy.get_all()}
            if self._taxonomy is not None
            else None
        )

        # 5. Rule-based Priority Engine
        breakdown: PriorityBreakdown = calculate_priority(
            result=absa_res,
            text=pre.clean_text,
            aspect_weights=aspect_weights,
            rules=self._priority_rules,
        )
        breakdown_dict = {
            "score": breakdown.score,
            "base": breakdown.base,
            "urgency_bonus": breakdown.urgency_bonus,
            "intensity_bonus": breakdown.intensity_bonus,
            "aspect_bonus": breakdown.aspect_bonus,
            "reasons": breakdown.reasons,
        }

        aspects_payload: list[dict[str, Any]] = [
            {
                "aspect": asp.aspect,
                "sentiment": asp.sentiment,
                "confidence": asp.confidence,
                "terms": (
                    list(asp.terms)
                    if asp.terms or not self._enable_abte
                    else list(
                        extract_aspect_terms(
                            pre.clean_text,
                            asp.aspect,
                            aspect_keywords=self._aspect_keywords,
                        )
                    )
                ),
            }
            for asp in absa_res.aspects
        ]

        # 6. Persist atomically via TicketRepositoryPort
        ticket = self._ticket_repo.create_ticket(
            content=raw_text,
            processed_content=pre.clean_text,
            language_flag="en",
            needs_manual_review=pre.needs_manual_review or is_low_conf,
            sentiment_label=absa_res.overall.label,
            confidence=absa_res.overall.confidence,
            low_confidence=is_low_conf,
            priority_score=breakdown.score,
            priority_level=breakdown.level,
            priority_breakdown=breakdown_dict,
            dominant_aspect=breakdown.dominant_aspect,
            status="new",
            source=source,
            product_id=product_id,
            product_name=product_name,
            product_slug=product_slug,
            user_id=user_id,
            author_name=author_name,
            aspects_data=aspects_payload,
        )

        # 7. Sync in-memory priority queue
        if self._priority_queue is not None:
            self._priority_queue.push(
                ticket.id,
                ticket.priority_score,
                ticket.created_at,
                ticket_queue_metadata(ticket),
            )

        return ticket

    def update_ticket_status(
        self,
        ticket_id: int,
        new_status: str,
        assigned_to: str | None = None,
    ) -> Any:
        """Transition ticket lifecycle state and synchronize the in-memory PriorityQueue."""
        existing = self._ticket_repo.get_by_id(ticket_id)
        if existing is None:
            raise EntityNotFoundError(f"Ticket #{ticket_id} không tồn tại")

        old_status = existing.status
        try:
            updated = self._ticket_repo.update_status(
                ticket_id=ticket_id,
                new_status=new_status,
                assigned_to=assigned_to,
            )
        except InvalidStateTransitionError as exc:
            raise DomainError(str(exc)) from exc

        if updated is None:
            raise EntityNotFoundError(f"Ticket #{ticket_id} không tồn tại")

        if self._priority_queue is not None:
            if updated.status == "resolved":
                self._priority_queue.remove(ticket_id)
            elif old_status == "resolved" and updated.status != "resolved":
                self._priority_queue.push(
                    updated.id,
                    updated.priority_score,
                    updated.created_at,
                    ticket_queue_metadata(updated),
                )

        return updated
