"""Unit tests verifying Dependency Inversion Principle (SOLID-D) and Concrete Adapters."""

from datetime import UTC, datetime

import httpx
import pytest

from ticket_triage.adapters.persistence.sqlalchemy_repos import (
    SqlAlchemyCatalogRepository,
    SqlAlchemyReviewRepository,
    SqlAlchemyTicketRepository,
    SqlAlchemyUserRepository,
)
from ticket_triage.adapters.security.jwt_provider import PyJwtTokenProvider
from ticket_triage.adapters.security.pbkdf2_hasher import Pbkdf2PasswordHasher
from ticket_triage.adapters.storage.cloudinary_storage import CloudinaryImageStorage
from ticket_triage.adapters.storage.local_storage import LocalFallbackImageStorage
from ticket_triage.adapters.triage.http_gateway import HttpTriageGateway
from ticket_triage.adapters.triage.local_gateway import LocalTriageGateway
from ticket_triage.application.auth_service import AuthService
from ticket_triage.application.review_service import ReviewService
from ticket_triage.application.triage_service import TriageService
from ticket_triage.core.sentiment.mock import MockSentimentModel
from ticket_triage.domain.entities import (
    AspectObservation,
    CategoryEntity,
    ProductEntity,
    ReviewEntity,
    TriageDispatchRequest,
    TriageDispatchResult,
    UserEntity,
    UserRole,
)
from ticket_triage.domain.exceptions import AuthenticationError, ConflictError
from ticket_triage.domain.ports import (
    CatalogRepositoryPort,
    ImageStoragePort,
    PasswordHasherPort,
    ReviewRepositoryPort,
    TicketRepositoryPort,
    TokenPayload,
    TokenProviderPort,
    TriageGatewayPort,
    UserRepositoryPort,
)


# ==============================================================================
# Pure In-Memory Fakes proving Application Services have ZERO DB/HTTP/ML coupling
# ==============================================================================
class FakeUserRepo:
    def __init__(self) -> None:
        self._users: dict[int, UserEntity] = {}
        self._seq = 1

    def get_by_email(self, email: str) -> UserEntity | None:
        target = email.strip().lower()
        return next((u for u in self._users.values() if u.email == target), None)

    def get_by_id(self, user_id: int) -> UserEntity | None:
        return self._users.get(user_id)

    def create(
        self,
        email: str,
        full_name: str,
        password_hash: str,
        role: UserRole = "customer",
    ) -> UserEntity:
        user = UserEntity(
            id=self._seq,
            email=email,
            full_name=full_name,
            password_hash=password_hash,
            role=role,
            is_active=True,
            created_at=datetime.now(UTC),
        )
        self._users[self._seq] = user
        self._seq += 1
        return user


class FakeHasher:
    def hash_password(self, plain_password: str) -> str:
        return f"fake::{plain_password}"

    def verify_password(self, plain_password: str, password_hash: str) -> bool:
        return password_hash == f"fake::{plain_password}"


class FakeTokenProvider:
    def create_access_token(self, user_id: int, email: str, role: UserRole) -> str:
        return f"tok:{user_id}:{email}:{role}"

    def decode_access_token(self, token: str) -> TokenPayload:
        parts = token.split(":")
        if len(parts) != 4 or parts[0] != "tok":
            raise AuthenticationError("Invalid fake token")
        return TokenPayload(
            user_id=int(parts[1]),
            email=parts[2],
            role=parts[3],  # type: ignore[arg-type]
        )


class FakeCatalogRepo:
    def __init__(self, product: ProductEntity) -> None:
        self._product = product
        self.sentiment_counts: dict[str, int] = {"positive": 1}
        self.aspect_obs: list[AspectObservation] = [
            AspectObservation(aspect="product_quality", sentiment="positive", confidence=0.92)
        ]

    def list_categories(self) -> list[CategoryEntity]:
        return []

    def list_products(self, category_slug=None, search=None, limit=24, offset=0):
        return [self._product], 1

    def get_product_by_slug(self, slug: str) -> ProductEntity | None:
        return self._product if slug == self._product.slug else None

    def get_product_by_id(self, product_id: int) -> ProductEntity | None:
        return self._product if product_id == self._product.id else None

    def get_product_sentiment_counts(self, product_id: int) -> dict[str, int]:
        return dict(self.sentiment_counts)

    def get_product_aspect_observations(self, product_id: int) -> list[AspectObservation]:
        return list(self.aspect_obs)

    def get_bulk_product_sentiment_counts(self, product_ids: list[int]):
        return {pid: self.get_product_sentiment_counts(pid) for pid in product_ids}

    def get_bulk_product_aspect_observations(self, product_ids: list[int]):
        return {pid: self.get_product_aspect_observations(pid) for pid in product_ids}


