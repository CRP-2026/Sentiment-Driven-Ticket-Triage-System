import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from ..sentiment.base import AbsaResult
from .intensity_extractor import extract_intensity_bonus

DEFAULT_ASPECT_WEIGHTS = {
    "customer_service": 1.0,
    "refund_payment": 1.0,
    "product_quality": 0.8,
    "shipping": 0.7,
    "general": 0.5,
}

CRITICAL_KEYWORDS = [
    "urgent", "immediately", "asap", "lawsuit", "sue", "lawyer",
    "fraud", "scam", "chargeback", "stolen", "charged twice"
]
HIGH_KEYWORDS = [
    "broken", "refund", "cancel", "not working", "never received",
    "dispute", "missing", "damaged", "overcharged"
]

DE_ESCALATION_KEYWORDS = {
    "urgent", "immediately", "asap", "emergency", "rush", "critical"
}

NEGATION_PATTERNS = [
    r"\bnot\s+", r"\bnever\s+", r"\bno\s+", r"\bwon't\s+", r"\bdoesn't\s+",
    r"\bdon't\s+", r"\bdidn't\s+", r"\bwithout\s+", r"\bstop\s+"
]

def load_priority_rules(yaml_path: Path | str | None = None) -> dict:
    """Nạp cấu hình từ configs/priority_rules.yaml vào runtime."""
    if yaml_path is None:
        try:
            from ...settings import settings
            yaml_path = Path(settings.configs_dir) / "priority_rules.yaml"
        except (ImportError, AttributeError):
            yaml_path = Path("configs/priority_rules.yaml")
    else:
        yaml_path = Path(yaml_path)

    if yaml_path.is_file():
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except (OSError, yaml.YAMLError):
            return {}
    return {}

@dataclass(frozen=True)
class PriorityBreakdown:
    score: float
    base: float
    urgency_bonus: float
    intensity_bonus: float
    aspect_bonus: float
    level: str
    dominant_aspect: str | None
    reasons: list[str] = field(default_factory=list)

def _split_sentences(text: str) -> list[str]:
    chunks = re.split(r"[.!?\n]+", text)
    return [c.strip() for c in chunks if c.strip()]

def _is_negated(sentence: str, kw_index: int, keyword: str) -> bool:
    """Chỉ phủ định các từ khóa tính chất khẩn cấp (hạ nhiệt: not urgent, no rush).
    Tuyệt đối không phủ định các từ khóa sự cố/khiếu nại (refund, broken, charged twice...).
    """
    if keyword.lower() not in DE_ESCALATION_KEYWORDS:
        return False

    prefix = sentence[:kw_index]
    for neg in NEGATION_PATTERNS:
        match = re.search(neg, prefix, re.IGNORECASE)
        if match and (kw_index - match.end() < 25):
            return True
    return False

