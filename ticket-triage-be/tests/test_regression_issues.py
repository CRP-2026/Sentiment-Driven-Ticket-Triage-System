from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from starlette.testclient import TestClient

from ticket_triage.api.main import app
from ticket_triage.api.schemas import (
    AspectStatItem,
    HealthResponse,
    StatsOverviewResponse,
    StatusEnum,
    StatusUpdateIn,
    TicketCreateIn,
    TicketOut,
)
from ticket_triage.core.preprocessing.lang_validator import validate_english
from ticket_triage.core.preprocessing.normalizer import clean_text
from ticket_triage.core.priority.priority_engine import calculate_priority
from ticket_triage.core.queue.priority_queue import TicketPriorityQueue
from ticket_triage.core.sentiment.base import AbsaResult, AspectSentiment, SentimentResult
from ticket_triage.core.sentiment.mock import MockSentimentModel


# ==============================================================================
# Issue 1: Langdetect nhận nhầm câu ngắn tiếng Anh thành ngoại ngữ
# ==============================================================================
@pytest.mark.parametrize(
    "short_en_text",
    [
        "Item arrived broken",
        "Order missing",
        "Need help",
        "Where is my package?",
        "Cancel my subscription",
    ],
)
def test_issue_1_short_english_sentences_not_flagged_as_foreign(short_en_text: str):
    res = validate_english(short_en_text)
    assert res.is_english is True, f"'{short_en_text}' should be recognized as English"
    assert res.detected_lang == "en"
    assert res.needs_manual_review is False


def test_issue_1_non_english_still_flagged_correctly():
    res = validate_english("Tôi cần trợ giúp đổi sản phẩm bị lỗi ngay lập tức.")
    assert res.is_english is False
    assert res.needs_manual_review is True


# ==============================================================================
# Issue 2: Logic phủ định triệt tiêu từ khóa khẩn cấp thật (_is_negated)
# ==============================================================================
def test_issue_2_negation_does_not_suppress_real_incident_keywords():
    absa = AbsaResult(
        overall=SentimentResult(label="negative", confidence=0.90),
        aspects=[AspectSentiment(aspect="refund_payment", sentiment="negative", confidence=0.90)],
    )

    # Khách hàng khiếu nại "chưa nhận được tiền hoàn" -> từ khóa "refund" phải được cộng điểm
    text_refund = "I did not receive my refund yet."
    breakdown_refund = calculate_priority(absa, text_refund)
    assert breakdown_refund.urgency_bonus > 0.0, "Incident keyword 'refund' must not be negated"
    assert any("refund" in r.lower() for r in breakdown_refund.reasons)

    # Trong khi đó "not urgent" phải bị triệt tiêu điểm khẩn cấp
    text_not_urgent = "This request is not urgent, please reply when you can."
    breakdown_urgent = calculate_priority(
        AbsaResult(overall=SentimentResult(label="neutral", confidence=0.8), aspects=[]),
        text_not_urgent,
    )
    assert breakdown_urgent.urgency_bonus == 0.0, "'not urgent' must suppress urgency bonus"


# ==============================================================================
# Issue 3: Mock model dùng Substring matching & Random không seed
# ==============================================================================
def test_issue_3_mock_model_word_boundary_and_deterministic():
    model = MockSentimentModel()

    # 1. "issue" không được nhận nhầm thành "sue" (kiện tụng)
    res_issue = model.predict("I have an issue with my login credentials.", candidates=["customer_service"])
    assert res_issue.overall.label != "negative", "Word 'issue' must not match negative keyword 'sue'"

    # 2. "goodbye" không được nhận nhầm thành "good" (tích cực)
    res_goodbye = model.predict("Goodbye.", candidates=["general"])
    assert res_goodbye.overall.label != "positive", "Word 'goodbye' must not match positive keyword 'good'"

    # 3. Tính tất định (deterministic) với cùng một văn bản
    text_sample = "The package arrived in bad condition and was completely damaged."
    run_1 = model.predict(text_sample, candidates=["shipping"])
    run_2 = model.predict(text_sample, candidates=["shipping"])
    assert run_1.overall.confidence == run_2.overall.confidence
    assert run_1.aspects[0].confidence == run_2.aspects[0].confidence


# ==============================================================================
# Issue 4: clean_text làm hỏng từ gốc tiếng Anh
# ==============================================================================
def test_issue_4_clean_text_preserves_double_letters():
    text_cool = "This support agent is so coool and helpful!"
    cleaned_cool = clean_text(text_cool)
    assert "cool" in cleaned_cool, f"Expected 'cool' in '{cleaned_cool}'"
    assert "col" not in cleaned_cool

    text_good = "Very goood service, thank you."
    cleaned_good = clean_text(text_good)
    assert "good" in cleaned_good, f"Expected 'good' in '{cleaned_good}'"
    assert "god" not in cleaned_good


