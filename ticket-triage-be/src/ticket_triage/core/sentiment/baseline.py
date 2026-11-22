import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from ..config_utils import find_config_file as _find_config_file
from .base import AbsaResult, AspectSentiment, BaseSentimentModel, SentimentResult

logger = logging.getLogger(__name__)

ALL_CAPS_WORD_RE = re.compile(r"\b[A-Z]{2,}\b")


def normalize_caps_for_nli(text: str) -> str:
    """Chuyển các từ viết IN HOA toàn bộ (ALL CAPS >= 2 ký tự) về chữ thường trước khi đưa vào NLI
    để tránh Tokenizer của DeBERTa/BART cắt vụn sub-token làm giảm confidence,
    trong khi văn bản gốc vẫn giữ nguyên CAPS LOCK cho bộ tính Intensity Bonus.
    """
    if not text:
        return ""
    return ALL_CAPS_WORD_RE.sub(lambda m: m.group(0).lower(), text)

DEFAULT_HF_MODELS: dict[str, str] = {
    "baseline": "valhalla/distilbart-mnli-12-3",
    "deberta": "MoritzLaurer/deberta-v3-base-zeroshot-v1.1-all-33",
}


@lru_cache(maxsize=4)
def _read_hypotheses_yaml(path_str: str) -> dict[str, Any]:
    try:
        with open(path_str, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, dict) else {}
    except (OSError, yaml.YAMLError):
        return {}


def load_aspect_hypotheses(yaml_path: Path | str | None = None) -> dict[str, Any]:
    """Nạp template và định nghĩa khía cạnh từ configs/aspect_hypotheses.yaml."""
    if yaml_path is not None:
        target_path = Path(yaml_path)
    else:
        target_path = _find_config_file("aspect_hypotheses.yaml")

    if target_path is not None and target_path.is_file():
        return _read_hypotheses_yaml(str(target_path.resolve()))
    return {}


class ZeroShotNliModel(BaseSentimentModel):
    """Mô hình ABSA Zero-shot NLI (distilbart-mnli / deberta-v3-base-zeroshot):
    - Tải lazy để máy không cài torch vẫn chạy mock bình thường.
    - Dự đoán cảm xúc từng khía cạnh qua NLI cross-encoder hypothesis testing.
    """

    def __init__(
        self,
        model_name_or_path: str = DEFAULT_HF_MODELS["baseline"],
        hypotheses_path: Path | str | None = None,
        hypotheses: dict[str, Any] | None = None,
    ):
        self.model_name_or_path = model_name_or_path
        self._classifier: Any = None
        self._has_logged_fallback = False
        self._config = (
            hypotheses if hypotheses is not None else load_aspect_hypotheses(hypotheses_path)
        )

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

        nli_text = normalize_caps_for_nli(text)

        sentiment_cfg = self._config.get("sentiments", {})
        if sentiment_cfg:
            verbalizer_to_sentiment = {v: k for k, v in sentiment_cfg.items()}
            candidate_labels = list(verbalizer_to_sentiment.keys())
        else:
            verbalizer_to_sentiment = {k: k for k in ["negative", "neutral", "positive"]}
            candidate_labels = ["negative", "neutral", "positive"]

        overall_template = self._config.get(
            "overall_sentiment_template",
            "The sentiment of this customer review is {}.",
        )
        overall_res = self._classifier(
            nli_text,
            candidate_labels=candidate_labels,
            hypothesis_template=overall_template,
        )

        top_verbalizer = str(overall_res["labels"][0])
        top_label = verbalizer_to_sentiment.get(top_verbalizer, top_verbalizer)
        top_conf = round(float(overall_res["scores"][0]), 2)

        aspect_names = self._config.get("aspect_names", {})
        aspect_template = self._config.get(
            "aspect_sentiment_template",
            "The customer's feedback regarding {aspect} is {sentiment}."
        )

        aspect_candidates = ["general"] if candidates is None else list(candidates)

        # Giải pháp B (1): Zero-shot Aspect Detection Fallback khi bộ lọc từ khóa chỉ ra ['general']
        # nhưng câu mang cảm xúc tiêu cực rõ rệt và có cấu hình aspect_detection_template + aspect_names.
        detection_template = self._config.get("aspect_detection_template")
        if (
            aspect_candidates == ["general"]
            and top_label == "negative"
            and isinstance(detection_template, str)
            and "{aspect}" in detection_template
            and isinstance(aspect_names, dict)
        ):
            specific_map = {
                str(v): str(k)
                for k, v in aspect_names.items()
                if str(k) != "general" and str(v).strip()
            }
            if specific_map:
                det_template = detection_template.replace("{aspect}", "{}")
                det_res = self._classifier(
                    nli_text,
                    candidate_labels=list(specific_map.keys()),
                    hypothesis_template=det_template,
                )
                det_labels = det_res.get("labels", [])
                det_scores = det_res.get("scores", [])
                detected_aspects = [
                    specific_map[str(lbl)]
                    for lbl, sc in zip(det_labels, det_scores)
                    if str(lbl) in specific_map and float(sc) >= 0.45
                ]
                if detected_aspects:
                    aspect_candidates = detected_aspects[:2]

        aspect_items: list[AspectSentiment] = []
        for asp in aspect_candidates:
            asp_clean = aspect_names.get(asp, asp.replace("_", " "))
            template = aspect_template.replace("{aspect}", asp_clean).replace("{sentiment}", "{}")
            asp_res = self._classifier(
                nli_text,
                candidate_labels=candidate_labels,
                hypothesis_template=template,
            )
            asp_verbalizer = str(asp_res["labels"][0])
            asp_label = verbalizer_to_sentiment.get(asp_verbalizer, asp_verbalizer)
            asp_conf = round(float(asp_res["scores"][0]), 2)

            aspect_items.append(
                AspectSentiment(
                    aspect=asp,
                    sentiment=asp_label, # type: ignore
                    confidence=asp_conf,
                )
            )

        # Giải pháp B (2): Zero-shot Semantic Urgency Evaluation từ model NLI
        sem_urgency_level: Any = None
        sem_urgency_conf: float = 0.0
        urgency_cfg = self._config.get("urgency_levels")
        if top_label == "negative" and isinstance(urgency_cfg, dict) and urgency_cfg:
            urg_verbalizer_to_level = {str(v): str(k) for k, v in urgency_cfg.items() if str(v).strip()}
            urg_labels = list(urg_verbalizer_to_level.keys())
            if urg_labels:
                urg_template = str(
                    self._config.get("urgency_hypothesis_template", "This customer ticket represents {}.")
                )
                urg_res = self._classifier(
                    nli_text,
                    candidate_labels=urg_labels,
                    hypothesis_template=urg_template,
                )
                top_urg_verb = str(urg_res["labels"][0])
                mapped_level = urg_verbalizer_to_level.get(top_urg_verb)
                if mapped_level in ("critical", "high", "normal"):
                    sem_urgency_level = mapped_level
                    sem_urgency_conf = round(float(urg_res["scores"][0]), 2)

        return AbsaResult(
            overall=SentimentResult(label=top_label, confidence=top_conf), # type: ignore
            aspects=aspect_items,
            semantic_urgency_level=sem_urgency_level,
            semantic_urgency_confidence=sem_urgency_conf,
        )
