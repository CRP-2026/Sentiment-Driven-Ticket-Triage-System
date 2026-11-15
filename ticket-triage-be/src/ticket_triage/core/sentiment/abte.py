import re

from ..preprocessing.keyword_prefilter import load_aspect_keywords


def extract_aspect_terms(
    text: str,
    aspect: str,
    aspect_keywords: dict[str, list[str]] | None = None,
) -> tuple[str, ...]:
    """Trích xuất cụm từ biểu đạt khía cạnh (ABTE - Could Have).
    Chỉ kích hoạt khi ENABLE_ABTE=true; trả về các cụm từ khớp theo thứ tự xuất hiện.
    """
    if not text or not aspect:
        return ()

    keywords_by_aspect = (
        aspect_keywords if aspect_keywords is not None else load_aspect_keywords()
    )
    keywords = keywords_by_aspect.get(aspect, [])
    if not keywords:
        return ()

    # Ưu tiên cụm từ dài trước để tránh match đè cụm con (vd: "never received" trước "received")
    sorted_keywords = sorted(
        {kw.strip() for kw in keywords if kw.strip()},
        key=len,
        reverse=True,
    )
    if not sorted_keywords:
        return ()

    pattern = re.compile(
        r"\b(?:" + "|".join(re.escape(kw) for kw in sorted_keywords) + r")\b",
        re.IGNORECASE,
    )
    seen: set[str] = set()
    extracted: list[str] = []
    for match in pattern.finditer(text):
        phrase = match.group(0)
        key = phrase.lower()
        if key not in seen:
            seen.add(key)
            extracted.append(phrase)

    return tuple(extracted)
