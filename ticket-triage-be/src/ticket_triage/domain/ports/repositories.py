"""Persistence repository ports (DIP) independent of SQLAlchemy/SQLite/PostgreSQL."""

from typing import Any, Protocol, runtime_checkable

from ..entities import (
    AspectObservation,
    CategoryEntity,
    ProductEntity,
    ReviewEntity,
    UserEntity,
    UserRole,
)


@runtime_checkable
class UserRepositoryPort(Protocol):
    def get_by_email(self, email: str) -> UserEntity | None:
        ...

    def get_by_id(self, user_id: int) -> UserEntity | None:
        ...

    def create(
        self,
        email: str,
        full_name: str,
        password_hash: str,
        role: UserRole = "customer",
    ) -> UserEntity:
        ...


@runtime_checkable
class CatalogRepositoryPort(Protocol):
    def list_categories(self) -> list[CategoryEntity]:
        ...

    def list_products(
        self,
        category_slug: str | None = None,
        search: str | None = None,
        limit: int = 24,
        offset: int = 0,
    ) -> tuple[list[ProductEntity], int]:
        ...

    def get_product_by_slug(self, slug: str) -> ProductEntity | None:
        ...

    def get_product_by_id(self, product_id: int) -> ProductEntity | None:
        ...

    def get_product_sentiment_counts(self, product_id: int) -> dict[str, int]:
        ...

    def get_product_aspect_observations(self, product_id: int) -> list[AspectObservation]:
        ...

    def get_bulk_product_sentiment_counts(
        self, product_ids: list[int]
    ) -> dict[int, dict[str, int]]:
        ...

    def get_bulk_product_aspect_observations(
        self, product_ids: list[int]
    ) -> dict[int, list[AspectObservation]]:
        ...


@runtime_checkable
class ReviewRepositoryPort(Protocol):
    def list_by_product(
        self,
        product_id: int,
        aspect: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[ReviewEntity], int]:
        ...

    def create(
        self,
        product_id: int,
        user_id: int,
        ticket_id: int,
        content: str,
        title: str | None = None,
        *,
        sentiment_label: str | None = None,
        confidence: float | None = None,
        priority_score: float = 0.0,
        priority_level: str = "LOW",
        needs_manual_review: bool = False,
        aspects: tuple[AspectObservation, ...] = (),
    ) -> ReviewEntity:
        ...


@runtime_checkable
class TicketRepositoryPort(Protocol):
    def create_ticket(
        self,
        *,
        content: str,
        processed_content: str | None = None,
        language_flag: str = "en",
        needs_manual_review: bool = False,
        sentiment_label: str | None = None,
        confidence: float | None = None,
        low_confidence: bool = False,
        priority_score: float = 0.0,
        priority_level: str = "LOW",
        priority_breakdown: dict[str, Any] | None = None,
        dominant_aspect: str | None = None,
        status: str = "new",
        assigned_to: str | None = None,
        source: str = "direct_api",
        product_id: int | None = None,
        product_name: str | None = None,
        product_slug: str | None = None,
        user_id: int | None = None,
        author_name: str | None = None,
        aspects_data: list[dict[str, Any]] | None = None,
    ) -> Any:
        ...

    def get_by_id(self, ticket_id: int) -> Any | None:
        ...

    def get_tickets(
        self,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
        aspect: str | None = None,
        sentiment: str | None = None,
    ) -> tuple[list[Any], int]:
        ...

    def get_unresolved_tickets(self) -> list[Any]:
        ...

    def update_status(
        self,
        ticket_id: int,
        new_status: str,
        assigned_to: str | None = None,
    ) -> Any | None:
        ...

    def get_stats_overview(self) -> dict[str, Any]:
        ...

    def get_aspect_matrix(self) -> list[tuple[str, str, int]]:
        ...
