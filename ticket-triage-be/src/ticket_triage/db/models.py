from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _utc_now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


# ==============================================================================
# Storefront Bounded Context (Users, Catalog, Product Reviews & Review Aspects)
# ==============================================================================
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="customer", index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now, index=True)


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    icon: Mapped[str] = mapped_column(String(40), default="package", nullable=False)

    products: Mapped[list["Product"]] = relationship(
        back_populates="category", cascade="all, delete-orphan"
    )


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), index=True, nullable=False
    )
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    short_description: Mapped[str] = mapped_column(String(320), default="", nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    sku: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now, index=True)

    category: Mapped["Category"] = relationship(back_populates="products", lazy="joined")
    reviews: Mapped[list["ProductReview"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )


class ProductReview(Base):
    """Storefront review storing its own AI ABSA snapshot for full service isolation.

    `ticket_id` is stored as a logical cross-context reference (no hard FK to `tickets`)
    so Storefront and Triage can be split into independent databases via HttpTriageGateway.
    """

    __tablename__ = "product_reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    ticket_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    sentiment_label: Mapped[str | None] = mapped_column(String(20), index=True, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    priority_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    priority_level: Mapped[str] = mapped_column(String(20), default="LOW", nullable=False)
    needs_manual_review: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utc_now, index=True)

    product: Mapped["Product"] = relationship(back_populates="reviews")
    author: Mapped["User"] = relationship(lazy="joined")
    aspects: Mapped[list["ProductReviewAspect"]] = relationship(
        back_populates="review", cascade="all, delete-orphan", lazy="joined"
    )


class ProductReviewAspect(Base):
    """ABSA aspect tags owned by the Storefront bounded context for fast Amazon Insights."""

    __tablename__ = "product_review_aspects"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    review_id: Mapped[int] = mapped_column(
        ForeignKey("product_reviews.id", ondelete="CASCADE"), index=True, nullable=False
    )
    aspect: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    sentiment: Mapped[str] = mapped_column(String(20), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    terms: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    review: Mapped["ProductReview"] = relationship(back_populates="aspects")


# ==============================================================================
# Admin Triage Bounded Context (Tickets & Ticket Aspects)
# ==============================================================================
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

    # Denormalized Storefront provenance (no cross-context FK -> works in split-DB HTTP mode
    # and eliminates extra JOINs on Admin Inbox polling)
    source: Mapped[str] = mapped_column(String(30), default="direct_api", index=True)
    product_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    product_name: Mapped[str | None] = mapped_column(String(180), nullable=True)
    product_slug: Mapped[str | None] = mapped_column(String(120), nullable=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    author_name: Mapped[str | None] = mapped_column(String(120), nullable=True)

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
