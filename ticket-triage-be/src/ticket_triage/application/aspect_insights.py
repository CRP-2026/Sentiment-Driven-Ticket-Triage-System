"""Pure domain/application aggregator for Amazon-style Top 1-2-3 Aspect Insights."""

from collections import Counter, defaultdict

from ..core.taxonomy import Taxonomy
from ..domain.entities import (
    AspectInsight,
    AspectObservation,
    ProductInsightsSummary,
    SentimentSummary,
)

HIGHLY_RATED_THRESHOLD = 0.60
MIXED_THRESHOLD = 0.35


def _classify_aspect_summary(positive_ratio: float) -> SentimentSummary:
    if positive_ratio >= HIGHLY_RATED_THRESHOLD:
        return "positive"
    if positive_ratio >= MIXED_THRESHOLD:
        return "mixed"
    return "negative"


def _compute_bayesian_score(positive_count: int, total_mentions: int) -> float:
    """Laplace/Bayesian smoothed positivity score preventing 1/1 from beating 15/16."""
    return round((positive_count + 1) / (total_mentions + 2), 4)


def _format_summary_text(
    total_reviews: int,
    satisfaction_rate: float,
    top_ranked: list[AspectInsight],
    all_aspects: list[AspectInsight],
) -> str:
    if total_reviews == 0:
        return "Chưa có bình luận nào cho sản phẩm này. Hãy là người đầu tiên chia sẻ trải nghiệm!"

    negative_watch = [a for a in all_aspects if a.sentiment_summary == "negative"]

    if top_ranked:
        ranked_str = ", ".join(
            f"#{item.rank} {item.name_vi} ({round(item.positive_ratio * 100)}% tích cực)"
            for item in top_ranked
        )
        if negative_watch:
            caution_str = ", ".join(item.name_vi for item in negative_watch[:2])
            return f"Top khía cạnh được đánh giá cao: {ranked_str}. Cần lưu ý thêm về {caution_str}."
        return f"Top khía cạnh được đánh giá cao: {ranked_str}."

    if negative_watch:
        caution_str = ", ".join(item.name_vi for item in negative_watch[:2])
        return (
            f"Đã phân tích {total_reviews} bình luận ({round(satisfaction_rate * 100)}% tích cực). "
            f"Khách hàng đang phản ánh nhiều về {caution_str}."
        )

    return (
        f"Đã phân tích {total_reviews} bình luận bằng AI ABSA "
        f"với tỷ lệ hài lòng {round(satisfaction_rate * 100)}%."
    )


def build_product_insights(
    sentiment_counts: dict[str, int],
    aspect_observations: list[AspectObservation],
    taxonomy: Taxonomy | None = None,
    top_n: int = 3,
) -> ProductInsightsSummary:
    """Compute 100% AI sentiment-driven satisfaction metrics and Top 1-2-3 aspects (Option A)."""
    positive_reviews = int(sentiment_counts.get("positive", 0))
    neutral_reviews = int(sentiment_counts.get("neutral", 0))
    negative_reviews = int(sentiment_counts.get("negative", 0))
    other_reviews = sum(
        int(v)
        for k, v in sentiment_counts.items()
        if k not in ("positive", "neutral", "negative")
    )
    total_reviews = positive_reviews + neutral_reviews + negative_reviews + other_reviews
    satisfaction_rate = round(positive_reviews / total_reviews, 4) if total_reviews > 0 else 0.0

    grouped_counts: dict[str, dict[str, int]] = defaultdict(
        lambda: {"positive": 0, "neutral": 0, "negative": 0}
    )
    grouped_terms: dict[str, Counter[str]] = defaultdict(Counter)
    term_display_case: dict[tuple[str, str], str] = {}

    for obs in aspect_observations:
        asp_id = obs.aspect.strip()
        if not asp_id:
            continue
        sent = obs.sentiment if obs.sentiment in ("positive", "neutral", "negative") else "neutral"
        grouped_counts[asp_id][sent] += 1
        for raw_term in obs.terms:
            cleaned = str(raw_term).strip()
            if not cleaned:
                continue
            key = cleaned.lower()
            grouped_terms[asp_id][key] += 1
            term_display_case.setdefault((asp_id, key), cleaned)

    unsorted_insights: list[AspectInsight] = []
    for asp_id, counts in grouped_counts.items():
        pos = counts["positive"]
        neu = counts["neutral"]
        neg = counts["negative"]
        total = pos + neu + neg
        if total == 0:
            continue

        pos_ratio = round(pos / total, 4)
        ranking_score = _compute_bayesian_score(pos, total)
        summary = _classify_aspect_summary(pos_ratio)
        is_highly_rated = pos >= 1 and pos_ratio >= HIGHLY_RATED_THRESHOLD

        defn = taxonomy.get_aspect(asp_id) if taxonomy is not None else None
        name_vi = defn.name_vi if defn is not None else asp_id.replace("_", " ")
        description = defn.description if defn is not None else ""

        top_terms = tuple(
            term_display_case[(asp_id, term_key)]
            for term_key, _ in grouped_terms[asp_id].most_common(5)
        )

        unsorted_insights.append(
            AspectInsight(
                aspect_id=asp_id,
                name_vi=name_vi,
                description=description,
                rank=None,
                total_mentions=total,
                positive_count=pos,
                neutral_count=neu,
                negative_count=neg,
                positive_ratio=pos_ratio,
                ranking_score=ranking_score,
                sentiment_summary=summary,
                is_highly_rated=is_highly_rated,
                top_terms=top_terms,
            )
        )

    ordered = sorted(
        unsorted_insights,
        key=lambda item: (
            not item.is_highly_rated,
            -item.ranking_score,
            -item.positive_count,
            -item.total_mentions,
            item.aspect_id,
        ),
    )

    ranked_insights: list[AspectInsight] = []
    top_ranked: list[AspectInsight] = []
    next_rank = 1
    for item in ordered:
        assigned_rank: int | None = None
        if item.is_highly_rated and next_rank <= top_n:
            assigned_rank = next_rank
            next_rank += 1

        final_item = AspectInsight(
            aspect_id=item.aspect_id,
            name_vi=item.name_vi,
            description=item.description,
            rank=assigned_rank,
            total_mentions=item.total_mentions,
            positive_count=item.positive_count,
            neutral_count=item.neutral_count,
            negative_count=item.negative_count,
            positive_ratio=item.positive_ratio,
            ranking_score=item.ranking_score,
            sentiment_summary=item.sentiment_summary,
            is_highly_rated=item.is_highly_rated,
            top_terms=item.top_terms,
        )
        ranked_insights.append(final_item)
        if assigned_rank is not None:
            top_ranked.append(final_item)

    summary_text = _format_summary_text(
        total_reviews=total_reviews,
        satisfaction_rate=satisfaction_rate,
        top_ranked=top_ranked,
        all_aspects=ranked_insights,
    )

    return ProductInsightsSummary(
        total_reviews=total_reviews,
        positive_review_count=positive_reviews,
        neutral_review_count=neutral_reviews,
        negative_review_count=negative_reviews,
        satisfaction_rate=satisfaction_rate,
        summary_text_vi=summary_text,
        aspects=tuple(ranked_insights),
        top_ranked_aspects=tuple(top_ranked),
    )
