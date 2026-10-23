from ticket_triage.core.preprocessing.keyword_prefilter import filter_candidate_aspects
from ticket_triage.core.preprocessing.lang_validator import validate_english
from ticket_triage.core.preprocessing.normalizer import clean_text
from ticket_triage.core.preprocessing.pipeline import preprocess_ticket


def test_clean_text_basic():
    raw = "<b>Hello</b> <a href='https://example.com'>click here</a>   world!!! soooo baaaad!!!!"
    cleaned = clean_text(raw)
    assert "<b>" not in cleaned
    assert "https://" not in cleaned
    assert "so" in cleaned
    assert "bad" in cleaned
    assert "!!!" in cleaned

def test_clean_text_preserves_caps_and_negations():
    raw = "I DID NOT receive my item and I am ANGRY!!!"
    cleaned = clean_text(raw)
    assert "DID NOT" in cleaned
    assert "ANGRY" in cleaned
    assert "!!!" in cleaned

def test_validate_english_valid():
    res = validate_english("This is an English customer support request about my package.")
    assert res.is_english is True
    assert res.detected_lang == "en"
    assert res.needs_manual_review is False

def test_validate_english_non_english():
    res = validate_english("Tôi muốn khiếu nại về đơn hàng giao trễ nhiều ngày.")
    assert res.is_english is False
    assert res.needs_manual_review is True

def test_filter_candidate_aspects():
    text_shipping = "My package has not arrived and tracking is delayed."
    candidates = filter_candidate_aspects(text_shipping)
    assert "shipping" in candidates

    text_refund = "Please issue a refund for the double charge on my credit card."
    candidates = filter_candidate_aspects(text_refund)
    assert "refund_payment" in candidates

    text_unknown = "Hello there, just checking in."
    candidates = filter_candidate_aspects(text_unknown)
    assert candidates == ["general"]

def test_preprocess_ticket_pipeline():
    res = preprocess_ticket("Order #1234 was damaged and broken! Please refund immediately.")
    assert res.is_english is True
    assert "refund_payment" in res.candidate_aspects or "product_quality" in res.candidate_aspects
    assert res.needs_manual_review is False