class FakeReviewRepo:
    def __init__(self) -> None:
        self.created: list[ReviewEntity] = []

    def list_by_product(self, product_id: int, aspect=None, limit=50, offset=0):
        return list(self.created), len(self.created)

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
        rev = ReviewEntity(
            id=len(self.created) + 1,
            product_id=product_id,
            user_id=user_id,
            author_name="Fake Customer",
            ticket_id=ticket_id,
            title=title,
            content=content,
            sentiment_label=sentiment_label or "positive",
            confidence=confidence if confidence is not None else 0.95,
            priority_score=priority_score,
            priority_level=priority_level,
            needs_manual_review=needs_manual_review,
            aspects=aspects,
            created_at=datetime.now(UTC),
        )
        self.created.append(rev)
        return rev


class FakeTriageGateway:
    def __init__(self) -> None:
        self.dispatched: list[TriageDispatchRequest] = []

    def dispatch_ticket(self, request: TriageDispatchRequest) -> TriageDispatchResult:
        self.dispatched.append(request)
        return TriageDispatchResult(
            ticket_id=42,
            sentiment_label="positive",
            confidence=0.95,
            priority_score=5.0,
            priority_level="LOW",
            dominant_aspect="product_quality",
            needs_manual_review=False,
            aspects=(
                AspectObservation(aspect="product_quality", sentiment="positive", confidence=0.95),
            ),
        )


def test_concrete_adapters_conform_to_domain_protocols(in_memory_db):
    assert isinstance(Pbkdf2PasswordHasher(), PasswordHasherPort)
    assert isinstance(PyJwtTokenProvider("secret-key-for-protocol-test-32bytes"), TokenProviderPort)
    assert isinstance(LocalFallbackImageStorage(), ImageStoragePort)
    assert isinstance(CloudinaryImageStorage("demo", "k", "s"), ImageStoragePort)
    assert isinstance(SqlAlchemyUserRepository(in_memory_db), UserRepositoryPort)
    assert isinstance(SqlAlchemyCatalogRepository(in_memory_db), CatalogRepositoryPort)
    assert isinstance(SqlAlchemyReviewRepository(in_memory_db), ReviewRepositoryPort)
    ticket_repo = SqlAlchemyTicketRepository(in_memory_db)
    assert isinstance(ticket_repo, TicketRepositoryPort)

    triage_service = TriageService(
        ticket_repo=ticket_repo,
        sentiment_model=MockSentimentModel(),
    )
    assert isinstance(LocalTriageGateway(triage_service), TriageGatewayPort)
    assert isinstance(HttpTriageGateway("http://triage.internal"), TriageGatewayPort)


def test_auth_service_runs_with_pure_in_memory_fakes():
    service = AuthService(
        user_repo=FakeUserRepo(),
        password_hasher=FakeHasher(),
        token_provider=FakeTokenProvider(),
    )

    token, user = service.register("alice@example.com", "Alice Nguyen", "secret123")
    assert user.role == "customer"
    assert token.startswith("tok:")

    with pytest.raises(ConflictError):
        service.register("ALICE@example.com", "Alice Duplicate", "secret123")

    login_token, logged_user = service.login("alice@example.com", "secret123")
    assert logged_user.id == user.id
    assert service.authenticate_token(login_token).email == "alice@example.com"

    with pytest.raises(AuthenticationError):
        service.login("alice@example.com", "wrong-password")