# ==============================================================================
# Issue 5: Nhận ticket rỗng / spam / DoS
# ==============================================================================
@pytest.mark.parametrize(
    "invalid_content",
    [
        "   ",
        "<b></b>",
        "...",
        "!!!",
        "a",
        "<b>   </b>",
        "x" * 5001,
    ],
)
def test_issue_5_reject_empty_or_spam_or_oversized_payloads(invalid_content: str):
    with pytest.raises(ValidationError):
        TicketCreateIn(content=invalid_content)


def test_issue_5_accept_valid_content():
    valid = TicketCreateIn(content="My order #9923 was damaged during delivery.")
    assert valid.content == "My order #9923 was damaged during delivery."


# ==============================================================================
# Issue 6: Múi giờ UTC trả về có hậu tố 'Z'
# ==============================================================================
def test_issue_6_utc_datetime_serialization_has_z_suffix():
    now_utc = datetime(2026, 10, 26, 4, 30, 53, tzinfo=timezone.utc)
    ticket_dict = {
        "id": 1,
        "content": "Test content",
        "language_flag": "en",
        "needs_manual_review": False,
        "low_confidence": False,
        "priority_score": 75.0,
        "priority_level": "CRITICAL",
        "status": StatusEnum.NEW,
        "created_at": now_utc,
        "updated_at": now_utc,
        "aspects": [],
    }
    ticket_out = TicketOut(**ticket_dict)
    json_data = ticket_out.model_dump(mode="json")

    assert json_data["created_at"].endswith("Z"), f"Expected 'Z' at end of {json_data['created_at']}"
    assert json_data["updated_at"].endswith("Z"), f"Expected 'Z' at end of {json_data['updated_at']}"
    assert json_data["created_at"] == "2026-10-26T04:30:53Z"


# ==============================================================================
# Issue 7: Hàng đợi heapq đồng bộ khi Ticket được resolved
# ==============================================================================
def test_issue_7_priority_queue_remove_and_sync():
    queue = TicketPriorityQueue()
    t1_dt = datetime.now(timezone.utc)
    queue.push(ticket_id=101, priority_score=85.0, created_at=t1_dt)
    queue.push(ticket_id=102, priority_score=60.0, created_at=t1_dt)
    assert queue.size() == 2

    # Loại bỏ ticket 101 khi đã resolved
    removed = queue.remove(101)
    assert removed is True
    assert queue.size() == 1

    remaining = queue.pop()
    assert remaining is not None
    assert remaining.ticket_id == 102
    assert queue.size() == 0


def test_issue_7_update_status_api_synchronizes_queue(client: TestClient):
    # Tạo ticket
    create_res = client.post("/api/v1/tickets", json={"content": "Immediate refund required for order #54321!"})
    assert create_res.status_code == 201
    ticket_id = create_res.json()["id"]

    # Kiểm tra queue size ban đầu
    health_before = client.get("/api/v1/health").json()
    size_before = health_before["queue_size"]
    assert size_before >= 1

    # Chuyển trạng thái sang resolved
    client.patch(f"/api/v1/tickets/{ticket_id}/status", json={"status": "in_progress"})
    patch_res = client.patch(f"/api/v1/tickets/{ticket_id}/status", json={"status": "resolved"})
    assert patch_res.status_code == 200

    # Kiểm tra queue size đã giảm
    health_after = client.get("/api/v1/health").json()
    assert health_after["queue_size"] == size_before - 1


# ==============================================================================
# Issue 8: Hợp đồng API chuẩn hóa (/stats, StatusEnum, HealthResponse)
# ==============================================================================
def test_issue_8_stats_and_health_schemas(client: TestClient):
    health_res = client.get("/api/v1/health")
    assert health_res.status_code == 200
    health_data = HealthResponse(**health_res.json())
    assert hasattr(health_data, "is_mock")
    assert hasattr(health_data, "model_loaded")

    stats_res = client.get("/api/v1/stats/overview")
    assert stats_res.status_code == 200
    overview_data = StatsOverviewResponse(**stats_res.json())
    assert overview_data.total_tickets >= 0

    aspects_res = client.get("/api/v1/stats/aspects")
    assert aspects_res.status_code == 200
    aspects_data = [AspectStatItem(**item) for item in aspects_res.json()]
    assert isinstance(aspects_data, list)

