"""FastAPI dependency providers injecting Application Services and RBAC guards."""

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..adapters.persistence.sqlalchemy_repos import SqlAlchemyTicketRepository
from ..application.auth_service import AuthService
from ..application.catalog_service import CatalogService
from ..application.review_service import ReviewService
from ..application.triage_service import TriageService
from ..db.session import get_db
from ..domain.entities import UserEntity
from ..domain.exceptions import AuthenticationError, AuthorizationError
from ..domain.ports.repositories import TicketRepositoryPort
from ..domain.ports.storage import ImageStoragePort
from ..settings import settings
from .container import AppContainer

_bearer_scheme = HTTPBearer(auto_error=False)


def get_container(request: Request) -> AppContainer:
    container = getattr(request.app.state, "container", None)
    if container is None:
        container = AppContainer.from_settings(settings)
        request.app.state.container = container
    return container


def get_auth_service(
    db: Session = Depends(get_db),
    container: AppContainer = Depends(get_container),
) -> AuthService:
    return container.build_auth_service(db)


def get_catalog_service(
    request: Request,
    db: Session = Depends(get_db),
    container: AppContainer = Depends(get_container),
) -> CatalogService:
    return container.build_catalog_service(db, request.app.state)


def get_review_service(
    request: Request,
    db: Session = Depends(get_db),
    container: AppContainer = Depends(get_container),
) -> ReviewService:
    return container.build_review_service(db, request.app.state)


def get_triage_service(
    request: Request,
    db: Session = Depends(get_db),
    container: AppContainer = Depends(get_container),
) -> TriageService:
    return container.build_triage_service(db, request.app.state)


def get_ticket_repository(db: Session = Depends(get_db)) -> TicketRepositoryPort:
    return SqlAlchemyTicketRepository(db)


def get_image_storage(
    container: AppContainer = Depends(get_container),
) -> ImageStoragePort:
    return container.image_storage


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserEntity:
    if credentials is None or not credentials.credentials:
        raise AuthenticationError("Vui lòng đăng nhập để sử dụng chức năng này.")
    return auth_service.authenticate_token(credentials.credentials)


def get_current_admin(
    current_user: UserEntity = Depends(get_current_user),
) -> UserEntity:
    if current_user.role != "admin":
        raise AuthorizationError("Chỉ tài khoản quản trị viên mới có quyền truy cập khu vực này.")
    return current_user
