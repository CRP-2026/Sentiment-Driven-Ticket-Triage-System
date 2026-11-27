from datetime import UTC, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_serializer, field_validator

from ..domain.validators import validate_text_content


def _serialize_utc_datetime(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    else:
        dt = dt.astimezone(UTC)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


class StatusEnum(str, Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class UserRoleEnum(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"


# ==============================================================================
# Triage / Admin Schemas
# ==============================================================================
class AspectOut(BaseModel):
    aspect: str
    sentiment: str
    confidence: float
    terms: list[str] = []

    model_config = {"from_attributes": True}


class PriorityBreakdownOut(BaseModel):
    score: float
    base: float
    urgency_bonus: float
    intensity_bonus: float
    aspect_bonus: float
    reasons: list[str]

    model_config = {"from_attributes": True}


class TicketCreateIn(BaseModel):
    content: str = Field(..., description="Nội dung phản hồi tiếng Anh của khách hàng")
    source: Literal["direct_api", "storefront_review"] = Field(
        default="direct_api",
        description="Nguồn gửi: direct_api | storefront_review",
    )
    product_id: int | None = None
    product_name: str | None = Field(default=None, max_length=180)
    product_slug: str | None = Field(default=None, max_length=120)
    user_id: int | None = None
    author_name: str | None = Field(default=None, max_length=120)

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        return validate_text_content(v, field_label="Nội dung ticket")


class TicketOut(BaseModel):
    id: int
    content: str
    processed_content: str | None = None
    language_flag: str
    needs_manual_review: bool
    sentiment_label: str | None = None
    confidence: float | None = None
    low_confidence: bool
    priority_score: float
    priority_level: str
    dominant_aspect: str | None = None
    priority_breakdown: PriorityBreakdownOut | None = None
    status: StatusEnum
    assigned_to: str | None = None
    source: str = "direct_api"
    product_id: int | None = None
    product_name: str | None = None
    product_slug: str | None = None
    author_name: str | None = None
    aspects: list[AspectOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("created_at", "updated_at", when_used="json")
    def serialize_dt(self, dt: datetime) -> str:
        return _serialize_utc_datetime(dt)


class TicketListResponse(BaseModel):
    items: list[TicketOut]
    total: int
    limit: int
    offset: int


class StatusUpdateIn(BaseModel):
    status: StatusEnum = Field(..., description="new | assigned | in_progress | resolved")
    assigned_to: str | None = None


class AspectMetaItem(BaseModel):
    id: str
    name_vi: str
    description: str
    department: str
    weight: float


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    model_name: str
    is_mock: bool = False
    model_loaded: bool = True
    queue_size: int
    triage_gateway_mode: str = "local"

    model_config = {"protected_namespaces": ()}


class StatsOverviewResponse(BaseModel):
    total_tickets: int
    sentiment_counts: dict[str, int]
    priority_counts: dict[str, int]
    status_counts: dict[str, int]
    aspect_counts: dict[str, int]


class AspectStatItem(BaseModel):
    aspect: str
    sentiment: str
    count: int


# ==============================================================================
# Auth Schemas
# ==============================================================================
class RegisterIn(BaseModel):
    email: str = Field(..., description="Địa chỉ email đăng ký")
    full_name: str = Field(..., description="Tên hiển thị của người dùng")
    password: str = Field(..., min_length=6, max_length=128, description="Mật khẩu tối thiểu 6 ký tự")


class LoginIn(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRoleEnum
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("created_at", when_used="json")
    def serialize_dt(self, dt: datetime) -> str:
        return _serialize_utc_datetime(dt)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ==============================================================================
# Storefront & Amazon-Style ABSA Insights Schemas (Option A — Pure AI ABSA)
# ==============================================================================
class CategoryOut(BaseModel):
    id: int
    slug: str
    name: str
    description: str
    icon: str
    product_count: int = 0


class AspectInsightOut(BaseModel):
    aspect_id: str
    name_vi: str
    description: str
    rank: int | None = None
    total_mentions: int
    positive_count: int
    neutral_count: int
    negative_count: int
    positive_ratio: float
    ranking_score: float
    sentiment_summary: str
    is_highly_rated: bool
    top_terms: list[str] = []


class ProductInsightsOut(BaseModel):
    total_reviews: int
    positive_review_count: int
    neutral_review_count: int
    negative_review_count: int
    satisfaction_rate: float
    summary_text_vi: str
    aspects: list[AspectInsightOut] = []
    top_ranked_aspects: list[AspectInsightOut] = []


class ProductOut(BaseModel):
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

    @field_serializer("created_at", when_used="json")
    def serialize_dt(self, dt: datetime) -> str:
        return _serialize_utc_datetime(dt)


class ProductSummaryOut(ProductOut):
    total_reviews: int = 0
    satisfaction_rate: float = 0.0
    top_ranked_aspects: list[AspectInsightOut] = []


class ProductListResponse(BaseModel):
    items: list[ProductSummaryOut]
    total: int
    limit: int
    offset: int


class ReviewOut(BaseModel):
    id: int
    product_id: int
    user_id: int
    author_name: str
    ticket_id: int
    title: str | None = None
    content: str
    sentiment_label: str | None = None
    confidence: float | None = None
    priority_score: float
    priority_level: str
    needs_manual_review: bool
    aspects: list[AspectOut] = []
    created_at: datetime

    @field_serializer("created_at", when_used="json")
    def serialize_dt(self, dt: datetime) -> str:
        return _serialize_utc_datetime(dt)


class ProductDetailResponse(BaseModel):
    product: ProductOut
    insights: ProductInsightsOut
    reviews: list[ReviewOut]
    total_filtered_reviews: int


class ReviewCreateIn(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    content: str = Field(..., description="Nội dung bình luận tiếng Anh về sản phẩm")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        return validate_text_content(v, field_label="Nội dung bình luận")


class ReviewTriageSummaryOut(BaseModel):
    ticket_id: int
    sentiment_label: str | None = None
    confidence: float | None = None
    priority_score: float
    priority_level: str
    dominant_aspect: str | None = None
    needs_manual_review: bool
    aspects: list[AspectOut] = []


class ReviewCreateResponse(BaseModel):
    review: ReviewOut
    triage: ReviewTriageSummaryOut
    insights: ProductInsightsOut


class ImageUploadResponse(BaseModel):
    image_url: str
