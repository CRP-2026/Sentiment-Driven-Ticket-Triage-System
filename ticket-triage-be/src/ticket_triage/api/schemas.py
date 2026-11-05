from datetime import datetime, timezone
from enum import Enum
import re
from typing import Any

from pydantic import BaseModel, Field, field_serializer, field_validator


class StatusEnum(str, Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


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

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("Nội dung ticket phải là chuỗi văn bản.")
        cleaned = v.strip()
        if len(cleaned) < 3:
            raise ValueError("Nội dung ticket quá ngắn (tối thiểu 3 ký tự không phải khoảng trắng).")
        if len(cleaned) > 5000:
            raise ValueError("Nội dung ticket vượt quá giới hạn tối đa cho phép (5000 ký tự).")

        # Kiểm tra nội dung rỗng sau khi loại bỏ HTML tags hoặc chỉ chứa toàn dấu câu
        text_without_html = re.sub(r"<[^>]+>", "", cleaned).strip()
        if not text_without_html or not re.search(r"\w", text_without_html):
            raise ValueError("Nội dung ticket không hợp lệ (chỉ chứa thẻ HTML rỗng hoặc ký tự đặc biệt).")

        return cleaned


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
    aspects: list[AspectOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("created_at", "updated_at", when_used="json")
    def serialize_dt(self, dt: datetime) -> str:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


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
