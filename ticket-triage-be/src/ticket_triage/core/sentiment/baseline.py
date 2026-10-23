import logging
from typing import Any
from .base import BaseSentimentModel, AbsaResult, SentimentResult, AspectSentiment

logger = logging.getLogger(__name__)

class ZeroShotNliModel(BaseSentimentModel):
    """Mô hình ABSA Zero-shot NLI (distilbart-mnli / deberta-v3-base-zeroshot):
    - Tải lazy để máy không cài torch vẫn chạy mock bình thường.
    - Dự đoán cảm xúc từng khía cạnh qua NLI cross-encoder hypothesis testing.
    """

    def __init__(self, model_name_or_path: str = "valhalla/distilbart-mnli-12-3"):
        self.model_name_or_path = model_name_or_path
        self._classifier: Any = None

    def _ensure_loaded(self) -> None:
        if self._classifier is not None:
            return

        try:
            from transformers import pipeline
            self._classifier = pipeline(
                "zero-shot-classification",
                model=self.model_name_or_path,
                device=-1, # CPU mặc định
            )
            logger.info("Loaded Zero-shot NLI model: %s", self.model_name_or_path)
        except Exception as e:
            logger.warning("Could not load transformers pipeline (%s). Falling back to mock.", e)
            self._classifier = None

    def predict(self, text: str, candidates: list[str] | None = None) -> AbsaResult:
        self._ensure_loaded()
        if self._classifier is None:
            from .mock import MockSentimentModel
            return MockSentimentModel().predict(text, candidates)

        candidate_labels = ["negative", "neutral", "positive"]
        overall_res = self._classifier(
            text,
            candidate_labels=candidate_labels,
            hypothesis_template="The sentiment of this customer review is {}.",
        )

        top_label = str(overall_res["labels"][0])
        top_conf = round(float(overall_res["scores"][0]), 2)

        aspect_items: list[AspectSentiment] = []
        for asp in (candidates or ["general"]):
            asp_clean = asp.replace("_", " ")
            asp_res = self._classifier(
                text,
                candidate_labels=candidate_labels,
                hypothesis_template=f"The customer's feedback regarding {asp_clean} is {{}}.",
            )
            asp_label = str(asp_res["labels"][0])
            asp_conf = round(float(asp_res["scores"][0]), 2)

            aspect_items.append(
                AspectSentiment(
                    aspect=asp,
                    sentiment=asp_label, # type: ignore
                    confidence=asp_conf,
                )
            )

        return AbsaResult(
            overall=SentimentResult(label=top_label, confidence=top_conf), # type: ignore
            aspects=aspect_items,
        )
