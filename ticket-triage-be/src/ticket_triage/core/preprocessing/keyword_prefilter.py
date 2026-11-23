import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from ..config_utils import find_config_file as _find_config_file

DEFAULT_ASPECT_KEYWORDS: dict[str, list[str]] = {
    "customer_service": [
        "agent", "representative", "support", "service", "rep", "staff",
        "attitude", "rude", "unhelpful", "reply", "response", "ticket",
        "chat", "call", "contact", "email", "manager", "assistance",
        "hung up", "hang up", "ignored", "supervisor", "disrespect", "disrespectful",
    ],
    "refund_payment": [
        "refund", "charge", "charged", "overcharged", "double charged", "charged twice",
        "payment", "pay", "paid", "bill", "billed", "billing", "invoice", "fee", "money back",
        "dispute", "chargeback", "credit card", "bank", "transaction", "reimburse",
        "unauthorized charge", "extra charge",
    ],
    "product_quality": [
        "broken", "damaged", "defect", "defective", "cheap", "poor quality",
        "quality", "fake", "counterfeit", "faulty", "flaw", "torn", "rip",
        "stopped working", "not working", "durability", "material", "smell",
        "zipper", "button", "size", "fit", "color",
    ],
    "shipping": [
        "ship", "shipping", "deliver", "delivery", "delivered", "package",
        "parcel", "box", "tracking", "track", "transit", "carrier", "courier",
        "usps", "fedex", "ups", "late", "delay", "delayed", "never arrived",
        "never received", "lost package", "wrong address", "customs",
    ],
    "general": [
        "account", "login", "password", "website", "app", "policy", "faq",
        "question", "inquiry", "how to", "terms", "subscribe", "cancel account",
    ],
}

# Alias giữ tương thích ngược cho các module hoặc test import trực tiếp
ASPECT_KEYWORDS = DEFAULT_ASPECT_KEYWORDS


def _normalize_keyword_list(raw_keywords: Any) -> list[str]:
    if not isinstance(raw_keywords, list):
        return []
    seen: set[str] = set()
    normalized: list[str] = []
    for kw in raw_keywords:
        cleaned = str(kw).strip().lower()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            normalized.append(cleaned)
    return normalized


@lru_cache(maxsize=4)
def load_aspect_keywords(yaml_path: Path | str | None = None) -> dict[str, list[str]]:
    """Nạp danh mục từ khóa lọc khía cạnh từ configs/aspects.yaml (fallback an toàn về mặc định)."""
    fallback = {k: list(v) for k, v in DEFAULT_ASPECT_KEYWORDS.items()}
    target_path = Path(yaml_path) if yaml_path is not None else _find_config_file("aspects.yaml")
    if target_path is None or not target_path.is_file():
        return fallback

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except (OSError, yaml.YAMLError):
        return fallback

    if not isinstance(data, dict) or not isinstance(data.get("aspects"), list):
        return fallback

    loaded: dict[str, list[str]] = {}
    has_yaml_keywords = False
    for item in data["aspects"]:
        if not isinstance(item, dict):
            continue
        aspect_id = str(item.get("id", "")).strip()
        if not aspect_id:
            continue
        if "keywords" in item:
            kw_list = _normalize_keyword_list(item.get("keywords"))
            loaded[aspect_id] = kw_list
            if kw_list:
                has_yaml_keywords = True
        else:
            loaded[aspect_id] = list(DEFAULT_ASPECT_KEYWORDS.get(aspect_id, []))

    return loaded if has_yaml_keywords else fallback


def _build_aspect_keyword_pattern(kw: str) -> str:
    """Xây dựng biểu thức chính quy khớp từ khóa khía cạnh:
    - Hỗ trợ tiền tố 'regex:' nếu khai báo mẫu động trong YAML.
    - Tự động cho phép các biến thể hậu tố tiếng Anh phổ biến (-s, -es, -d, -ed, -ing)
      ở từ cuối để không bỏ sót biến thể từ vựng (vd: 'bill' -> 'billed', 'bills', 'billing').
    """
    if kw.startswith("regex:"):
        return kw[6:].strip()
    escaped = re.escape(kw)
    if re.search(r"[a-z]{3,}$", kw):
        return rf"\b{escaped}(?:s|es|d|ed|ing)?\b"
    return rf"\b{escaped}\b"


def filter_candidate_aspects(
    text: str,
    aspect_keywords: dict[str, list[str]] | None = None,
) -> list[str]:
    """Quét tín hiệu từ khóa khía cạnh trước khi chạy NLI:
    - Trả về danh sách aspect IDs có từ khóa xuất hiện.
    - Nếu không phát hiện từ khóa cụ thể nào, mặc định trả về ['general'].
    """
    if not text:
        return ["general"]

    keywords_by_aspect = (
        aspect_keywords if aspect_keywords is not None else load_aspect_keywords()
    )
    text_lower = text.lower()
    matched_aspects: list[str] = []

    for aspect_id, keywords in keywords_by_aspect.items():
        if aspect_id == "general":
            continue

        for kw in keywords:
            pattern = _build_aspect_keyword_pattern(kw)
            if re.search(pattern, text_lower):
                matched_aspects.append(aspect_id)
                break

    if not matched_aspects:
        return ["general"]

    return matched_aspects