def calculate_priority(
    result: AbsaResult,
    text: str,
    aspect_weights: dict[str, float] | None = None,
    urgency_cap: float | None = None,
    aspect_cap: float | None = None,
    rules_config: dict | None = None,
) -> PriorityBreakdown:
    """Hàm tính toán điểm ưu tiên rule-based toán học minh bạch (Worst-aspect-wins):
    score = min(100.0, base + urgency_bonus + intensity_bonus + aspect_bonus)
    """
    rules = rules_config if rules_config is not None else load_priority_rules()
    critical_kws = rules.get("urgency_keywords", {}).get("critical", CRITICAL_KEYWORDS)
    high_kws = rules.get("urgency_keywords", {}).get("high", HIGH_KEYWORDS)

    cap_urgency = urgency_cap if urgency_cap is not None else rules.get("urgency_cap", 30.0)
    cap_aspect = aspect_cap if aspect_cap is not None else rules.get("aspect_cap", 20.0)

    weights = aspect_weights or DEFAULT_ASPECT_WEIGHTS
    reasons: list[str] = []

    # 1. Điểm nền cảm xúc tổng thể (Base Score)
    overall = result.overall
    if overall.label == "negative":
        base = round(60.0 * overall.confidence, 2)
        reasons.append(f"Cảm xúc tổng thể tiêu cực ({overall.confidence:.2f}): base = {base}")
    elif overall.label == "neutral":
        base = 20.0
        reasons.append("Cảm xúc tổng thể trung tính: base = 20.0")
    else: # positive
        base = 5.0
        reasons.append("Cảm xúc tổng thể tích cực: base = 5.0")

    # 2. Điểm từ khóa khẩn cấp (Urgency Bonus)
    sentences = _split_sentences(text)
    total_sentences = len(sentences)
    urgency_bonus = 0.0
    detected_keywords: set[str] = set()

    for i, sent in enumerate(sentences):
        sent_lower = sent.lower()
        is_last = (i == total_sentences - 1)

        for kw in (critical_kws + high_kws):
            if kw in detected_keywords:
                continue

            pattern = r"\b" + re.escape(kw) + r"\b"
            match = re.search(pattern, sent_lower)
            if match:
                if _is_negated(sent_lower, match.start(), kw):
                    continue # Bị phủ định -> bỏ qua

                detected_keywords.add(kw)
                # Phân tầng điểm rõ ràng: Critical nhận điểm cao hơn High
                if kw in critical_kws:
                    points = 20.0 if is_last else 15.0
                    kw_tier = "CRITICAL"
                else:
                    points = 15.0 if is_last else 10.0
                    kw_tier = "HIGH"

                urgency_bonus += points
                loc_str = "câu kết" if is_last else f"câu #{i+1}"
                reasons.append(f"Từ khóa khẩn cấp [{kw_tier}] '{kw}' ở {loc_str}: +{points}")

    urgency_bonus = min(cap_urgency, round(urgency_bonus, 2))

    # 3. Điểm cường độ câu (Intensity Bonus)
    intensity_res = extract_intensity_bonus(text, is_negative_overall=(overall.label == "negative"))
    intensity_bonus = intensity_res.bonus
    if intensity_res.reason:
        reasons.append(intensity_res.reason)

    # 4. Điểm khía cạnh tiêu cực (Aspect Bonus - Worst Aspect Wins)
    aspect_bonus = 0.0
    dominant_aspect = None

    negative_aspects = [
        asp for asp in result.aspects
        if asp.sentiment == "negative"
    ]

    if negative_aspects:
        # Sắp xếp theo weight * confidence giảm dần
        sorted_negs = sorted(
            negative_aspects,
            key=lambda x: weights.get(x.aspect, 0.5) * x.confidence,
            reverse=True
        )

        worst = sorted_negs[0]
        dominant_aspect = worst.aspect
        worst_weight = weights.get(worst.aspect, 0.5)
        worst_val = worst_weight * worst.confidence * 10.0
        aspect_bonus += worst_val
        reasons.append(
            f"Khía cạnh nghiêm trọng nhất '{worst.aspect}' (trọng số {worst_weight}, conf {worst.confidence:.2f}): +{worst_val:.2f}"
        )

        # Phạt dồn các khía cạnh tiêu cực còn lại (25%)
        for other in sorted_negs[1:]:
            other_weight = weights.get(other.aspect, 0.5)
            other_val = 0.25 * (other_weight * other.confidence * 10.0)
            aspect_bonus += other_val
            reasons.append(
                f"Khía cạnh tiêu cực cộng thêm '{other.aspect}' (25% phạt): +{other_val:.2f}"
            )

        aspect_bonus = min(cap_aspect, round(aspect_bonus, 2))
    else:
        # Nếu không có khía cạnh tiêu cực, lấy khía cạnh đầu tiên có trọng số lớn nhất làm dominant
        if result.aspects:
            dominant_aspect = max(result.aspects, key=lambda x: weights.get(x.aspect, 0.5)).aspect

    # Tổng điểm và làm tròn
    total_score = round(min(100.0, base + urgency_bonus + intensity_bonus + aspect_bonus), 2)

    # Phân cấp mức ưu tiên dựa trên cấu hình ngưỡng (Mặc định 70/30)
    thresholds = rules.get("priority_thresholds", {})
    high_threshold = thresholds.get("high", 70.0)
    medium_threshold = thresholds.get("medium", 30.0)

    if total_score >= high_threshold:
        level = "CRITICAL"
    elif total_score >= medium_threshold:
        level = "MEDIUM"
    else:
        level = "LOW"

    return PriorityBreakdown(
        score=total_score,
        base=base,
        urgency_bonus=urgency_bonus,
        intensity_bonus=intensity_bonus,
        aspect_bonus=aspect_bonus,
        level=level,
        dominant_aspect=dominant_aspect,
        reasons=reasons,
    )
