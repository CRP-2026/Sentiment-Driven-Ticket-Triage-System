from .cloudinary_storage import CloudinaryImageStorage
from .local_storage import LocalFallbackImageStorage

__all__ = ["CloudinaryImageStorage", "LocalFallbackImageStorage"]
