"""Offline-safe local fallback implementation of ImageStoragePort."""

import re
import uuid
from pathlib import Path

_SAFE_NAME_RE = re.compile(r"[^a-zA-Z0-9._-]+")
_SAFE_SEGMENT_RE = re.compile(r"[^a-zA-Z0-9_-]+")


def _sanitize_folder(folder: str) -> str:
    parts = [
        _SAFE_SEGMENT_RE.sub("_", seg)
        for seg in folder.replace("\\", "/").split("/")
        if seg and seg not in (".", "..")
    ]
    return "/".join(parts) or "products"


class LocalFallbackImageStorage:
    """Fallback image storage when Cloudinary credentials are not configured."""

    def __init__(self, upload_dir: Path | None = None, public_prefix: str = "/images") -> None:
        self._upload_dir = upload_dir
        self._public_prefix = public_prefix.rstrip("/")

    def upload_image(
        self,
        content: bytes,
        filename: str,
        folder: str = "products",
    ) -> str:
        safe_name = _SAFE_NAME_RE.sub("_", Path(filename or "image.png").name)
        unique_name = f"{uuid.uuid4().hex[:10]}_{safe_name}"
        clean_folder = _sanitize_folder(folder)

        if self._upload_dir is not None:
            target_dir = (self._upload_dir / clean_folder).resolve()
            root_dir = self._upload_dir.resolve()
            if root_dir in target_dir.parents or target_dir == root_dir:
                target_dir.mkdir(parents=True, exist_ok=True)
                (target_dir / unique_name).write_bytes(content)

        return f"{self._public_prefix}/{clean_folder}/{unique_name}"

    def resolve_url(self, image_ref: str) -> str:
        cleaned = (image_ref or "").strip()
        if not cleaned:
            return f"{self._public_prefix}/products/default.svg"
        if cleaned.startswith(("http://", "https://", "/")):
            return cleaned
        return f"{self._public_prefix}/{cleaned.lstrip('/')}"
