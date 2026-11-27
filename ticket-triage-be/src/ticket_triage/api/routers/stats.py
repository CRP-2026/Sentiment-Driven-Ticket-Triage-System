from fastapi import APIRouter, Depends

from ...domain.entities import UserEntity
from ...domain.ports.repositories import TicketRepositoryPort
from ..dependencies import get_current_admin, get_ticket_repository
from ..schemas import AspectStatItem, StatsOverviewResponse

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/overview", response_model=StatsOverviewResponse)
def get_stats_overview(
    _admin: UserEntity = Depends(get_current_admin),
    ticket_repo: TicketRepositoryPort = Depends(get_ticket_repository),
) -> StatsOverviewResponse:
    """Thống kê tổng thể: phân bố cảm xúc, cấp ưu tiên, trạng thái vòng đời."""
    data = ticket_repo.get_stats_overview()
    return StatsOverviewResponse(**data)


@router.get("/aspects", response_model=list[AspectStatItem])
def get_aspects_stats(
    _admin: UserEntity = Depends(get_current_admin),
    ticket_repo: TicketRepositoryPort = Depends(get_ticket_repository),
) -> list[AspectStatItem]:
    """Ma trận tương quan Khía cạnh x Cảm xúc (Aspect Sentiment Matrix)."""
    rows = ticket_repo.get_aspect_matrix()
    return [
        AspectStatItem(aspect=aspect, sentiment=sentiment, count=count)
        for aspect, sentiment, count in rows
    ]
