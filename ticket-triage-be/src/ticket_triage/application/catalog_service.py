"""Storefront catalog & Amazon-style ABSA insights use-case service."""

from dataclasses import replace

from ..core.taxonomy import Taxonomy
from ..domain.entities import (
    CategoryEntity,
    ProductCatalogItem,
    ProductDetailResult,
)
from ..domain.exceptions import EntityNotFoundError
from ..domain.ports.repositories import CatalogRepositoryPort, ReviewRepositoryPort
from ..domain.ports.storage import ImageStoragePort
from .aspect_insights import build_product_insights


class CatalogService:
    """Serves categories, product listings, and product details enriched with AI ABSA insights."""

    def __init__(
        self,
        catalog_repo: CatalogRepositoryPort,
        review_repo: ReviewRepositoryPort,
        image_storage: ImageStoragePort,
        taxonomy: Taxonomy | None = None,
    ) -> None:
        self._catalog_repo = catalog_repo
        self._review_repo = review_repo
        self._image_storage = image_storage
        self._taxonomy = taxonomy

    def list_categories(self) -> list[CategoryEntity]:
        return self._catalog_repo.list_categories()

    def list_products(
        self,
        category_slug: str | None = None,
        search: str | None = None,
        limit: int = 24,
        offset: int = 0,
    ) -> tuple[list[ProductCatalogItem], int]:
        products, total = self._catalog_repo.list_products(
            category_slug=category_slug,
            search=search,
            limit=limit,
            offset=offset,
        )
        if not products:
            return [], total

        product_ids = [p.id for p in products]
        sentiment_map = self._catalog_repo.get_bulk_product_sentiment_counts(product_ids)
        aspect_map = self._catalog_repo.get_bulk_product_aspect_observations(product_ids)

        catalog_items: list[ProductCatalogItem] = []
        for product in products:
            resolved_product = replace(
                product,
                image_url=self._image_storage.resolve_url(product.image_url),
            )
            insights = build_product_insights(
                sentiment_counts=sentiment_map.get(product.id, {}),
                aspect_observations=aspect_map.get(product.id, []),
                taxonomy=self._taxonomy,
                top_n=3,
            )
            catalog_items.append(
                ProductCatalogItem(
                    product=resolved_product,
                    total_reviews=insights.total_reviews,
                    satisfaction_rate=insights.satisfaction_rate,
                    top_ranked_aspects=insights.top_ranked_aspects,
                )
            )

        return catalog_items, total

    def get_product_detail(
        self,
        slug: str,
        aspect: str | None = None,
        review_limit: int = 50,
        review_offset: int = 0,
    ) -> ProductDetailResult:
        product = self._catalog_repo.get_product_by_slug(slug)
        if product is None:
            raise EntityNotFoundError(f"Không tìm thấy sản phẩm '{slug}'.")

        resolved_product = replace(
            product,
            image_url=self._image_storage.resolve_url(product.image_url),
        )
        sentiment_counts = self._catalog_repo.get_product_sentiment_counts(product.id)
        aspect_observations = self._catalog_repo.get_product_aspect_observations(product.id)
        insights = build_product_insights(
            sentiment_counts=sentiment_counts,
            aspect_observations=aspect_observations,
            taxonomy=self._taxonomy,
            top_n=3,
        )
        reviews, total_filtered = self._review_repo.list_by_product(
            product_id=product.id,
            aspect=aspect,
            limit=review_limit,
            offset=review_offset,
        )

        return ProductDetailResult(
            product=resolved_product,
            insights=insights,
            reviews=reviews,
            total_filtered_reviews=total_filtered,
        )
