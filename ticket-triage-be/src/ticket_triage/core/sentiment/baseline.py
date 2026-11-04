import logging
from pathlib import Path
from typing import Any

import yaml

from .base import AbsaResult, AspectSentiment, BaseSentimentModel, SentimentResult

logger = logging.getLogger(__name__)

def load_aspect_hypotheses(yaml_path: Path | str | None = None) -> dict:
    """Nạp template và định nghĩa khía cạnh từ configs/aspect_hypotheses.yaml."""
    if yaml_path is None:
        try:
            from ...settings import settings
            yaml_path = Path(settings.configs_dir) / "aspect_hypotheses.yaml"
        except (ImportError, AttributeError):
            yaml_path = Path("configs/aspect_hypotheses.yaml")
    else:
        yaml_path = Path(yaml_path)

    if yaml_path.is_file():
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except (OSError, yaml.YAMLError):
            return {}
    return {}

class ZeroShotNliModel(BaseSentimentModel):
    """Mô hình ABSA Zero-shot NLI (distilbart-mnli / deberta-v3-base-zeroshot):
    - Tải lazy để máy không cài torch vẫn chạy mock bình thường.
    - Dự đoán cảm xúc từng khía cạnh qua NLI cross-encoder hypothesis testing.
    """

    def __init__(self, model_name_or_path: str = "valhalla/distilbart-mnli-12-3"):
        self.model_name_or_path = model_name_or_path
        self._classifier: Any = None
        self._has_logged_fallback = False
        self._config = load_aspect_hypotheses()

    @property
    def is_mock(self) -> bool:
        self._ensure_loaded()
        return self._classifier is None

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
        except (ImportError, OSError, RuntimeError, ValueError) as e:
            if not self._has_logged_fallback:
                logger.warning(
                    "CRITICAL WARNING: Could not load transformers pipeline (%s). Falling back to MockSentimentModel! "
                    "System is operating in simulated mock mode.",
                    e,
                )
                self._has_logged_fallback = True
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

        aspect_names = self._config.get("aspect_names", {})
        aspect_template = self._config.get(
            "aspect_sentiment_template",
            "The customer's feedback regarding {aspect} is {sentiment}."
        )

        aspect_items: list[AspectSentiment] = []
        for asp in (candidates or ["general"]):
            asp_clean = aspect_names.get(asp, asp.replace("_", " "))
            template = aspect_template.replace("{aspect}", asp_clean).replace("{sentiment}", "{}")
            asp_res = self._classifier(
                text,
                candidate_labels=candidate_labels,
                hypothesis_template=template,
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
