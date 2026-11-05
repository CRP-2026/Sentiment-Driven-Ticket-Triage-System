import hashlib
import random
import re

from .base import AbsaResult, AspectSentiment, BaseSentimentModel, SentimentResult

NEG_INDICATORS = [
    "broken", "refund", "chargeback", "urgent", "bad", "terrible", "worst",
    "sue", "lawyer", "never", "hate", "scam", "fraud", "stolen"
]
POS_INDICATORS = [
    "thank", "thanks", "great", "excellent", "love", "awesome",
    "fast", "helpful", "good", "perfect"
]

def _matches_any_word(words: list[str], text: str) -> bool:
    for w in words:
        if re.search(rf"\b{re.escape(w)}\b", text):
            return True
    return False


class MockSentimentModel(BaseSentimentModel):
    """Mô hình giả lập trả kết quả chuẩn hóa để Bài toán 2 và frontend phát triển song song."""

    is_mock: bool = True

    def predict(self, text: str, candidates: list[str] | None = None) -> AbsaResult:
        text_lower = text.lower() if text else ""
        aspect_keys = candidates or ["general"]

        # Cố định seed dựa trên hash nội dung để kiểm thử mang tính xác định (deterministic)
        seed_val = int(hashlib.md5(text_lower.encode("utf-8")).hexdigest()[:8], 16) if text_lower else 42
        rng = random.Random(seed_val)

        # 1. Nhận diện các tín hiệu cảm xúc dựa trên ranh giới từ (\b) để tránh lỗi substring
        has_neg = _matches_any_word(NEG_INDICATORS, text_lower)
        has_pos = _matches_any_word(POS_INDICATORS, text_lower)

        if has_neg and not has_pos:
            overall_label = "negative"
            overall_conf = round(rng.uniform(0.85, 0.98), 2)
        elif has_pos and not has_neg:
            overall_label = "positive"
            overall_conf = round(rng.uniform(0.85, 0.98), 2)
        elif has_neg and has_pos:
            overall_label = "negative"
            overall_conf = round(rng.uniform(0.70, 0.88), 2)
        else:
            overall_label = "neutral"
            overall_conf = round(rng.uniform(0.75, 0.90), 2)

        # 2. Sinh AspectSentiment theo candidate list
        aspect_list: list[AspectSentiment] = []
        for asp in aspect_keys:
            # Gán cảm xúc tương ứng cho khía cạnh
            if asp in ["refund_payment", "product_quality", "shipping", "customer_service"] and has_neg:
                asp_sentiment = "negative"
                asp_conf = round(rng.uniform(0.80, 0.96), 2)
            elif asp in ["customer_service", "shipping"] and has_pos:
                asp_sentiment = "positive"
                asp_conf = round(rng.uniform(0.80, 0.96), 2)
            else:
                asp_sentiment = overall_label
                asp_conf = round(rng.uniform(0.70, 0.90), 2)

            aspect_list.append(
                AspectSentiment(
                    aspect=asp,
                    sentiment=asp_sentiment,
                    confidence=asp_conf,
                )
            )

        return AbsaResult(
            overall=SentimentResult(label=overall_label, confidence=overall_conf),
            aspects=aspect_list,
        )
