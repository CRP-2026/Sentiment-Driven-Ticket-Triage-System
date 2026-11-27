"""Media storage abstraction port (Cloudinary / Local fallback)."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ImageStoragePort(Protocol):
    def upload_image(
        self,
        content: bytes,
        filename: str,
        folder: str = "products",
    ) -> str:
        """Upload raw image bytes and return a public URL or resolvable reference."""
        ...

    def resolve_url(self, image_ref: str) -> str:
        """Normalize a stored image reference into a browser-ready URL."""
        ...
