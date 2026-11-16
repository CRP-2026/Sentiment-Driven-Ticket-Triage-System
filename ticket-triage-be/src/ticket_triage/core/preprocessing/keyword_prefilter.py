import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from ..config_utils import find_config_file as _find_config_file


def _normalize_keyword_list(raw_keywords: list[Any]) -> list[str]:
    seen: set[str] = set()
    normalized: list[str] = []
    for kw in raw_keywords:
        if kw is None:
            continue
        cleaned = str(kw).strip().lower()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            normalized.append(cleaned)
    return normalized


@lru_cache(maxsize=4)
def load_aspect_keywords(yaml_path: Path | str | None = None) -> dict[str, list[str]]:
    """Nạp danh mục từ khóa lọc khía cạnh từ configs/aspects.yaml (bắt buộc, fail-fast)."""
    target_path = Path(yaml_path) if yaml_path is not None else _find_config_file("aspects.yaml")
    if target_path is None or not target_path.is_file():
        raise FileNotFoundError(
            f"Aspects config not found at: {target_path or 'configs/aspects.yaml'}"
        )

    with open(target_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict) or not isinstance(data.get("aspects"), list):
        raise TypeError(f"Invalid aspects config format in: {target_path}")

    loaded: dict[str, list[str]] = {}
    for item in data["aspects"]:
        if not isinstance(item, dict):
            raise TypeError(f"Invalid aspect entry in: {target_path}")

        raw_id = item.get("id")
        aspect_id = str(raw_id).strip() if raw_id is not None else ""
        if not aspect_id:
            raise ValueError(f"Aspect entry missing 'id' in: {target_path}")
        if aspect_id in loaded:
            raise ValueError(f"Duplicate aspect ID detected: {aspect_id}")

        raw_keywords = item.get("keywords")
        if raw_keywords is None:
            loaded[aspect_id] = []
        elif not isinstance(raw_keywords, list):
            raise TypeError(
                f"Invalid 'keywords' list for aspect '{aspect_id}' in: {target_path}"
            )
        else:
            loaded[aspect_id] = _normalize_keyword_list(raw_keywords)

    if not loaded:
        raise ValueError(f"No aspects defined in: {target_path}")

    return loaded


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
            pattern = r"\b" + re.escape(kw) + r"\b"
            if re.search(pattern, text_lower):
                matched_aspects.append(aspect_id)
                break

    if not matched_aspects:
        return ["general"]

    return matched_aspects