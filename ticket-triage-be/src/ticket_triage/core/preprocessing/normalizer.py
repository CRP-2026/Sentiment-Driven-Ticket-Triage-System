import re
import unicodedata

HTML_TAG_RE = re.compile(r"<[^>]+>")
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
REPEATED_LETTERS_RE = re.compile(r"([a-zA-Z])\1{2,}")
REPEATED_PUNCT_RE = re.compile(r"([!?])\1{3,}")

def clean_text(raw_text: str) -> str:
    """Chuẩn hóa văn bản tiếng Anh:
    - Chuẩn hóa Unicode NFC
    - Loại bỏ HTML, URLs, Email
    - Rút gọn ký tự lặp quá mức (soooo -> so)
    - Rút gọn chuỗi dấu câu quá dài (!!!!! -> !!!)
    - Giữ nguyên chữ hoa (CAPS) và dấu chấm than/hỏi để phục vụ tính Intensity.
    """
    if not raw_text or not raw_text.strip():
        return ""

    # 1. Unicode NFC
    text = unicodedata.normalize("NFC", raw_text)

    # 2. Loại bỏ HTML, URLs, Email
    text = HTML_TAG_RE.sub(" ", text)
    text = URL_RE.sub(" ", text)
    text = EMAIL_RE.sub(" ", text)

    # 3. Rút gọn ký tự chữ cái lặp quá 2 lần (ví dụ: pleeeease -> please, baaaad -> bad)
    text = REPEATED_LETTERS_RE.sub(r"\1", text)

    # 4. Rút gọn dấu câu lặp quá mức (ví dụ: !!!!!!! -> !!!)
    text = REPEATED_PUNCT_RE.sub(r"\1\1\1", text)

    # 5. Chuẩn hóa khoảng trắng
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()
