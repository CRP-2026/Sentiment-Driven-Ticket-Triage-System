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


def test_load_priority_rules_default_repo_yaml():
    from ticket_triage.core.priority.priority_engine import load_priority_rules

    load_priority_rules.cache_clear()
    rules = load_priority_rules()
    assert "damaged" in rules.high_keywords
    assert "overcharged" in rules.high_keywords
    assert "charged twice" in rules.critical_keywords
    assert rules.critical_last_sentence == 30.0
    assert rules.critical_other_sentence == 20.0
    assert rules.high_last_sentence == 15.0
    assert rules.high_other_sentence == 10.0
    assert rules.urgency_cap == 30.0
    assert rules.aspect_cap == 20.0
    assert rules.intensity_bonus == 5.0
    assert rules.threshold_high == 70.0
    assert rules.threshold_medium == 30.0


def test_load_priority_rules_custom_yaml_and_fallbacks(tmp_path):
    from ticket_triage.core.priority.priority_engine import PriorityRules, load_priority_rules

    custom_yaml = tmp_path / "custom_rules.yaml"
    custom_yaml.write_text(
        """
urgency_keywords:
  critical:
    - "  VIP_OUTAGE  "
    - "vip_outage"
    - "System Down"
  high: []
urgency_cap: 45
aspect_cap: 25
intensity_bonus: -5
urgency_points:
  critical_last_sentence: 40
  critical_other_sentence: 25
  high_last_sentence: 18
  high_other_sentence: 12
priority_thresholds:
  high: 65
  medium: 25
""",
        encoding="utf-8",
    )

    load_priority_rules.cache_clear()
    rules = load_priority_rules(custom_yaml)
    assert rules.critical_keywords == ["vip_outage", "system down"]
    assert rules.high_keywords == []
    assert rules.urgency_cap == 45.0
    assert rules.aspect_cap == 25.0
    assert rules.intensity_bonus == 0.0
    assert rules.critical_last_sentence == 40.0
    assert rules.critical_other_sentence == 25.0
    assert rules.high_last_sentence == 18.0
    assert rules.high_other_sentence == 12.0
    assert rules.threshold_high == 65.0
    assert rules.threshold_medium == 25.0

    missing_rules = load_priority_rules(tmp_path / "missing.yaml")
    assert missing_rules == PriorityRules()

    corrupt_yaml = tmp_path / "corrupt.yaml"
    corrupt_yaml.write_text(":::invalid: [", encoding="utf-8")
    assert load_priority_rules(corrupt_yaml) == PriorityRules()

    non_dict_yaml = tmp_path / "list.yaml"
    non_dict_yaml.write_text("- item1\n- item2\n", encoding="utf-8")
    assert load_priority_rules(non_dict_yaml) == PriorityRules()


def test_priority_engine_uses_injected_rules_and_clamps_confidence():
    from ticket_triage.core.priority.priority_engine import PriorityRules, calculate_priority
    from ticket_triage.core.sentiment.base import AbsaResult, SentimentResult

    custom_rules = PriorityRules(
        critical_keywords=["VIP_VIP"],
        high_keywords=[],
        critical_last_sentence=25.0,
        urgency_cap=25.0,
        threshold_high=60.0,
    )
    high_conf_res = AbsaResult(
        overall=SentimentResult(label="negative", confidence=1.8),
        aspects=[],
    )
    bd = calculate_priority(high_conf_res, "Please handle vip_vip.", rules=custom_rules)
    assert bd.base == 60.0
    assert bd.urgency_bonus == 25.0
    assert bd.level == "CRITICAL"

    neg_conf_res = AbsaResult(
        overall=SentimentResult(label="negative", confidence=-0.4),
        aspects=[],
    )
    bd_low = calculate_priority(neg_conf_res, "Just checking status.", rules=custom_rules)
    assert bd_low.base == 0.0


