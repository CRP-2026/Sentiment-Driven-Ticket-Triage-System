from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ...db.models import TicketAspect
from ...db.repository import TicketRepository
from ...db.session import get_db
from ..schemas import AspectStatItem, StatsOverviewResponse

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("/overview", response_model=StatsOverviewResponse)
def get_stats_overview(db: Session = Depends(get_db)) -> StatsOverviewResponse:
    """Thống kê tổng thể: phân bố cảm xúc, cấp ưu tiên, trạng thái vòng đời."""
    data = TicketRepository.get_stats_overview(db)
    return StatsOverviewResponse(**data)

@router.get("/aspects", response_model=list[AspectStatItem])
def get_aspects_stats(db: Session = Depends(get_db)) -> list[AspectStatItem]:
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
        AspectStatItem(aspect=r[0], sentiment=r[1], count=r[2])
        for r in rows
    ]
