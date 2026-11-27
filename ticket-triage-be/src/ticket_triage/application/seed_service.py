"""Idempotent storefront & triage seeding use case obeying SOLID-D ports."""

from dataclasses import dataclass

from ..domain.ports.repositories import UserRepositoryPort
from ..domain.ports.security import PasswordHasherPort
from ..domain.ports.seeding import SeedRepositoryPort, SeedSourcePort
from .review_service import ReviewService


@dataclass(frozen=True)
class SeedSummary:
    users_created: int
    categories_created: int
    products_created: int
    reviews_created: int
    reviews_skipped: int


class SeedService:
    """Seeds users, categories, products, and real M-ABSA reviews idempotently.

    Every seeded review flows through ReviewService -> TriageGatewayPort so Amazon-style
    Top 1-2-3 aspect insights and Admin Triage priorities are computed by the real pipeline.
    """

    def __init__(
        self,
        seed_source: SeedSourcePort,
        seed_repo: SeedRepositoryPort,
        user_repo: UserRepositoryPort,
        password_hasher: PasswordHasherPort,
        review_service: ReviewService,
    ) -> None:
        self._seed_source = seed_source
        self._seed_repo = seed_repo
        self._user_repo = user_repo
        self._password_hasher = password_hasher
        self._review_service = review_service

    def run(self, only_if_empty: bool = False) -> SeedSummary:
        if only_if_empty and self._seed_repo.count_products() > 0:
            return SeedSummary(0, 0, 0, 0, 0)

        bundle = self._seed_source.load()

        users_created = 0
        for u in bundle.users:
            _, created = self._seed_repo.ensure_user(
                email=u.email,
                full_name=u.full_name,
                password_hash=self._password_hasher.hash_password(u.password),
                role=u.role,
            )
            if created:
                users_created += 1

        categories_created = 0
        cat_ids: dict[str, int] = {}
        for c in bundle.categories:
            cat_id, created = self._seed_repo.ensure_category(
                slug=c.slug,
                name=c.name,
                description=c.description,
                icon=c.icon,
            )
            cat_ids[c.slug] = cat_id
            if created:
                categories_created += 1

        products_created = 0
        for p in bundle.products:
            cat_id = cat_ids.get(p.category_slug)
            if cat_id is None:
                continue
            _, created = self._seed_repo.ensure_product(
                category_id=cat_id,
                slug=p.slug,
                name=p.name,
                short_description=p.short_description,
                description=p.description,
                price=p.price,
                image_url=p.image_url,
                sku=p.sku,
                stock=p.stock,
            )
            if created:
                products_created += 1

        reviews_created = 0
        reviews_skipped = 0
        user_cache = {}
        for rev in bundle.reviews:
            if self._seed_repo.review_exists(rev.product_slug, rev.content):
                reviews_skipped += 1
                continue

            author = user_cache.get(rev.author_email)
            if author is None:
                author = self._user_repo.get_by_email(rev.author_email)
                if author is not None:
                    user_cache[rev.author_email] = author
            if author is None:
                reviews_skipped += 1
                continue

            self._review_service.submit_review(
                user=author,
                product_slug=rev.product_slug,
                content=rev.content,
                title=rev.title,
            )
            reviews_created += 1

        return SeedSummary(
            users_created=users_created,
            categories_created=categories_created,
            products_created=products_created,
            reviews_created=reviews_created,
            reviews_skipped=reviews_skipped,
        )
