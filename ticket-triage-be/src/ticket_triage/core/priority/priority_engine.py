import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from ..sentiment.base import AbsaResult
from .intensity_extractor import extract_intensity_bonus

NEGATION_PATTERNS = [
    r"\bnot\s+", r"\bnever\s+", r"\bno\s+", r"\bwon't\s+", r"\bdoesn't\s+",
    r"\bdon't\s+", r"\bdidn't\s+", r"\bwithout\s+",
]

REMEDY_ACTION_KEYWORDS = frozenset({"refund", "cancel"})

CONTRAST_CLAUSE_RE = re.compile(
    r"(?:\b(?:but|however|although|though)\b|[;]|,(?=\s))",
    re.IGNORECASE,
)

RESOLUTION_PATTERNS = [
    re.compile(r"\b(?:thanks|thank\s+you)\s+for\s+resolving(?!\s+nothing\b)", re.IGNORECASE),
    re.compile(r"\brefund\s+(?:was\s+|has\s+been\s+)?received\b", re.IGNORECASE),
    re.compile(r"\b(?:received|got)\s+(?:my|the)\s+refund\b", re.IGNORECASE),
    re.compile(r"\b(?:issue|problem|ticket)\s+(?:is\s+|was\s+|has\s+been\s+|already\s+)?resolved\b", re.IGNORECASE),
    re.compile(r"\balready\s+resolved\b", re.IGNORECASE),
]

RESOLUTION_NEGATION_RE = re.compile(
    r"\b(?:not|never|no|don't|didn't|doesn't|won't|haven't|hasn't|hadn't|couldn't|isn't|wasn't|still\s+not)\s+(?:yet\s+|even\s+|actually\s+)?$",
    re.IGNORECASE,
)


def _normalize_keywords(raw_keywords: Any, fallback: list[str]) -> list[str]:
    if raw_keywords is None or not isinstance(raw_keywords, list):
        return list(fallback)
    seen: set[str] = set()
    normalized: list[str] = []
    for kw in raw_keywords:
        cleaned = str(kw).strip().lower()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            normalized.append(cleaned)
    return normalized

@dataclass(frozen=True)
class PriorityRules:
    critical_keywords: list[str] = field(default_factory=lambda: [
        "urgent", "immediately", "asap", "lawsuit", "sue", "lawyer",
        "fraud", "scam", "chargeback", "stolen", "charged twice"
    ])
    high_keywords: list[str] = field(default_factory=lambda: [
        "broken", "refund", "cancel", "not working", "never received",
        "dispute", "missing", "damaged", "overcharged"
    ])
    urgency_cap: float = 30.0
    aspect_cap: float = 20.0
    intensity_bonus: float = 5.0
    critical_last_sentence: float = 30.0
    critical_other_sentence: float = 20.0
    high_last_sentence: float = 15.0
    high_other_sentence: float = 10.0
    threshold_high: float = 70.0
    threshold_medium: float = 30.0


def _find_config_file(filename: str = "priority_rules.yaml") -> Path | None:
    """Tự động duyệt ngược từ vị trí module hiện tại và CWD để tìm file config an toàn."""
    search_roots = [Path(__file__).resolve(), Path.cwd().resolve()]

    for start_path in search_roots:
        candidates = [start_path, *start_path.parents]
        for parent in candidates:
            target = parent / "configs" / filename
            if target.is_file():
                return target

            nested_target = parent / "ticket-triage-be" / "configs" / filename
            if nested_target.is_file():
                return nested_target

    return None


def _non_negative_float(value: Any, default: float) -> float:
    if value is None:
        return default
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        return default


@lru_cache(maxsize=4)
def load_aspect_weights(yaml_path: Path | str | None = None) -> dict[str, float]:
    """Nạp trọng số khía cạnh từ aspects.yaml (Single Source of Truth)."""
    target_path = Path(yaml_path) if yaml_path is not None else _find_config_file("aspects.yaml")
    if target_path is None or not target_path.is_file():
        return {}

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except (OSError, yaml.YAMLError):
        return {}

    if not isinstance(data, dict):
        return {}

    raw_aspects = data.get("aspects")
    if not isinstance(raw_aspects, list):
        return {}

    weights: dict[str, float] = {}
    for item in raw_aspects:
        if not isinstance(item, dict):
            continue
        aspect_id = str(item.get("id", "")).strip()
        if aspect_id:
            weights[aspect_id] = _non_negative_float(item.get("weight"), 0.5)
    return weights


