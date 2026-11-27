"""SQLAlchemy 2.0 concrete repositories implementing Domain Repository Ports."""

from collections import defaultdict
from typing import Any

from sqlalchemy import desc, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ...db.models import (
    Category,
    Product,
    ProductReview,
    ProductReviewAspect,
    Ticket,
    TicketAspect,
    User,
)
from ...db.repository import TicketRepository
from ...domain.entities import (
    AspectObservation,
    CategoryEntity,
    ProductEntity,
    ReviewEntity,
    UserEntity,
    UserRole,
)
from ...domain.exceptions import ConflictError


def _to_user_entity(row: User) -> UserEntity:
    role: UserRole = "admin" if row.role == "admin" else "customer"
    return UserEntity(
        id=row.id,
        email=row.email,
        full_name=row.full_name,
        password_hash=row.password_hash,
        role=role,
        is_active=row.is_active,
        created_at=row.created_at,
    )


def _to_product_entity(row: Product) -> ProductEntity:
    cat = row.category
    return ProductEntity(
        id=row.id,
        category_id=row.category_id,
        category_slug=cat.slug if cat else "",
        category_name=cat.name if cat else "",
        slug=row.slug,
        name=row.name,
        short_description=row.short_description,
        description=row.description,
        price=float(row.price),
        image_url=row.image_url,
        sku=row.sku,
        stock=int(row.stock),
        created_at=row.created_at,
    )


def _to_review_entity(row: ProductReview) -> ReviewEntity:
    author = row.author
    aspect_tags = tuple(
        AspectObservation(
            aspect=asp.aspect,
            sentiment=asp.sentiment,
            confidence=float(asp.confidence),
            terms=tuple(asp.terms or ()),
        )
        for asp in row.aspects
    )
    return ReviewEntity(
        id=row.id,
        product_id=row.product_id,
        user_id=row.user_id,
        author_name=author.full_name if author else "Khách hàng",
        ticket_id=row.ticket_id,
        title=row.title,
        content=row.content,
        sentiment_label=row.sentiment_label,
        confidence=float(row.confidence) if row.confidence is not None else None,
        priority_score=float(row.priority_score),
        priority_level=row.priority_level,
        needs_manual_review=bool(row.needs_manual_review),
        aspects=aspect_tags,
        created_at=row.created_at,
    )


class SqlAlchemyUserRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_email(self, email: str) -> UserEntity | None:
        stmt = select(User).where(func.lower(User.email) == email.strip().lower())
        row = self._db.scalar(stmt)
        return _to_user_entity(row) if row else None

    def get_by_id(self, user_id: int) -> UserEntity | None:
        row = self._db.scalar(select(User).where(User.id == user_id))
        return _to_user_entity(row) if row else None

    def create(
        self,
        email: str,
        full_name: str,
        password_hash: str,
        role: UserRole = "customer",
    ) -> UserEntity:
        user = User(
            email=email.strip().lower(),
            full_name=full_name.strip(),
            password_hash=password_hash,
            role=role,
            is_active=True,
        )
        self._db.add(user)
        try:
            self._db.commit()
        except IntegrityError as exc:
            self._db.rollback()
            raise ConflictError("Email này đã được đăng ký tài khoản.") from exc
        self._db.refresh(user)
        return _to_user_entity(user)


class SqlAlchemyCatalogRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_categories(self) -> list[CategoryEntity]:
        stmt = (
            select(Category, func.count(Product.id).label("product_count"))
            .outerjoin(Product, Product.category_id == Category.id)
            .group_by(Category.id)
            .order_by(Category.id.asc())
        )
        rows = self._db.execute(stmt).all()
        return [
            CategoryEntity(
                id=cat.id,
                slug=cat.slug,
                name=cat.name,
                description=cat.description,
                icon=cat.icon,
                product_count=int(count),
            )
            for cat, count in rows
        ]

    def list_products(
        self,
        category_slug: str | None = None,
        search: str | None = None,
        limit: int = 24,
        offset: int = 0,
    ) -> tuple[list[ProductEntity], int]:
        stmt = select(Product).join(Product.category)

        if category_slug:
            stmt = stmt.where(Category.slug == category_slug.strip().lower())

        if search and search.strip():
            pattern = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Product.name.ilike(pattern),
                    Product.short_description.ilike(pattern),
                    Product.description.ilike(pattern),
                    Product.sku.ilike(pattern),
                )
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = int(self._db.scalar(count_stmt) or 0)

        paged = stmt.order_by(Product.id.asc()).offset(offset).limit(limit)
        rows = list(self._db.scalars(paged).unique().all())
        return [_to_product_entity(r) for r in rows], total

    def get_product_by_slug(self, slug: str) -> ProductEntity | None:
        stmt = select(Product).where(Product.slug == slug.strip().lower())
        row = self._db.scalar(stmt)
        return _to_product_entity(row) if row else None

    def get_product_by_id(self, product_id: int) -> ProductEntity | None:
        row = self._db.scalar(select(Product).where(Product.id == product_id))
        return _to_product_entity(row) if row else None

    def get_product_sentiment_counts(self, product_id: int) -> dict[str, int]:
        return self.get_bulk_product_sentiment_counts([product_id]).get(product_id, {})

    def get_product_aspect_observations(self, product_id: int) -> list[AspectObservation]:
        return self.get_bulk_product_aspect_observations([product_id]).get(product_id, [])

    def get_bulk_product_sentiment_counts(
        self, product_ids: list[int]
    ) -> dict[int, dict[str, int]]:
        """Query Storefront's own ProductReview snapshots (zero cross-context JOIN to tickets)."""
        if not product_ids:
            return {}
        stmt = (
            select(
                ProductReview.product_id,
                ProductReview.sentiment_label,
                func.count(ProductReview.id),
            )
            .where(ProductReview.product_id.in_(product_ids))
            .group_by(ProductReview.product_id, ProductReview.sentiment_label)
        )
        result: dict[int, dict[str, int]] = defaultdict(dict)
        for prod_id, label, count in self._db.execute(stmt).all():
            result[int(prod_id)][str(label or "neutral")] = int(count)
        return dict(result)

    def get_bulk_product_aspect_observations(
        self, product_ids: list[int]
    ) -> dict[int, list[AspectObservation]]:
        """Query Storefront's own ProductReviewAspect rows (works identically in split-DB HTTP mode)."""
        if not product_ids:
            return {}
        stmt = (
            select(
                ProductReview.product_id,
                ProductReviewAspect.aspect,
                ProductReviewAspect.sentiment,
                ProductReviewAspect.confidence,
                ProductReviewAspect.terms,
            )
            .join(ProductReviewAspect, ProductReviewAspect.review_id == ProductReview.id)
            .where(ProductReview.product_id.in_(product_ids))
        )
        result: dict[int, list[AspectObservation]] = defaultdict(list)
        for prod_id, aspect, sentiment, confidence, terms in self._db.execute(stmt).all():
            result[int(prod_id)].append(
                AspectObservation(
                    aspect=str(aspect),
                    sentiment=str(sentiment),
                    confidence=float(confidence),
                    terms=tuple(terms or ()),
                )
            )
        return dict(result)


class SqlAlchemyReviewRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_by_product(
        self,
        product_id: int,
        aspect: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[ReviewEntity], int]:
        stmt = select(ProductReview).where(ProductReview.product_id == product_id)

        if aspect and aspect.strip():
            stmt = (
                stmt.join(ProductReviewAspect, ProductReviewAspect.review_id == ProductReview.id)
                .where(ProductReviewAspect.aspect == aspect.strip())
                .distinct()
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = int(self._db.scalar(count_stmt) or 0)

        paged = (
            stmt.order_by(desc(ProductReview.created_at), desc(ProductReview.id))
            .offset(offset)
            .limit(limit)
        )
        rows = list(self._db.scalars(paged).unique().all())
        return [_to_review_entity(r) for r in rows], total

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
        review = ProductReview(
            product_id=product_id,
            user_id=user_id,
            ticket_id=ticket_id,
            title=title.strip() if title and title.strip() else None,
            content=content,
            sentiment_label=sentiment_label,
            confidence=confidence,
            priority_score=float(priority_score),
            priority_level=priority_level,
            needs_manual_review=needs_manual_review,
        )
        for asp in aspects:
            review.aspects.append(
                ProductReviewAspect(
                    aspect=asp.aspect,
                    sentiment=asp.sentiment,
                    confidence=float(asp.confidence),
                    terms=list(asp.terms),
                )
            )
        self._db.add(review)
        self._db.commit()
        self._db.refresh(review)
        return _to_review_entity(review)


class SqlAlchemyTicketRepository:
    """Adapter exposing TicketRepositoryPort over SQLAlchemy Session."""

    def __init__(self, db: Session) -> None:
        self._db = db

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
    ) -> Ticket:
        return TicketRepository.create_ticket(
            db=self._db,
            content=content,
            processed_content=processed_content,
            language_flag=language_flag,
            needs_manual_review=needs_manual_review,
            sentiment_label=sentiment_label,
            confidence=confidence,
            low_confidence=low_confidence,
            priority_score=priority_score,
            priority_level=priority_level,
            priority_breakdown=priority_breakdown,
            dominant_aspect=dominant_aspect,
            status=status,
            assigned_to=assigned_to,
            source=source,
            product_id=product_id,
            product_name=product_name,
            product_slug=product_slug,
            user_id=user_id,
            author_name=author_name,
            aspects_data=aspects_data,
        )

    def get_by_id(self, ticket_id: int) -> Ticket | None:
        return TicketRepository.get_by_id(self._db, ticket_id)

    def get_tickets(
        self,
        limit: int = 50,
        offset: int = 0,
        status: str | None = None,
        aspect: str | None = None,
        sentiment: str | None = None,
    ) -> tuple[list[Ticket], int]:
        return TicketRepository.get_tickets(
            self._db,
            limit=limit,
            offset=offset,
            status=status,
            aspect=aspect,
            sentiment=sentiment,
        )

    def get_unresolved_tickets(self) -> list[Ticket]:
        return TicketRepository.get_unresolved_tickets(self._db)

    def update_status(
        self,
        ticket_id: int,
        new_status: str,
        assigned_to: str | None = None,
    ) -> Ticket | None:
        return TicketRepository.update_status(
            self._db,
            ticket_id=ticket_id,
            new_status=new_status,
            assigned_to=assigned_to,
        )

    def get_stats_overview(self) -> dict[str, Any]:
        return TicketRepository.get_stats_overview(self._db)

    def get_aspect_matrix(self) -> list[tuple[str, str, int]]:
        stmt = (
            select(
                TicketAspect.aspect,
                TicketAspect.sentiment,
                func.count(TicketAspect.id).label("count"),
            )
            .group_by(TicketAspect.aspect, TicketAspect.sentiment)
        )
        return [(str(r[0]), str(r[1]), int(r[2])) for r in self._db.execute(stmt).all()]
