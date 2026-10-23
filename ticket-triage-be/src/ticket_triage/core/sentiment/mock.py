import random
from .base import BaseSentimentModel, AbsaResult, SentimentResult, AspectSentiment

class MockSentimentModel(BaseSentimentModel):
    """Mô hình giả lập trả kết quả chuẩn hóa để Bài toán 2 và frontend phát triển song song."""

    def predict(self, text: str, candidates: list[str] | None = None) -> AbsaResult:
        text_lower = text.lower() if text else ""
        aspect_keys = candidates or ["general"]

        # 1. Nhận diện các tín hiệu cảm xúc dựa trên từ vựng đơn giản để mock có tính thực tế cao
        neg_indicators = ["broken", "refund", "chargeback", "urgent", "bad", "terrible", "worst", "sue", "lawyer", "never", "hate", "scam", "fraud", "stolen"]
        pos_indicators = ["thank", "thanks", "great", "excellent", "love", "awesome", "fast", "helpful", "good", "perfect"]

        has_neg = any(w in text_lower for w in neg_indicators)
        has_pos = any(w in text_lower for w in pos_indicators)

        if has_neg and not has_pos:
            overall_label = "negative"
            overall_conf = round(random.uniform(0.85, 0.98), 2)
        elif has_pos and not has_neg:
            overall_label = "positive"
            overall_conf = round(random.uniform(0.85, 0.98), 2)
        elif has_neg and has_pos:
            overall_label = "negative"
            overall_conf = round(random.uniform(0.70, 0.88), 2)
        else:
            overall_label = "neutral"
            overall_conf = round(random.uniform(0.75, 0.90), 2)

        # 2. Sinh AspectSentiment theo candidate list
        aspect_list: list[AspectSentiment] = []
        for asp in aspect_keys:
            # Gán cảm xúc tương ứng cho khía cạnh
            if asp in ["refund_payment", "product_quality", "shipping", "customer_service"] and has_neg:
                asp_sentiment = "negative"
                asp_conf = round(random.uniform(0.80, 0.96), 2)
            elif asp in ["customer_service", "shipping"] and has_pos:
                asp_sentiment = "positive"
                asp_conf = round(random.uniform(0.80, 0.96), 2)
            else:
                asp_sentiment = overall_label
                asp_conf = round(random.uniform(0.70, 0.90), 2)

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
