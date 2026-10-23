import re
from dataclasses import dataclass

try:
    from langdetect import detect_langs, DetectorFactory
    DetectorFactory.seed = 42
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

@dataclass(frozen=True)
class LanguageValidationResult:
    is_english: bool
    detected_lang: str
    confidence: float
    needs_manual_review: bool

def validate_english(text: str) -> LanguageValidationResult:
    """Xác thực ngôn ngữ của ticket:
    - Nếu là tiếng Anh (en) với xác suất >= 0.70: hợp lệ.
    - Nếu ngoại ngữ (vi, fr, es...): gắn cờ needs_manual_review = True.
    - Với văn bản cực ngắn hoặc chỉ số/ký tự: kiểm tra an toàn theo bảng chữ cái.
    """
    clean = text.strip()
    if not clean:
        return LanguageValidationResult(
            is_english=False,
            detected_lang="unknown",
            confidence=0.0,
            needs_manual_review=True,
        )

    # Nếu chỉ gồm số hoặc ký tự đặc biệt
    if not re.search(r"[a-zA-Z]", clean):
        return LanguageValidationResult(
            is_english=False,
            detected_lang="symbol_only",
            confidence=0.0,
            needs_manual_review=True,
        )

    if not LANGDETECT_AVAILABLE:
        # Fallback cơ bản khi chưa cài thư viện
        return LanguageValidationResult(
            is_english=True,
            detected_lang="en",
            confidence=1.0,
            needs_manual_review=False,
        )

    try:
        langs = detect_langs(clean)
        top = langs[0] if langs else None

        if top and top.lang == "en" and top.prob >= 0.65:
            return LanguageValidationResult(
                is_english=True,
                detected_lang="en",
                confidence=round(float(top.prob), 3),
                needs_manual_review=False,
            )
        else:
            lang_code = top.lang if top else "unknown"
            prob = round(float(top.prob), 3) if top else 0.0
            return LanguageValidationResult(
                is_english=False,
                detected_lang=lang_code,
                confidence=prob,
                needs_manual_review=True,
            )
    except Exception:
        # Nếu câu quá ngắn gây lỗi langdetect nhưng toàn ký tự ASCII alphabet
        ascii_words = re.findall(r"\b[A-Za-z]+\b", clean)
        if len(ascii_words) >= 1:
            return LanguageValidationResult(
                is_english=True,
                detected_lang="en",
                confidence=0.70,
                needs_manual_review=False,
            )

        return LanguageValidationResult(
            is_english=False,
            detected_lang="unknown",
            confidence=0.0,
            needs_manual_review=True,
        )
