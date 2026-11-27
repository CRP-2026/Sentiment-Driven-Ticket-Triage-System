"""Composition Root wiring Concrete Adapters to Domain DIP Ports."""

import logging
from typing import Any

from sqlalchemy.orm import Session

from ..adapters.persistence.sqlalchemy_repos import (
    SqlAlchemyCatalogRepository,
    SqlAlchemyReviewRepository,
    SqlAlchemyTicketRepository,
    SqlAlchemyUserRepository,
)
from ..adapters.security.jwt_provider import PyJwtTokenProvider
from ..adapters.security.pbkdf2_hasher import Pbkdf2PasswordHasher
from ..adapters.storage.cloudinary_storage import CloudinaryImageStorage
from ..adapters.storage.local_storage import LocalFallbackImageStorage
from ..adapters.triage.http_gateway import HttpTriageGateway
from ..adapters.triage.local_gateway import LocalTriageGateway
from ..application.auth_service import AuthService
from ..application.catalog_service import CatalogService
from ..application.review_service import ReviewService
from ..application.triage_service import TriageService
from ..domain.ports.security import PasswordHasherPort, TokenProviderPort
from ..domain.ports.storage import ImageStoragePort
from ..domain.ports.triage import TriageGatewayPort
from ..settings import Settings

logger = logging.getLogger("ticket_triage.container")


class AppContainer:
    """Single Composition Root instantiating low-level adapters from environment settings."""

    def __init__(
        self,
        *,
        password_hasher: PasswordHasherPort,
        token_provider: TokenProviderPort,
        image_storage: ImageStoragePort,
        triage_gateway_mode: str = "local",
        triage_api_url: str = "",
        triage_api_token: str = "",
        triage_http_timeout_seconds: float = 30.0,
    ) -> None:
        self.password_hasher = password_hasher
        self.token_provider = token_provider
        self.image_storage = image_storage
        self.triage_gateway_mode = triage_gateway_mode
        self.triage_api_url = triage_api_url
        self.triage_api_token = triage_api_token
        self.triage_http_timeout_seconds = triage_http_timeout_seconds

    @classmethod
    def from_settings(cls, cfg: Settings) -> "AppContainer":
        if (
            not cfg.is_testing()
            and cfg.jwt_secret_key == "dev-insecure-jwt-secret-change-in-production"
        ):
            logger.warning(
                "Using default development JWT_SECRET_KEY. Set a strong secret in .env for deployment."
            )

        password_hasher: PasswordHasherPort = Pbkdf2PasswordHasher()
        token_provider: TokenProviderPort = PyJwtTokenProvider(
            secret_key=cfg.jwt_secret_key,
            expire_minutes=cfg.jwt_expire_minutes,
        )

        has_cloudinary = bool(
            cfg.cloudinary_cloud_name.strip()
            and cfg.cloudinary_api_key.strip()
            and cfg.cloudinary_api_secret.strip()
        )
        if has_cloudinary:
            image_storage: ImageStoragePort = CloudinaryImageStorage(
                cloud_name=cfg.cloudinary_cloud_name,
                api_key=cfg.cloudinary_api_key,
                api_secret=cfg.cloudinary_api_secret,
                default_folder=cfg.cloudinary_folder,
            )
            logger.info("ImageStoragePort adapter: Cloudinary (%s)", cfg.cloudinary_cloud_name)
        else:
            image_storage = LocalFallbackImageStorage()
            logger.info("ImageStoragePort adapter: LocalFallbackImageStorage")

        raw_mode = cfg.triage_gateway_mode.strip().lower()
        if raw_mode == "http" and cfg.triage_api_url.strip():
            gateway_mode = "http"
            logger.info("TriageGatewayPort adapter: HttpTriageGateway (%s)", cfg.triage_api_url)
        else:
            if raw_mode == "http":
                logger.warning(
                    "TRIAGE_GATEWAY_MODE=http without TRIAGE_API_URL; falling back to local gateway."
                )
            gateway_mode = "local"
            logger.info("TriageGatewayPort adapter: LocalTriageGateway (in-process)")

        return cls(
            password_hasher=password_hasher,
            token_provider=token_provider,
            image_storage=image_storage,
            triage_gateway_mode=gateway_mode,
            triage_api_url=cfg.triage_api_url.strip(),
            triage_api_token=cfg.triage_api_token.strip(),
            triage_http_timeout_seconds=cfg.triage_http_timeout_seconds,
        )

    def build_auth_service(self, db: Session) -> AuthService:
        return AuthService(
            user_repo=SqlAlchemyUserRepository(db),
            password_hasher=self.password_hasher,
            token_provider=self.token_provider,
        )

    def build_triage_service(self, db: Session, app_state: Any) -> TriageService:
        return TriageService(
            ticket_repo=SqlAlchemyTicketRepository(db),
            sentiment_model=app_state.sentiment_model,
            priority_queue=getattr(app_state, "priority_queue", None),
            taxonomy=getattr(app_state, "taxonomy", None),
            priority_rules=getattr(app_state, "priority_rules", None),
            model_task=getattr(app_state, "model_task", "absa"),
            aspect_keywords=getattr(app_state, "aspect_keywords", None),
            enable_abte=bool(getattr(app_state, "enable_abte", False)),
        )

    def build_triage_gateway(self, db: Session, app_state: Any) -> TriageGatewayPort:
        if self.triage_gateway_mode == "http" and self.triage_api_url:
            return HttpTriageGateway(
                base_url=self.triage_api_url,
                api_token=self.triage_api_token,
                timeout_seconds=self.triage_http_timeout_seconds,
            )
        return LocalTriageGateway(self.build_triage_service(db, app_state))

    def build_catalog_service(self, db: Session, app_state: Any) -> CatalogService:
        return CatalogService(
            catalog_repo=SqlAlchemyCatalogRepository(db),
            review_repo=SqlAlchemyReviewRepository(db),
            image_storage=self.image_storage,
            taxonomy=getattr(app_state, "taxonomy", None),
        )

    def build_review_service(self, db: Session, app_state: Any) -> ReviewService:
        return ReviewService(
            catalog_repo=SqlAlchemyCatalogRepository(db),
            review_repo=SqlAlchemyReviewRepository(db),
            triage_gateway=self.build_triage_gateway(db, app_state),
            taxonomy=getattr(app_state, "taxonomy", None),
        )
