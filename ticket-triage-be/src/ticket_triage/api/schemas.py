from datetime import datetime

from pydantic import BaseModel, Field


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
    content: str = Field(..., min_length=1, description="Nội dung phản hồi tiếng Anh của khách hàng")

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
    status: str
    assigned_to: str | None = None
    aspects: list[AspectOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class TicketListResponse(BaseModel):
    items: list[TicketOut]
    total: int
    limit: int
    offset: int

class StatusUpdateIn(BaseModel):
    status: str = Field(..., description="new | assigned | in_progress | resolved")
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
    queue_size: int
