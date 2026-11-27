"""Cloudinary REST API implementation of ImageStoragePort (zero SDK overhead)."""

import hashlib
import time
from typing import Any

import httpx

from ...domain.exceptions import DomainError, ValidationDomainError


class CloudinaryImageStorage:
    """Uploads images directly to Cloudinary via signed REST calls and optimizes delivery URLs."""

    def __init__(
        self,
        cloud_name: str,
        api_key: str,
        api_secret: str,
        default_folder: str = "ticket-triage/products",
        http_client: httpx.Client | None = None,
        timeout_seconds: float = 20.0,
    ) -> None:
        self._cloud_name = cloud_name.strip()
        self._api_key = api_key.strip()
        self._api_secret = api_secret.strip()
        self._default_folder = default_folder.strip("/")
        self._http_client = http_client
        self._timeout = timeout_seconds

    def _sign_params(self, params: dict[str, str]) -> str:
        canonical = "&".join(f"{k}={params[k]}" for k in sorted(params) if params[k])
        return hashlib.sha1(f"{canonical}{self._api_secret}".encode()).hexdigest()

    def upload_image(
        self,
        content: bytes,
        filename: str,
        folder: str = "products",
    ) -> str:
        if not content:
            raise ValidationDomainError("Tệp hình ảnh tải lên không được để trống.")

        timestamp = str(int(time.time()))
        target_folder = folder.strip("/") or self._default_folder
        signed_fields = {"folder": target_folder, "timestamp": timestamp}
        signature = self._sign_params(signed_fields)

        endpoint = f"https://api.cloudinary.com/v1_1/{self._cloud_name}/image/upload"
        form_data = {
            "api_key": self._api_key,
            "timestamp": timestamp,
            "folder": target_folder,
            "signature": signature,
        }
        files = {"file": (filename or "upload.png", content)}

        try:
            if self._http_client is not None:
                response = self._http_client.post(endpoint, data=form_data, files=files)
            else:
                with httpx.Client(timeout=self._timeout) as client:
                    response = client.post(endpoint, data=form_data, files=files)
        except httpx.HTTPError as exc:
            raise DomainError(f"Không thể kết nối tới Cloudinary: {exc}") from exc

        if response.status_code >= 400:
            raise DomainError(
                f"Không thể tải ảnh lên Cloudinary (HTTP {response.status_code})."
            )

        body: dict[str, Any] = response.json()
        secure_url = str(body.get("secure_url") or body.get("url") or "").strip()
        if not secure_url:
            raise ValidationDomainError("Cloudinary không trả về đường dẫn ảnh hợp lệ.")
        return self.resolve_url(secure_url)

    def resolve_url(self, image_ref: str) -> str:
        cleaned = (image_ref or "").strip()
        if not cleaned:
            return ""
        # Inject Cloudinary auto-format & auto-quality optimization for standard delivery URLs
        if "res.cloudinary.com" in cleaned and "/image/upload/" in cleaned:
            if "/image/upload/f_auto,q_auto/" not in cleaned:
                return cleaned.replace("/image/upload/", "/image/upload/f_auto,q_auto/", 1)
            return cleaned
        if cleaned.startswith(("http://", "https://", "/")):
            return cleaned
        return (
            f"https://res.cloudinary.com/{self._cloud_name}/image/upload/"
            f"f_auto,q_auto/{cleaned.lstrip('/')}"
        )
