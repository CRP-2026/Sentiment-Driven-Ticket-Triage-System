from dataclasses import dataclass, field
from typing import Literal

Sentiment = Literal["negative", "neutral", "positive"]

@dataclass(frozen=True)
class SentimentResult:
    """Cảm xúc tổng thể của ticket."""
    label: Sentiment
    confidence: float           # [0.0, 1.0]

@dataclass(frozen=True)
class AspectSentiment:
    """Khía cạnh phát hiện được kèm trạng thái cảm xúc tương ứng."""
    aspect: str                 # ID định danh từ configs/aspects.yaml
    sentiment: Sentiment        # negative | neutral | positive
    confidence: float           # [0.0, 1.0]
    terms: tuple[str, ...] = ()  # Cụm từ trích xuất (chỉ có khi ENABLE_ABTE=true)

@dataclass(frozen=True)
class AbsaResult:
    """Hợp đồng dữ liệu đầu ra chuẩn hóa của Bài toán 1 bàn giao cho Bài toán 2."""
    overall: SentimentResult
    aspects: list[AspectSentiment] = field(default_factory=list)

class BaseSentimentModel:
    """Interface trừu tượng chung cho các mô hình ABSA (Mock / Baseline / NLI Fine-tuned)."""

    def predict(self, text: str, candidates: list[str] | None = None) -> AbsaResult:
        raise NotImplementedError
