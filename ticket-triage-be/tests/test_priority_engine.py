from ticket_triage.core.priority.priority_engine import calculate_priority
from ticket_triage.core.sentiment.base import AbsaResult, AspectSentiment, SentimentResult


def test_priority_engine_critical_case():
    result = AbsaResult(
        overall=SentimentResult(label="negative", confidence=0.95),
        aspects=[
            AspectSentiment(aspect="refund_payment", sentiment="negative", confidence=0.95),
        ],
    )
    text = "I was charged twice! Please refund immediately or I will dispute the chargeback!!!"
    breakdown = calculate_priority(result, text)

    assert breakdown.score >= 70.0
    assert breakdown.level == "CRITICAL"
    assert breakdown.dominant_aspect == "refund_payment"
    assert breakdown.urgency_bonus > 0
    assert breakdown.intensity_bonus == 5.0
    assert len(breakdown.reasons) >= 3

def test_priority_engine_low_case():
    result = AbsaResult(
        overall=SentimentResult(label="positive", confidence=0.90),
        aspects=[
            AspectSentiment(aspect="customer_service", sentiment="positive", confidence=0.95),
        ],
    )
    text = "Thank you for the quick help, the representative was wonderful."
    breakdown = calculate_priority(result, text)

    assert breakdown.score < 30.0
    assert breakdown.level == "LOW"
    assert breakdown.base == 5.0
    assert breakdown.urgency_bonus == 0.0

def test_priority_engine_negation_awareness():
    result = AbsaResult(
        overall=SentimentResult(label="neutral", confidence=0.80),
        aspects=[],
    )
    # "not urgent" shouldn't trigger urgent bonus
    text = "This inquiry is not urgent, please reply whenever you have time."
    breakdown = calculate_priority(result, text)

    assert breakdown.urgency_bonus == 0.0
    assert breakdown.score == 20.0
    assert breakdown.level == "LOW"

def test_priority_engine_worst_aspect_wins_multiple_aspects():
    result = AbsaResult(
        overall=SentimentResult(label="negative", confidence=0.80),
        aspects=[
            AspectSentiment(aspect="refund_payment", sentiment="negative", confidence=0.90), # weight 1.0 -> 9.0
            AspectSentiment(aspect="shipping", sentiment="negative", confidence=0.80), # weight 0.7 -> 5.6, 25% -> 1.4
        ],
    )
    text = "Package arrived 10 days late and I was double charged."
    breakdown = calculate_priority(result, text)

    assert breakdown.dominant_aspect == "refund_payment"
    assert breakdown.aspect_bonus == round(9.0 + 0.25 * (0.7 * 0.80 * 10.0), 2)
