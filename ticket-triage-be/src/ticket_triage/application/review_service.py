"""Storefront review submission use case decoupled from AI Triage via TriageGatewayPort."""

from ..core.taxonomy import Taxonomy
from ..domain.entities import (
    ReviewSubmissionResult,
    TriageDispatchRequest,
    UserEntity,
)
from ..domain.exceptions import EntityNotFoundError, ValidationDomainError
from ..domain.ports.repositories import CatalogRepositoryPort, ReviewRepositoryPort
from ..domain.ports.triage import TriageGatewayPort
from ..domain.validators import validate_text_content
from .aspect_insights import build_product_insights


class ReviewService:
    """Handles customer review submission and dispatches to TriageGatewayPort (SOLID-D)."""

    def __init__(
        self,
        catalog_repo: CatalogRepositoryPort,
        review_repo: ReviewRepositoryPort,
        triage_gateway: TriageGatewayPort,
        taxonomy: Taxonomy | None = None,
    ) -> None:
        self._catalog_repo = catalog_repo
        self._review_repo = review_repo
        self._triage_gateway = triage_gateway
        self._taxonomy = taxonomy

    def submit_review(
        self,
        user: UserEntity,
        product_slug: str,
        content: str,
        title: str | None = None,
    ) -> ReviewSubmissionResult:
        try:
            cleaned_content = validate_text_content(content, field_label="Nội dung bình luận")
        except (ValueError, TypeError) as exc:
            raise ValidationDomainError(str(exc)) from exc

        cleaned_title = title.strip() if title and title.strip() else None
        if cleaned_title and len(cleaned_title) > 200:
            raise ValidationDomainError("Tiêu đề bình luận không được vượt quá 200 ký tự.")

        product = self._catalog_repo.get_product_by_slug(product_slug)
        if product is None:
            raise EntityNotFoundError(f"Không tìm thấy sản phẩm '{product_slug}'.")

        # 1. Dispatch review to Triage Gateway (in-process or remote HTTP via DIP)
        triage_result = self._triage_gateway.dispatch_ticket(
            TriageDispatchRequest(
                content=cleaned_content,
                product_id=product.id,
                product_name=product.name,
                product_slug=product.slug,
                user_id=user.id,
                author_name=user.full_name,
                source="storefront_review",
            )
        )

        # 2. Persist ProductReview + AI snapshot in Storefront's own bounded context
        review = self._review_repo.create(
            product_id=product.id,
            user_id=user.id,
            ticket_id=triage_result.ticket_id,
            content=cleaned_content,
            title=cleaned_title,
            sentiment_label=triage_result.sentiment_label,
            confidence=triage_result.confidence,
            priority_score=triage_result.priority_score,
            priority_level=triage_result.priority_level,
            needs_manual_review=triage_result.needs_manual_review,
            aspects=triage_result.aspects,
        )

        # 3. Recompute fresh Amazon-style product insights from Storefront data
        sentiment_counts = self._catalog_repo.get_product_sentiment_counts(product.id)
        aspect_observations = self._catalog_repo.get_product_aspect_observations(product.id)
        updated_insights = build_product_insights(
            sentiment_counts=sentiment_counts,
            aspect_observations=aspect_observations,
            taxonomy=self._taxonomy,
            top_n=3,
        )

        return ReviewSubmissionResult(
            review=review,
            triage=triage_result,
            insights=updated_insights,
        )
