"""Pure Presentation mappers converting Domain entities to API Pydantic schemas."""

from datetime import UTC, datetime

from ..domain.entities import (
    AspectInsight,
    CategoryEntity,
    ProductCatalogItem,
    ProductEntity,
    ProductInsightsSummary,
    ReviewEntity,
    TriageDispatchResult,
    UserEntity,
)
from .schemas import (
    AspectInsightOut,
    AspectOut,
    CategoryOut,
    ProductInsightsOut,
    ProductOut,
    ProductSummaryOut,
    ReviewOut,
    ReviewTriageSummaryOut,
    UserOut,
    UserRoleEnum,
)


def to_user_out(user: UserEntity) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=UserRoleEnum(user.role),
        created_at=user.created_at,
    )


def to_category_out(cat: CategoryEntity) -> CategoryOut:
    return CategoryOut(
        id=cat.id,
        slug=cat.slug,
        name=cat.name,
        description=cat.description,
        icon=cat.icon,
        product_count=cat.product_count,
    )


def to_aspect_insight_out(item: AspectInsight) -> AspectInsightOut:
    return AspectInsightOut(
        aspect_id=item.aspect_id,
        name_vi=item.name_vi,
        description=item.description,
        rank=item.rank,
        total_mentions=item.total_mentions,
        positive_count=item.positive_count,
        neutral_count=item.neutral_count,
        negative_count=item.negative_count,
        positive_ratio=item.positive_ratio,
        ranking_score=item.ranking_score,
        sentiment_summary=item.sentiment_summary,
        is_highly_rated=item.is_highly_rated,
        top_terms=list(item.top_terms),
    )


def to_insights_out(summary: ProductInsightsSummary) -> ProductInsightsOut:
    return ProductInsightsOut(
        total_reviews=summary.total_reviews,
        positive_review_count=summary.positive_review_count,
        neutral_review_count=summary.neutral_review_count,
        negative_review_count=summary.negative_review_count,
        satisfaction_rate=summary.satisfaction_rate,
        summary_text_vi=summary.summary_text_vi,
        aspects=[to_aspect_insight_out(a) for a in summary.aspects],
        top_ranked_aspects=[to_aspect_insight_out(a) for a in summary.top_ranked_aspects],
    )


def to_product_out(product: ProductEntity) -> ProductOut:
    return ProductOut(
        id=product.id,
        category_id=product.category_id,
        category_slug=product.category_slug,
        category_name=product.category_name,
        slug=product.slug,
        name=product.name,
        short_description=product.short_description,
        description=product.description,
        price=product.price,
        image_url=product.image_url,
        sku=product.sku,
        stock=product.stock,
        created_at=product.created_at,
    )


def to_product_summary_out(entry: ProductCatalogItem) -> ProductSummaryOut:
    return ProductSummaryOut(
        **to_product_out(entry.product).model_dump(),
        total_reviews=entry.total_reviews,
        satisfaction_rate=entry.satisfaction_rate,
        top_ranked_aspects=[to_aspect_insight_out(a) for a in entry.top_ranked_aspects],
    )


def to_review_out(review: ReviewEntity) -> ReviewOut:
    return ReviewOut(
        id=review.id,
        product_id=review.product_id,
        user_id=review.user_id,
        author_name=review.author_name,
        ticket_id=review.ticket_id,
        title=review.title,
        content=review.content,
        sentiment_label=review.sentiment_label,
        confidence=review.confidence,
        priority_score=review.priority_score,
        priority_level=review.priority_level,
        needs_manual_review=review.needs_manual_review,
        aspects=[
            AspectOut(
                aspect=asp.aspect,
                sentiment=asp.sentiment,
                confidence=asp.confidence,
                terms=list(asp.terms),
            )
            for asp in review.aspects
        ],
        created_at=review.created_at or datetime.now(UTC),
    )


def to_review_triage_summary_out(triage: TriageDispatchResult) -> ReviewTriageSummaryOut:
    return ReviewTriageSummaryOut(
        ticket_id=triage.ticket_id,
        sentiment_label=triage.sentiment_label,
        confidence=triage.confidence,
        priority_score=triage.priority_score,
        priority_level=triage.priority_level,
        dominant_aspect=triage.dominant_aspect,
        needs_manual_review=triage.needs_manual_review,
        aspects=[
            AspectOut(
                aspect=asp.aspect,
                sentiment=asp.sentiment,
                confidence=asp.confidence,
                terms=list(asp.terms),
            )
            for asp in triage.aspects
        ],
    )