@lru_cache(maxsize=4)
def load_priority_rules(yaml_path: Path | str | None = None) -> PriorityRules:
    """Nạp từ khóa khẩn cấp, điểm cộng vị trí câu, trần điểm và ngưỡng phân cấp từ priority_rules.yaml."""
    if yaml_path is not None:
        target_path = Path(yaml_path)
    else:
        target_path = _find_config_file("priority_rules.yaml")

    if target_path is None or not target_path.is_file():
        return PriorityRules()

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except (OSError, yaml.YAMLError):
        return PriorityRules()

    if not isinstance(data, dict):
        return PriorityRules()

    default_rules = PriorityRules()
    raw_urgency_kw = data.get("urgency_keywords")
    urgency_kw = raw_urgency_kw if isinstance(raw_urgency_kw, dict) else {}

    raw_urgency_pts = data.get("urgency_points")
    urgency_pts = raw_urgency_pts if isinstance(raw_urgency_pts, dict) else {}

    raw_thresholds = data.get("priority_thresholds")
    thresholds = raw_thresholds if isinstance(raw_thresholds, dict) else {}

    return PriorityRules(
        critical_keywords=_normalize_keywords(
            urgency_kw.get("critical"), default_rules.critical_keywords
        ),
        high_keywords=_normalize_keywords(
            urgency_kw.get("high"), default_rules.high_keywords
        ),
        urgency_cap=_non_negative_float(data.get("urgency_cap"), default_rules.urgency_cap),
        aspect_cap=_non_negative_float(data.get("aspect_cap"), default_rules.aspect_cap),
        intensity_bonus=_non_negative_float(
            data.get("intensity_bonus"), default_rules.intensity_bonus
        ),
        critical_last_sentence=_non_negative_float(
            urgency_pts.get("critical_last_sentence"), default_rules.critical_last_sentence
        ),
        critical_other_sentence=_non_negative_float(
            urgency_pts.get("critical_other_sentence"), default_rules.critical_other_sentence
        ),
        high_last_sentence=_non_negative_float(
            urgency_pts.get("high_last_sentence"), default_rules.high_last_sentence
        ),
        high_other_sentence=_non_negative_float(
            urgency_pts.get("high_other_sentence"), default_rules.high_other_sentence
        ),
        threshold_high=_non_negative_float(thresholds.get("high"), default_rules.threshold_high),
        threshold_medium=_non_negative_float(
            thresholds.get("medium"), default_rules.threshold_medium
        ),
    )


# Hằng số mặc định để duy trì backward compatibility cho các module hoặc test import trực tiếp
_DEFAULT_RULES = PriorityRules()
CRITICAL_KEYWORDS = _DEFAULT_RULES.critical_keywords
HIGH_KEYWORDS = _DEFAULT_RULES.high_keywords


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


def _is_negated(sentence: str, kw_index: int, keyword: str = "") -> bool:
    """Kiểm tra từ khóa có bị phủ định trực tiếp ngay phía trước không (≤ 5 ký tự)."""
    if keyword.strip().lower() in REMEDY_ACTION_KEYWORDS:
        return False
    prefix = sentence[:kw_index]
    for neg in NEGATION_PATTERNS:
        for match in re.finditer(neg, prefix, re.IGNORECASE):
            if kw_index - match.end() <= 5:
                return True
    return False


def _is_resolved_clause(clause: str) -> bool:
    """Nhận diện mệnh đề xác nhận vấn đề đã được giải quyết và không mang phủ định."""
    for pattern in RESOLUTION_PATTERNS:
        match = pattern.search(clause)
        if match:
            prefix = clause[: match.start()]
            if not RESOLUTION_NEGATION_RE.search(prefix):
                return True
    return False


def classify_priority_level(score: float, rules: PriorityRules | None = None) -> str:
    """Phân cấp mức ưu tiên dựa trên điểm số và ngưỡng từ PriorityRules."""
    active_rules = rules or load_priority_rules()
    if score >= active_rules.threshold_high:
        return "CRITICAL"
    if score >= active_rules.threshold_medium:
        return "MEDIUM"
    return "LOW"


