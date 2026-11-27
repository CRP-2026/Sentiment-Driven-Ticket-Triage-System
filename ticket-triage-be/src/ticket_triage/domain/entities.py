"""Immutable domain entities shared across Application use cases and Adapters."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

UserRole = Literal["customer", "admin"]
SentimentSummary = Literal["positive", "mixed", "negative"]
TicketSource = Literal["direct_api", "storefront_review"]


@dataclass(frozen=True)
class UserEntity:
    id: int
    email: str
    full_name: str
    password_hash: str
    role: UserRole
    is_active: bool
    created_at: datetime


@dataclass(frozen=True)
class CategoryEntity:
    id: int
    slug: str
    name: str
    description: str
    icon: str
    product_count: int = 0


@dataclass(frozen=True)
class ProductEntity:
    id: int
    category_id: int
    category_slug: str
    category_name: str
    slug: str
    name: str
    short_description: str
    description: str
    price: float
    image_url: str
    sku: str
    stock: int
    created_at: datetime


@dataclass(frozen=True)
class AspectObservation:
    """Single ABSA aspect output attached to a product review."""

    aspect: str
    sentiment: str
    confidence: float
    terms: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReviewEntity:
    id: int
    product_id: int
    user_id: int
    author_name: str
    ticket_id: int
    title: str | None
    content: str
    sentiment_label: str | None
    confidence: float | None
    priority_score: float
    priority_level: str
    needs_manual_review: bool
    aspects: tuple[AspectObservation, ...] = ()
    created_at: datetime | None = None


@dataclass(frozen=True)
class AspectInsight:
    """Amazon-style aggregated aspect evaluation for a single product."""

    aspect_id: str
    name_vi: str
    description: str
    rank: int | None
    total_mentions: int
    positive_count: int
    neutral_count: int
    negative_count: int
    positive_ratio: float
    ranking_score: float
    sentiment_summary: SentimentSummary
    is_highly_rated: bool
    top_terms: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProductInsightsSummary:
    """100% Sentiment-driven product evaluation (Option A — no fabricated stars)."""

    total_reviews: int
    positive_review_count: int
    neutral_review_count: int
    negative_review_count: int
    satisfaction_rate: float
    summary_text_vi: str
    aspects: tuple[AspectInsight, ...] = ()
    top_ranked_aspects: tuple[AspectInsight, ...] = ()


@dataclass(frozen=True)
class ProductCatalogItem:
    product: ProductEntity
    total_reviews: int
    satisfaction_rate: float
    top_ranked_aspects: tuple[AspectInsight, ...] = ()


@dataclass(frozen=True)
class ProductDetailResult:
    product: ProductEntity
    insights: ProductInsightsSummary
    reviews: list[ReviewEntity]
    total_filtered_reviews: int


@dataclass(frozen=True)
class TriageDispatchRequest:
    """Port payload sent from Storefront to Triage Gateway."""

    content: str
    product_id: int | None = None
    product_name: str | None = None
    product_slug: str | None = None
    user_id: int | None = None
    author_name: str | None = None
    source: TicketSource = "direct_api"


@dataclass(frozen=True)
class TriageDispatchResult:
    """Normalized result returned by any TriageGatewayPort implementation."""

    ticket_id: int
    sentiment_label: str | None
    confidence: float | None
    priority_score: float
    priority_level: str
    dominant_aspect: str | None
    needs_manual_review: bool
    aspects: tuple[AspectObservation, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ReviewSubmissionResult:
    review: ReviewEntity
    triage: TriageDispatchResult
    insights: ProductInsightsSummary