def test_review_service_depends_only_on_triage_gateway_port(sample_taxonomy):
    product = ProductEntity(
        id=7,
        category_id=1,
        category_slug="smartphones",
        category_name="Điện thoại",
        slug="aerophone-pro",
        name="AeroPhone Pro",
        short_description="Flagship smartphone",
        description="Flagship smartphone",
        price=799.0,
        image_url="/images/products/phone.svg",
        sku="PH-001",
        stock=10,
        created_at=datetime.now(UTC),
    )
    user = UserEntity(
        id=3,
        email="buyer@example.com",
        full_name="Buyer",
        password_hash="h",
        role="customer",
        is_active=True,
        created_at=datetime.now(UTC),
    )
    gateway = FakeTriageGateway()
    review_repo = FakeReviewRepo()
    service = ReviewService(
        catalog_repo=FakeCatalogRepo(product),
        review_repo=review_repo,
        triage_gateway=gateway,
        taxonomy=sample_taxonomy,
    )

    result = service.submit_review(
        user=user,
        product_slug="aerophone-pro",
        content="Great battery life and awesome build quality!",
        title="Love it",
    )

    assert len(gateway.dispatched) == 1
    assert gateway.dispatched[0].source == "storefront_review"
    assert gateway.dispatched[0].product_id == 7
    assert result.review.ticket_id == 42
    assert result.triage.ticket_id == 42
    assert result.insights.top_ranked_aspects[0].rank == 1


def test_http_triage_gateway_dispatches_over_http_without_touching_review_service():
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["auth"] = request.headers.get("Authorization")
        return httpx.Response(
            201,
            json={
                "id": 501,
                "sentiment_label": "negative",
                "confidence": 0.94,
                "priority_score": 88.5,
                "priority_level": "CRITICAL",
                "dominant_aspect": "refund_payment",
                "needs_manual_review": False,
                "aspects": [
                    {
                        "aspect": "refund_payment",
                        "sentiment": "negative",
                        "confidence": 0.94,
                        "terms": ["charged twice"],
                    }
                ],
            },
        )

    mock_client = httpx.Client(transport=httpx.MockTransport(handler))
    gateway = HttpTriageGateway(
        base_url="https://ml-triage.example.com",
        api_token="svc-jwt-token",
        http_client=mock_client,
    )

    res = gateway.dispatch_ticket(
        TriageDispatchRequest(
            content="I was charged twice! Refund ASAP!",
            product_id=10,
            product_name="AeroPhone Pro",
            product_slug="aerophone-pro",
            user_id=2,
            author_name="Alice",
            source="storefront_review",
        )
    )

    assert captured["url"] == "https://ml-triage.example.com/api/v1/tickets"
    assert captured["auth"] == "Bearer svc-jwt-token"
    assert res.ticket_id == 501
    assert res.priority_level == "CRITICAL"
    assert res.aspects[0].aspect == "refund_payment"
    assert res.aspects[0].terms == ("charged twice",)


def test_local_fallback_storage_sanitizes_folder_traversal(tmp_path):
    storage = LocalFallbackImageStorage(upload_dir=tmp_path)
    url = storage.upload_image(b"pngbytes", "../evil.png", folder="../../outside")
    assert ".." not in url
    assert url.startswith("/images/outside/")


def test_cloudinary_storage_signs_upload_and_optimizes_delivery_url():
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["body"] = request.read()
        return httpx.Response(
            200,
            json={
                "secure_url": "https://res.cloudinary.com/demo-cloud/image/upload/v170000/products/phone.png"
            },
        )

    mock_client = httpx.Client(transport=httpx.MockTransport(handler))
    storage = CloudinaryImageStorage(
        cloud_name="demo-cloud",
        api_key="test-key",
        api_secret="test-secret",
        http_client=mock_client,
    )

    uploaded_url = storage.upload_image(b"\x89PNG\r\n\x1a\nfake", "phone.png", folder="products")
    assert captured["url"] == "https://api.cloudinary.com/v1_1/demo-cloud/image/upload"
    assert b"signature" in captured["body"]
    assert "/image/upload/f_auto,q_auto/" in uploaded_url
    assert storage.resolve_url(uploaded_url) == uploaded_url


def test_pbkdf2_hasher_and_pyjwt_provider_roundtrip():
    hasher = Pbkdf2PasswordHasher(iterations=10_000)
    h1 = hasher.hash_password("MyPass@2026")
    h2 = hasher.hash_password("MyPass@2026")
    assert h1 != h2  # Random per-password salt
    assert hasher.verify_password("MyPass@2026", h1) is True
    assert hasher.verify_password("WrongPass", h1) is False

    provider = PyJwtTokenProvider(secret_key="super-secret-key-at-least-32-bytes-long", expire_minutes=60)
    token = provider.create_access_token(user_id=12, email="admin@triage.shop", role="admin")
    payload = provider.decode_access_token(token)
    assert payload.user_id == 12
    assert payload.email == "admin@triage.shop"
    assert payload.role == "admin"

    with pytest.raises(AuthenticationError):
        provider.decode_access_token("not.a.valid.jwt")
