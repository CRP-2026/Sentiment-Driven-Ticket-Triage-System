from dataclasses import dataclass, field

from .keyword_prefilter import filter_candidate_aspects
from .lang_validator import validate_english
from .normalizer import clean_text


@dataclass(frozen=True)
class PreprocessedTicket:
    raw_text: str
    clean_text: str
    is_english: bool
    detected_lang: str
    lang_confidence: float
    needs_manual_review: bool
    candidate_aspects: list[str] = field(default_factory=list)

def preprocess_ticket(raw_text: str) -> PreprocessedTicket:
    """Chuỗi tiền xử lý tích hợp:
    1. Làm sạch văn bản (clean_text)
    2. Xác thực ngôn ngữ tiếng Anh (validate_english)
    3. Lọc trước ứng viên khía cạnh (filter_candidate_aspects)
    """
    cleaned = clean_text(raw_text)
    lang_res = validate_english(cleaned)

    if lang_res.is_english:
        candidates = filter_candidate_aspects(cleaned)
    else:
        candidates = []

    return PreprocessedTicket(
        raw_text=raw_text,
        clean_text=cleaned,
        is_english=lang_res.is_english,
        detected_lang=lang_res.detected_lang,
        lang_confidence=lang_res.confidence,
        needs_manual_review=lang_res.needs_manual_review,
        candidate_aspects=candidates,
    )
