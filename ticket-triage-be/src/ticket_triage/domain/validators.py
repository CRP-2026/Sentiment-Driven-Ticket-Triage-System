"""Shared pure domain text validators (Single Source of Truth for Application & API)."""

import re

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WORD_CHAR_RE = re.compile(r"\w")


def validate_text_content(
    value: str,
    field_label: str = "Nội dung",
    min_len: int = 3,
    max_len: int = 5000,
) -> str:
    """Validate customer text against empty/whitespace, HTML-only spam, and DoS length."""
    if not isinstance(value, str):
        raise TypeError(f"{field_label} phải là chuỗi văn bản.")
    cleaned = value.strip()
    if len(cleaned) < min_len:
        raise ValueError(
            f"{field_label} quá ngắn (tối thiểu {min_len} ký tự không phải khoảng trắng)."
        )
    if len(cleaned) > max_len:
        raise ValueError(
            f"{field_label} vượt quá giới hạn tối đa cho phép ({max_len} ký tự)."
        )

    without_html = _HTML_TAG_RE.sub("", cleaned).strip()
    if not without_html or not _WORD_CHAR_RE.search(without_html):
        raise ValueError(
            f"{field_label} không hợp lệ (chỉ chứa thẻ HTML rỗng hoặc ký tự đặc biệt)."
        )
    return cleaned
