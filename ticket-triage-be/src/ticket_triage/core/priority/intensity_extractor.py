import re
from dataclasses import dataclass

CAPS_WORD_RE = re.compile(r"\b[A-Z]{6,}\b")
EXCLAMATION_RE = re.compile(r"!{3,}")
QUESTION_RE = re.compile(r"\?{2,}")

@dataclass(frozen=True)
class IntensityAnalysis:
    has_exclamation: bool
    has_caps: bool
    has_question_marks: bool
    bonus: float
    reason: str | None

def extract_intensity_bonus(text: str, is_negative_overall: bool) -> IntensityAnalysis:
    """Trích xuất cường độ cảm xúc từ cú pháp câu tiếng Anh:
    - +5 điểm nếu có chuỗi '!!!' hoặc từ viết hoa (CAPS LOCK, len > 5)
      VÀ cảm xúc tổng thể là negative.
    """
    if not text:
        return IntensityAnalysis(False, False, False, 0.0, None)

    has_excl = bool(EXCLAMATION_RE.search(text))
    has_caps = bool(CAPS_WORD_RE.search(text))
    has_q = bool(QUESTION_RE.search(text))

    triggers = []
    if has_excl:
        triggers.append("dấu cảm thán liên tiếp '!!!'")
    if has_caps:
        triggers.append("từ viết hoa toàn bộ (CAPS LOCK)")

    bonus = 0.0
    reason = None

    if triggers and is_negative_overall:
        bonus = 5.0
        reason = f"Cú pháp câu thể hiện bức xúc ({', '.join(triggers)}): +5.0"

    return IntensityAnalysis(
        has_exclamation=has_excl,
        has_caps=has_caps,
        has_question_marks=has_q,
        bonus=bonus,
        reason=reason,
    )