def _calculate_urgency_bonus(
    text: str,
    active_rules: PriorityRules,
    urgency_cap: float,
    reasons: list[str],
) -> float:
    """Tính điểm thưởng từ khóa khẩn cấp theo vị trí câu và lọc bỏ phủ định/đã giải quyết."""
    sentences = _split_sentences(text)
    total_sentences = len(sentences)
    urgency_bonus = 0.0
    detected_keywords: set[str] = set()

    for i, sent in enumerate(sentences):
        is_last = i == total_sentences - 1
        loc_str = "câu kết" if is_last else f"câu #{i + 1}"
        clauses = [c.strip() for c in CONTRAST_CLAUSE_RE.split(sent) if c.strip()]
        tiers = (
            (
                "CRITICAL",
                active_rules.critical_keywords,
                active_rules.critical_last_sentence
                if is_last
                else active_rules.critical_other_sentence,
            ),
            (
                "HIGH",
                active_rules.high_keywords,
                active_rules.high_last_sentence
                if is_last
                else active_rules.high_other_sentence,
            ),
        )

        for clause in clauses:
            if _is_resolved_clause(clause):
                continue
            for tier_label, keywords, points in tiers:
                for kw in keywords:
                    kw_clean = kw.strip()
                    kw_lower = kw_clean.lower()
                    if not kw_lower or kw_lower in detected_keywords:
                        continue

                    pattern = r"\b" + re.escape(kw_clean) + r"\b"
                    matched = any(
                        not _is_negated(clause, m.start(), keyword=kw_lower)
                        for m in re.finditer(pattern, clause, re.IGNORECASE)
                    )
                    if matched:
                        detected_keywords.add(kw_lower)
                        urgency_bonus += points
                        reasons.append(f"Từ khóa {tier_label} '{kw_clean}' ở {loc_str}: +{points}")

    return min(max(0.0, float(urgency_cap)), round(urgency_bonus, 2))


def calculate_priority(
    result: AbsaResult,
    text: str,
    aspect_weights: dict[str, float] | None = None,
    urgency_cap: float | None = None,
    aspect_cap: float | None = None,
    rules: PriorityRules | None = None,
) -> PriorityBreakdown:
    """Hàm tính toán điểm ưu tiên rule-based toán học minh bạch (Worst-aspect-wins):
    score = min(100.0, base + urgency_bonus + intensity_bonus + aspect_bonus)
    """
    active_rules = rules or load_priority_rules()
    eff_urgency_cap = max(
        0.0, float(urgency_cap if urgency_cap is not None else active_rules.urgency_cap)
    )
    eff_aspect_cap = max(
        0.0, float(aspect_cap if aspect_cap is not None else active_rules.aspect_cap)
    )

    weights = aspect_weights if aspect_weights is not None else load_aspect_weights()
    reasons: list[str] = []

    # 1. Điểm nền cảm xúc tổng thể (Base Score)
    overall = result.overall
    overall_conf = max(0.0, min(1.0, float(overall.confidence)))
    if overall.label == "negative":
        base = round(60.0 * overall_conf, 2)
        reasons.append(f"Cảm xúc tổng thể tiêu cực ({overall_conf:.2f}): base = {base}")
    elif overall.label == "neutral":
        base = 20.0
        reasons.append("Cảm xúc tổng thể trung tính: base = 20.0")
    else:  # positive
        base = 5.0
        reasons.append("Cảm xúc tổng thể tích cực: base = 5.0")

    # 2. Điểm từ khóa khẩn cấp (Urgency Bonus)
    urgency_bonus = _calculate_urgency_bonus(text, active_rules, eff_urgency_cap, reasons)

    # 3. Điểm cường độ câu (Intensity Bonus)
    intensity_res = extract_intensity_bonus(
        text,
        is_negative_overall=(overall.label == "negative"),
        bonus_value=active_rules.intensity_bonus,
    )
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
            key=lambda x: weights.get(x.aspect, 0.5) * max(0.0, min(1.0, float(x.confidence))),
            reverse=True,
        )

        worst = sorted_negs[0]
        dominant_aspect = worst.aspect
        worst_weight = weights.get(worst.aspect, 0.5)
        worst_conf = max(0.0, min(1.0, float(worst.confidence)))
        worst_val = worst_weight * worst_conf * 10.0
        aspect_bonus += worst_val
        reasons.append(
            f"Khía cạnh nghiêm trọng nhất '{worst.aspect}' (trọng số {worst_weight}, conf {worst_conf:.2f}): +{worst_val:.2f}"
        )

        # Phạt dồn các khía cạnh tiêu cực còn lại (25%)
        for other in sorted_negs[1:]:
            other_weight = weights.get(other.aspect, 0.5)
            other_conf = max(0.0, min(1.0, float(other.confidence)))
            other_val = 0.25 * (other_weight * other_conf * 10.0)
            aspect_bonus += other_val
            reasons.append(
                f"Khía cạnh tiêu cực cộng thêm '{other.aspect}' (25% phạt): +{other_val:.2f}"
            )

        aspect_bonus = min(eff_aspect_cap, round(aspect_bonus, 2))
    else:
        # Nếu không có khía cạnh tiêu cực, lấy khía cạnh đầu tiên có trọng số lớn nhất làm dominant
        if result.aspects:
            dominant_aspect = max(result.aspects, key=lambda x: weights.get(x.aspect, 0.5)).aspect

    # Tổng điểm và làm tròn
    total_score = round(min(100.0, base + urgency_bonus + intensity_bonus + aspect_bonus), 2)

    # Phân cấp mức ưu tiên theo ngưỡng cấu hình từ rules
    level = classify_priority_level(total_score, active_rules)

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
