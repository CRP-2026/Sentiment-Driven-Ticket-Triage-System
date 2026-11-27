"""SQLAlchemy implementation of SeedRepositoryPort for idempotent demo seeding."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ...db.models import Category, Product, ProductReview, User
from ...domain.entities import UserRole


class SqlAlchemySeedRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def count_products(self) -> int:
        return int(self._db.scalar(select(func.count(Product.id))) or 0)

    def ensure_user(
        self,
        *,
        email: str,
        full_name: str,
        password_hash: str,
        role: UserRole,
    ) -> tuple[int, bool]:
        normalized = email.strip().lower()
        existing = self._db.scalar(select(User).where(func.lower(User.email) == normalized))
        if existing is not None:
            return existing.id, False

        user = User(
            email=normalized,
            full_name=full_name.strip(),
            password_hash=password_hash,
            role=role,
            is_active=True,
        )
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user.id, True

    def ensure_category(
        self,
        *,
        slug: str,
        name: str,
        description: str,
        icon: str,
    ) -> tuple[int, bool]:
        normalized = slug.strip().lower()
        existing = self._db.scalar(select(Category).where(Category.slug == normalized))
        if existing is not None:
            return existing.id, False

        category = Category(
            slug=normalized,
            name=name.strip(),
            description=description.strip(),
            icon=icon.strip(),
        )
        self._db.add(category)
        self._db.commit()
        self._db.refresh(category)
        return category.id, True

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
        normalized = slug.strip().lower()
        existing = self._db.scalar(select(Product).where(Product.slug == normalized))
        if existing is not None:
            return existing.id, False

        product = Product(
            category_id=category_id,
            slug=normalized,
            name=name.strip(),
            short_description=short_description.strip(),
            description=description.strip(),
            price=float(price),
            image_url=image_url.strip(),
            sku=sku.strip(),
            stock=int(stock),
        )
        self._db.add(product)
        self._db.commit()
        self._db.refresh(product)
        return product.id, True

    def review_exists(self, product_slug: str, content: str) -> bool:
        stmt = (
            select(func.count(ProductReview.id))
            .join(Product, Product.id == ProductReview.product_id)
            .where(
                Product.slug == product_slug.strip().lower(),
                ProductReview.content == content.strip(),
            )
        )
        return int(self._db.scalar(stmt) or 0) > 0
