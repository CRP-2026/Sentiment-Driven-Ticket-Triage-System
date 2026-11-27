"""Unit tests for Amazon-style Top 1-2-3 Bayesian Aspect Insights (Option A)."""

from ticket_triage.application.aspect_insights import build_product_insights
from ticket_triage.domain.entities import AspectObservation


def test_build_product_insights_empty_state(sample_taxonomy):
    summary = build_product_insights({}, [], taxonomy=sample_taxonomy)
    assert summary.total_reviews == 0
    assert summary.satisfaction_rate == 0.0
    assert summary.aspects == ()
    assert summary.top_ranked_aspects == ()
    assert "Chưa có bình luận" in summary.summary_text_vi


def test_bayesian_ranking_prevents_single_review_from_beating_high_volume_aspect(sample_taxonomy):
    # product_quality: 10 positive / 11 total -> 90.9%, Bayesian = 11/13 = 0.8462 -> MUST BE #1
    # shipping: 5 positive / 6 total -> 83.3%, Bayesian = 6/8 = 0.7500 -> MUST BE #2
    # customer_service: 1 positive / 1 total -> 100%, Bayesian = 2/3 = 0.6667 -> MUST BE #3
    # refund_payment: 1 positive / 5 total -> 20% negative -> rank MUST BE None
    observations = (
        [AspectObservation("product_quality", "positive", 0.92, ("battery life", "build")) for _ in range(10)]
        + [AspectObservation("product_quality", "negative", 0.85, ("zipper",))]
        + [AspectObservation("shipping", "positive", 0.90, ("fast shipping",)) for _ in range(5)]
        + [AspectObservation("shipping", "neutral", 0.70, ("tracking",))]
        + [AspectObservation("customer_service", "positive", 0.88, ("helpful support",))]
        + [AspectObservation("refund_payment", "positive", 0.80)]
        + [AspectObservation("refund_payment", "negative", 0.95) for _ in range(4)]
    )

    summary = build_product_insights(
        sentiment_counts={"positive": 14, "neutral": 2, "negative": 4},
        aspect_observations=observations,
        taxonomy=sample_taxonomy,
        top_n=3,
    )

    assert summary.total_reviews == 20
    assert summary.satisfaction_rate == 0.7
    assert [a.aspect_id for a in summary.top_ranked_aspects] == [
        "product_quality",
        "shipping",
        "customer_service",
    ]
    assert [a.rank for a in summary.top_ranked_aspects] == [1, 2, 3]
    assert summary.top_ranked_aspects[0].name_vi == "Chất lượng sản phẩm"
    assert "battery life" in summary.top_ranked_aspects[0].top_terms

    refund_item = next(a for a in summary.aspects if a.aspect_id == "refund_payment")
    assert refund_item.rank is None
    assert refund_item.is_highly_rated is False
    assert refund_item.sentiment_summary == "negative"

    assert "#1 Chất lượng sản phẩm" in summary.summary_text_vi
    assert "#2 Vận chuyển & Giao hàng" in summary.summary_text_vi
    assert "#3 Dịch vụ khách hàng" in summary.summary_text_vi
    assert "Hoàn tiền & Thanh toán" in summary.summary_text_vi


def test_only_highly_rated_aspects_receive_top_1_2_3_ranks(sample_taxonomy):
    # Only 1 aspect >= 60% positive; another is mixed (50%) and another is negative (0%)
    observations = [
        AspectObservation("shipping", "positive", 0.90),
        AspectObservation("shipping", "positive", 0.88),
        AspectObservation("product_quality", "positive", 0.80),
        AspectObservation("product_quality", "negative", 0.85),
        AspectObservation("customer_service", "negative", 0.92),
    ]
    summary = build_product_insights(
        sentiment_counts={"positive": 2, "negative": 3},
        aspect_observations=observations,
        taxonomy=sample_taxonomy,
        top_n=3,
    )

    assert len(summary.top_ranked_aspects) == 1
    assert summary.top_ranked_aspects[0].aspect_id == "shipping"
    assert summary.top_ranked_aspects[0].rank == 1

    by_id = {a.aspect_id: a for a in summary.aspects}
    assert by_id["product_quality"].sentiment_summary == "mixed"
    assert by_id["product_quality"].rank is None
    assert by_id["customer_service"].sentiment_summary == "negative"
    assert by_id["customer_service"].rank is None


def test_equal_scores_tie_break_alphabetically_ascending(sample_taxonomy):
    observations = [
        AspectObservation("shipping", "positive", 0.90),
        AspectObservation("customer_service", "positive", 0.90),
    ]
    summary = build_product_insights(
        sentiment_counts={"positive": 2},
        aspect_observations=observations,
        taxonomy=sample_taxonomy,
        top_n=3,
    )
    assert [a.aspect_id for a in summary.top_ranked_aspects] == [
        "customer_service",
        "shipping",
    ]
    assert [a.rank for a in summary.top_ranked_aspects] == [1, 2]
