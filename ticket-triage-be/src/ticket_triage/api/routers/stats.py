from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from ...db.session import get_db
from ...db.models import TicketAspect
from ...db.repository import TicketRepository

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("/overview")
def get_stats_overview(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Thống kê tổng thể: phân bố cảm xúc, cấp ưu tiên, trạng thái vòng đời."""
    return TicketRepository.get_stats_overview(db)

@router.get("/aspects")
def get_aspects_stats(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    """Ma trận tương quan Khía cạnh x Cảm xúc (Aspect Sentiment Matrix)."""
    stmt = (
        select(
            TicketAspect.aspect,
            TicketAspect.sentiment,
            func.count(TicketAspect.id).label("count"),
        )
        .group_by(TicketAspect.aspect, TicketAspect.sentiment)
    )
    rows = db.execute(stmt).all()
    return [
        {"aspect": r[0], "sentiment": r[1], "count": r[2]}
        for r in rows
    ]
