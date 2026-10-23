from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from ..core.queue.state_manager import StateManager
from .models import Ticket, TicketAspect


class TicketRepository:
    """Data Access Layer cho CSDL SQLite."""

    @staticmethod
    def create_ticket(
        db: Session,
        content: str,
        processed_content: str | None = None,
        language_flag: str = "en",
        needs_manual_review: bool = False,
        sentiment_label: str | None = None,
        confidence: float | None = None,
        low_confidence: bool = False,
        priority_score: float = 0.0,
        priority_level: str = "LOW",
        priority_breakdown: dict[str, Any] | None = None,
        dominant_aspect: str | None = None,
        status: str = "new",
        assigned_to: str | None = None,
        aspects_data: list[dict[str, Any]] | None = None,
    ) -> Ticket:
        """Tạo ticket mới và toàn bộ khía cạnh liên quan trong một Transaction duy nhất."""
        ticket = Ticket(
            content=content,
            processed_content=processed_content,
            language_flag=language_flag,
            needs_manual_review=needs_manual_review,
            sentiment_label=sentiment_label,
            confidence=confidence,
            low_confidence=low_confidence,
            priority_score=priority_score,
            priority_level=priority_level,
            priority_breakdown=priority_breakdown,
            dominant_aspect=dominant_aspect,
            status=status,
            assigned_to=assigned_to,
        )

        if aspects_data:
            for asp in aspects_data:
                aspect_obj = TicketAspect(
                    aspect=asp["aspect"],
                    sentiment=asp["sentiment"],
                    confidence=float(asp["confidence"]),
                    terms=asp.get("terms"),
                )
                ticket.aspects.append(aspect_obj)

        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def get_by_id(db: Session, ticket_id: int) -> Ticket | None:
        stmt = select(Ticket).where(Ticket.id == ticket_id)
        return db.scalar(stmt)

    @staticmethod
    def get_tickets(
        db: Session,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
        aspect: str | None = None,
        sentiment: str | None = None,
    ) -> tuple[list[Ticket], int]:
        """Truy vấn danh sách ticket sắp xếp theo priority_score giảm dần, kèm phân trang và bộ lọc."""
        stmt = select(Ticket)

        if status:
            stmt = stmt.where(Ticket.status == status)
        if sentiment:
            stmt = stmt.where(Ticket.sentiment_label == sentiment)
        if aspect:
            stmt = stmt.join(Ticket.aspects).where(TicketAspect.aspect == aspect)

        # Đếm tổng số
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt) or 0

        # Sắp xếp theo điểm ưu tiên giảm dần, sau đó thời gian tiếp nhận tăng dần (FIFO tie-break)
        stmt = stmt.order_by(desc(Ticket.priority_score), Ticket.created_at.asc())
        stmt = stmt.offset(offset).limit(limit)

        tickets = list(db.scalars(stmt).unique().all())
        return tickets, total

    @staticmethod
    def get_unresolved_tickets(db: Session) -> list[Ticket]:
        """Lấy toàn bộ ticket chưa hoàn thành để nạp lại vào hàng đợi heapq khi khởi động."""
        stmt = select(Ticket).where(Ticket.status != "resolved").order_by(desc(Ticket.priority_score))
        return list(db.scalars(stmt).unique().all())

    @staticmethod
    def update_status(
        db: Session,
        ticket_id: int,
        new_status: str,
        assigned_to: str | None = None,
    ) -> Ticket | None:
        """Cập nhật trạng thái vòng đời có kiểm soát quy tắc chuyển trạng thái."""
        ticket = TicketRepository.get_by_id(db, ticket_id)
        if not ticket:
            return None

        # Kiểm tra bước chuyển hợp lệ qua StateManager
        StateManager.validate_transition(ticket.status, new_status)

        ticket.status = new_status
        if assigned_to is not None:
            ticket.assigned_to = assigned_to

        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def get_stats_overview(db: Session) -> dict[str, Any]:
        """Thống kê tổng quan phục vụ Dashboard Analytics."""
        total = db.scalar(select(func.count(Ticket.id))) or 0

        # Sentiment breakdown
        sent_stmt = select(Ticket.sentiment_label, func.count(Ticket.id)).group_by(Ticket.sentiment_label)
        sent_rows = db.execute(sent_stmt).all()
        sentiment_counts = {r[0] or "unknown": r[1] for r in sent_rows}

        # Priority level breakdown
        prio_stmt = select(Ticket.priority_level, func.count(Ticket.id)).group_by(Ticket.priority_level)
        prio_rows = db.execute(prio_stmt).all()
        priority_counts = {r[0] or "unknown": r[1] for r in prio_rows}

        # Status breakdown
        stat_stmt = select(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status)
        stat_rows = db.execute(stat_stmt).all()
        status_counts = {r[0] or "unknown": r[1] for r in stat_rows}

        # Aspect counts
        asp_stmt = select(TicketAspect.aspect, func.count(TicketAspect.id)).group_by(TicketAspect.aspect)
        asp_rows = db.execute(asp_stmt).all()
        aspect_counts = {r[0]: r[1] for r in asp_rows}

        return {
            "total_tickets": total,
            "sentiment_counts": sentiment_counts,
            "priority_counts": priority_counts,
            "status_counts": status_counts,
            "aspect_counts": aspect_counts,
        }
