from typing import Any

from sqlalchemy.orm import Session

from ...core.preprocessing.pipeline import preprocess_ticket
from ...core.priority.priority_engine import PriorityBreakdown, calculate_priority
from ...core.queue.priority_queue import TicketPriorityQueue
from ...core.sentiment.base import BaseSentimentModel
from ...core.taxonomy import Taxonomy
from ...db.models import Ticket
from ...db.repository import TicketRepository


def process_ticket_pipeline(
    raw_text: str,
    db: Session,
    sentiment_model: BaseSentimentModel,
    priority_queue: TicketPriorityQueue | None = None,
    taxonomy: Taxonomy | None = None,
) -> Ticket:
    """Điều phối toàn trình 2 bài toán:
    1. Module 1: Preprocessing + Language Validator + Keyword Pre-filter
    2. Bài toán 1: ABSA Zero-shot NLI (hoặc Mock Model)
    3. Bài toán 2: Rule-based Priority Engine
    4. Bài toán 2: Lưu SQLite và đẩy vào Max-Heap
    """
    # 1. Tiền xử lý
    pre = preprocess_ticket(raw_text)

    # 2. Xử lý ranh giới ngoại ngữ (English-only)
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

        ticket = TicketRepository.create_ticket(
            db=db,
            content=raw_text,
            processed_content=pre.clean_text,
            language_flag=pre.detected_lang,
            needs_manual_review=True,
            sentiment_label="neutral",
            confidence=pre.lang_confidence,
            low_confidence=False,
            priority_score=50.0,
            priority_level="MEDIUM",
            priority_breakdown=breakdown_dict,
            dominant_aspect="general",
            status="new",
            aspects_data=[],
        )

        if priority_queue is not None:
            priority_queue.push(ticket.id, ticket.priority_score, ticket.created_at, ticket)

        return ticket

    # 3. Tiếng Anh hợp lệ -> Kích hoạt Bài toán 1 (ABSA)
    absa_res = sentiment_model.predict(pre.clean_text, candidates=pre.candidate_aspects)
    is_low_conf = absa_res.overall.confidence < 0.50

    # 4. Trích xuất trọng số khía cạnh từ Taxonomy
    aspect_weights = None
    if taxonomy is not None:
        aspect_weights = {a.id: a.weight for a in taxonomy.get_all()}

    # 5. Kích hoạt Bài toán 2 (Priority Engine)
    breakdown: PriorityBreakdown = calculate_priority(
        result=absa_res,
        text=pre.clean_text,
        aspect_weights=aspect_weights,
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
            "terms": list(asp.terms),
        }
        for asp in absa_res.aspects
    ]

    # 6. Lưu trữ CSDL SQLite trong một transaction duy nhất
    ticket = TicketRepository.create_ticket(
        db=db,
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
        aspects_data=aspects_payload,
    )

    # 7. Đẩy vào hàng đợi ưu tiên in-memory
    if priority_queue is not None:
        priority_queue.push(ticket.id, ticket.priority_score, ticket.created_at, ticket)

    return ticket
