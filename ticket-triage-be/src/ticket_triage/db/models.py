from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _utc_now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass

class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    processed_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    language_flag: Mapped[str] = mapped_column(String(20), default="en")
    needs_manual_review: Mapped[bool] = mapped_column(Boolean, default=False)

    sentiment_label: Mapped[str | None] = mapped_column(String(20), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    low_confidence: Mapped[bool] = mapped_column(Boolean, default=False)

    priority_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    priority_level: Mapped[str] = mapped_column(String(20), default="LOW")
    priority_breakdown: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    dominant_aspect: Mapped[str | None] = mapped_column(String(50), nullable=True)

    status: Mapped[str] = mapped_column(String(30), default="new", index=True)
    assigned_to: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_utc_now, onupdate=_utc_now
    )

    aspects: Mapped[list["TicketAspect"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan", lazy="joined"
    )

class TicketAspect(Base):
    __tablename__ = "ticket_aspects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(
        ForeignKey("tickets.id", ondelete="CASCADE"), index=True, nullable=False
    )
    aspect: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    sentiment: Mapped[str] = mapped_column(String(20), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    terms: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    ticket: Mapped["Ticket"] = relationship(back_populates="aspects")
