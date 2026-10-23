from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from ...db.session import get_db
from ...db.repository import TicketRepository
from ...core.queue.state_manager import InvalidStateTransitionError
from ..schemas import TicketCreateIn, TicketOut, TicketListResponse, StatusUpdateIn
from ..services.pipeline import process_ticket_pipeline

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
@router.post("/triage", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
def triage_ticket(
    payload: TicketCreateIn,
    request: Request,
    db: Session = Depends(get_db),
) -> TicketOut:
    """Tiếp nhận ticket tiếng Anh thô, chạy toàn trình (ABSA -> Priority Engine),
    lưu CSDL SQLite và cập nhật hàng đợi Max-Heap.
    """
    model = request.app.state.sentiment_model
    queue = request.app.state.priority_queue
    taxonomy = request.app.state.taxonomy

    ticket = process_ticket_pipeline(
        raw_text=payload.content,
        db=db,
        sentiment_model=model,
        priority_queue=queue,
        taxonomy=taxonomy,
    )
    return ticket # type: ignore

@router.get("", response_model=TicketListResponse)
@router.get("/queue", response_model=TicketListResponse)
def get_tickets(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    ticket_status: str | None = Query(None, alias="status"),
    aspect: str | None = None,
    sentiment: str | None = None,
    db: Session = Depends(get_db),
) -> TicketListResponse:
    """Lấy danh sách ticket từ CSDL SQLite sắp xếp theo priority_score giảm dần."""
    tickets, total = TicketRepository.get_tickets(
        db=db,
        limit=limit,
        offset=offset,
        status=ticket_status,
        aspect=aspect,
        sentiment=sentiment,
    )
    return TicketListResponse(
        items=tickets, # type: ignore
        total=total,
        limit=limit,
        offset=offset,
    )

@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket_detail(
    ticket_id: int,
    db: Session = Depends(get_db),
) -> TicketOut:
    """Lấy thông tin chi tiết của một ticket kèm danh sách aspects và priority breakdown."""
    ticket = TicketRepository.get_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket #{ticket_id} không tồn tại",
        )
    return ticket # type: ignore

@router.patch("/{ticket_id}/status", response_model=TicketOut)
def update_ticket_status(
    ticket_id: int,
    payload: StatusUpdateIn,
    db: Session = Depends(get_db),
) -> TicketOut:
    """Cập nhật trạng thái vòng đời ticket (new -> assigned -> in_progress -> resolved)."""
    try:
        updated = TicketRepository.update_status(
            db=db,
            ticket_id=ticket_id,
            new_status=payload.status,
            assigned_to=payload.assigned_to,
        )
    except InvalidStateTransitionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket #{ticket_id} không tồn tại",
        )

    return updated # type: ignore
