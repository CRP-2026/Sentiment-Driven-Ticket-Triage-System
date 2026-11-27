from fastapi import APIRouter, Depends, Query, status

from ...application.triage_service import TriageService
from ...domain.entities import UserEntity
from ...domain.exceptions import EntityNotFoundError
from ...domain.ports.repositories import TicketRepositoryPort
from ..dependencies import get_current_admin, get_ticket_repository, get_triage_service
from ..schemas import StatusUpdateIn, TicketCreateIn, TicketListResponse, TicketOut

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
@router.post("/triage", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
def triage_ticket(
    payload: TicketCreateIn,
    _admin: UserEntity = Depends(get_current_admin),
    triage_service: TriageService = Depends(get_triage_service),
) -> TicketOut:
    """Tiếp nhận ticket tiếng Anh thô, chạy toàn trình (ABSA -> Priority Engine),
    lưu CSDL và cập nhật hàng đợi Max-Heap.
    """
    ticket = triage_service.process_ticket(
        raw_text=payload.content,
        source=payload.source,
        product_id=payload.product_id,
        product_name=payload.product_name,
        product_slug=payload.product_slug,
        user_id=payload.user_id,
        author_name=payload.author_name,
    )
    return ticket  # type: ignore[return-value]


@router.get("", response_model=TicketListResponse)
@router.get("/queue", response_model=TicketListResponse)
def get_tickets(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    ticket_status: str | None = Query(None, alias="status"),
    aspect: str | None = None,
    sentiment: str | None = None,
    _admin: UserEntity = Depends(get_current_admin),
    ticket_repo: TicketRepositoryPort = Depends(get_ticket_repository),
) -> TicketListResponse:
    """Lấy danh sách ticket sắp xếp theo priority_score giảm dần."""
    tickets, total = ticket_repo.get_tickets(
        limit=limit,
        offset=offset,
        status=ticket_status,
        aspect=aspect,
        sentiment=sentiment,
    )
    return TicketListResponse(
        items=tickets,  # type: ignore[arg-type]
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket_detail(
    ticket_id: int,
    _admin: UserEntity = Depends(get_current_admin),
    ticket_repo: TicketRepositoryPort = Depends(get_ticket_repository),
) -> TicketOut:
    """Lấy thông tin chi tiết của một ticket kèm danh sách aspects và priority breakdown."""
    ticket = ticket_repo.get_by_id(ticket_id)
    if ticket is None:
        raise EntityNotFoundError(f"Ticket #{ticket_id} không tồn tại")
    return ticket  # type: ignore[return-value]


@router.patch("/{ticket_id}/status", response_model=TicketOut)
def update_ticket_status(
    ticket_id: int,
    payload: StatusUpdateIn,
    _admin: UserEntity = Depends(get_current_admin),
    triage_service: TriageService = Depends(get_triage_service),
) -> TicketOut:
    """Cập nhật trạng thái vòng đời ticket (new -> assigned -> in_progress -> resolved)."""
    status_str = payload.status.value if hasattr(payload.status, "value") else str(payload.status)
    updated = triage_service.update_ticket_status(
        ticket_id=ticket_id,
        new_status=status_str,
        assigned_to=payload.assigned_to,
    )
    return updated  # type: ignore[return-value]