def test_negation_multiple_occurrences_and_remedy_keywords():
    from ticket_triage.core.priority.priority_engine import _is_negated, calculate_priority
    from ticket_triage.core.sentiment.base import AbsaResult, SentimentResult

    absa = AbsaResult(overall=SentimentResult(label="negative", confidence=0.8), aspects=[])

    multi_neg_text = "I did not get a reply, and this is not urgent."
    assert _is_negated(multi_neg_text, multi_neg_text.index("urgent"), keyword="urgent") is True
    bd_multi_neg = calculate_priority(absa, multi_neg_text)
    assert bd_multi_neg.urgency_bonus == 0.0

    for complaint in [
        "There is no refund processed.",
        "They won't refund my payment.",
        "I could not cancel my subscription.",
        "Left without refund for two weeks.",
        "Please stop this fraud.",
    ]:
        bd = calculate_priority(absa, complaint)
        assert bd.urgency_bonus > 0.0, f"Expected urgency bonus for: {complaint}"

    for false_alarm in [
        "This item is not broken.",
        "No fraud happened here.",
    ]:
        bd_ok = calculate_priority(absa, false_alarm)
        assert bd_ok.urgency_bonus == 0.0, f"Expected zero urgency for: {false_alarm}"


def test_resolution_context_and_contrast_clause_handling():
    from ticket_triage.core.priority.priority_engine import calculate_priority
    from ticket_triage.core.sentiment.base import AbsaResult, SentimentResult

    absa = AbsaResult(overall=SentimentResult(label="neutral", confidence=0.7), aspects=[])

    for resolved_text in [
        "Refund received, thank you!",
        "I received my refund quickly.",
        "Thanks for resolving my issue.",
        "My issue is resolved now.",
    ]:
        bd = calculate_priority(absa, resolved_text)
        assert bd.urgency_bonus == 0.0, f"Expected resolved clause skip for: {resolved_text}"

    for unresolved_text in [
        "My refund was not received!",
        "I have not received my refund!",
        "I have not yet received my refund!",
    ]:
        bd = calculate_priority(absa, unresolved_text)
        assert bd.urgency_bonus == 15.0, f"Expected urgency for negated resolution: {unresolved_text}"

    contrast_text = "Thanks for resolving the previous ticket, but this new item is broken!"
    bd_contrast = calculate_priority(absa, contrast_text)
    assert bd_contrast.urgency_bonus == 15.0

    although_text = "Although my refund was received, this replacement is broken!"
    bd_although = calculate_priority(absa, although_text)
    assert bd_although.urgency_bonus == 15.0


def test_load_aspect_weights_from_yaml_and_explicit_empty_dict(tmp_path):
    from ticket_triage.core.priority.priority_engine import (
        calculate_priority,
        load_aspect_weights,
    )
    from ticket_triage.core.sentiment.base import AbsaResult, AspectSentiment, SentimentResult

    load_aspect_weights.cache_clear()
    weights = load_aspect_weights()
    assert weights == {
        "customer_service": 1.0,
        "refund_payment": 1.0,
        "product_quality": 0.8,
        "shipping": 0.7,
        "general": 0.5,
    }

    custom_aspects = tmp_path / "aspects.yaml"
    custom_aspects.write_text(
        """
aspects:
  - id: billing
    weight: 1.5
  - id: feedback
""",
        encoding="utf-8",
    )
    assert load_aspect_weights(custom_aspects) == {"billing": 1.5, "feedback": 0.5}
    assert load_aspect_weights(tmp_path / "missing.yaml") == {}

    absa = AbsaResult(
        overall=SentimentResult(label="negative", confidence=0.8),
        aspects=[AspectSentiment(aspect="refund_payment", sentiment="negative", confidence=1.0)],
    )
    bd = calculate_priority(absa, "Please check this.", aspect_weights={})
    assert bd.aspect_bonus == 5.0


def test_intensity_extractor_question_marks_triple():
    from ticket_triage.core.priority.intensity_extractor import extract_intensity_bonus
    from ticket_triage.core.priority.priority_engine import calculate_priority
    from ticket_triage.core.sentiment.base import AbsaResult, SentimentResult

    res_triple = extract_intensity_bonus("Where is my refund???", is_negative_overall=True)
    assert res_triple.has_question_marks is True
    assert res_triple.bonus == 5.0
    assert res_triple.reason is not None and "???" in res_triple.reason

    res_double = extract_intensity_bonus("Where is my refund??", is_negative_overall=True)
    assert res_double.has_question_marks is False
    assert res_double.bonus == 0.0

    res_neutral = extract_intensity_bonus("Where is my order???", is_negative_overall=False)
    assert res_neutral.has_question_marks is True
    assert res_neutral.bonus == 0.0

    absa = AbsaResult(overall=SentimentResult(label="negative", confidence=0.8), aspects=[])
    bd = calculate_priority(absa, "Why has nothing shipped yet???")
    assert bd.intensity_bonus == 5.0
