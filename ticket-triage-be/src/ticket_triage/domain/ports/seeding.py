"""Seeding data structures and DIP ports (SeedSourcePort & SeedRepositoryPort)."""

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from ..entities import UserRole


@dataclass(frozen=True)
class SeedUser:
    email: str
    full_name: str
    password: str
    role: UserRole = "customer"


@dataclass(frozen=True)
class SeedCategory:
    slug: str
    name: str
    description: str
    icon: str


@dataclass(frozen=True)
class SeedProduct:
    category_slug: str
    slug: str
    name: str
    short_description: str
    description: str
    price: float
    image_url: str
    sku: str
    stock: int = 25


@dataclass(frozen=True)
class SeedReview:
    product_slug: str
    author_email: str
    content: str
    title: str | None = None
    source_domain: str = "mabsa"
    source_language: str = "en"


@dataclass(frozen=True)
class SeedBundle:
    users: tuple[SeedUser, ...] = field(default_factory=tuple)
    categories: tuple[SeedCategory, ...] = field(default_factory=tuple)
    products: tuple[SeedProduct, ...] = field(default_factory=tuple)
    reviews: tuple[SeedReview, ...] = field(default_factory=tuple)


@runtime_checkable
class SeedSourcePort(Protocol):
    """Abstract source of storefront seed data (JSON fixture vs raw M-ABSA directory)."""

    def load(self) -> SeedBundle:
        ...


@runtime_checkable
class SeedRepositoryPort(Protocol):
    """Idempotent persistence operations required by SeedService."""

    def count_products(self) -> int:
        ...

    def ensure_user(
        self,
        *,
        email: str,
        full_name: str,
        password_hash: str,
        role: UserRole,
    ) -> tuple[int, bool]:
        """Return (user_id, created)."""
        ...

    def ensure_category(
        self,
        *,
        slug: str,
        name: str,
        description: str,
        icon: str,
    ) -> tuple[int, bool]:
        """Return (category_id, created)."""
        ...

    def ensure_product(
        self,
        *,
        category_id: int,
        slug: str,
        name: str,
        short_description: str,
        description: str,
        price: float,
        image_url: str,
        sku: str,
        stock: int,
    ) -> tuple[int, bool]:
        """Return (product_id, created)."""
        ...

    def review_exists(self, product_slug: str, content: str) -> bool:
        ...
