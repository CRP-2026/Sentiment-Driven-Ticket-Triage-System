"""Authentication use-case service adhering strictly to SOLID-D ports."""

import re

from ..domain.entities import UserEntity
from ..domain.exceptions import (
    AuthenticationError,
    ConflictError,
    ValidationDomainError,
)
from ..domain.ports.repositories import UserRepositoryPort
from ..domain.ports.security import PasswordHasherPort, TokenProviderPort

_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


class AuthService:
    """Handles customer registration, login, and token verification via abstract ports."""

    def __init__(
        self,
        user_repo: UserRepositoryPort,
        password_hasher: PasswordHasherPort,
        token_provider: TokenProviderPort,
    ) -> None:
        self._user_repo = user_repo
        self._password_hasher = password_hasher
        self._token_provider = token_provider

    def register(
        self,
        email: str,
        full_name: str,
        password: str,
    ) -> tuple[str, UserEntity]:
        normalized_email = email.strip().lower()
        cleaned_name = full_name.strip()

        if not _EMAIL_RE.match(normalized_email):
            raise ValidationDomainError("Địa chỉ email không hợp lệ.")
        if len(cleaned_name) < 2 or len(cleaned_name) > 120:
            raise ValidationDomainError("Họ tên phải có độ dài từ 2 đến 120 ký tự.")
        if len(password) < 6 or len(password) > 128:
            raise ValidationDomainError("Mật khẩu phải có độ dài từ 6 đến 128 ký tự.")

        if self._user_repo.get_by_email(normalized_email) is not None:
            raise ConflictError("Email này đã được đăng ký tài khoản.")

        password_hash = self._password_hasher.hash_password(password)
        user = self._user_repo.create(
            email=normalized_email,
            full_name=cleaned_name,
            password_hash=password_hash,
            role="customer",
        )
        token = self._token_provider.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
        )
        return token, user

    def login(self, email: str, password: str) -> tuple[str, UserEntity]:
        normalized_email = email.strip().lower()
        user = self._user_repo.get_by_email(normalized_email)
        if user is None or not self._password_hasher.verify_password(
            password, user.password_hash
        ):
            raise AuthenticationError("Email hoặc mật khẩu không chính xác.")
        if not user.is_active:
            raise AuthenticationError("Tài khoản đã bị vô hiệu hóa.")

        token = self._token_provider.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
        )
        return token, user

    def authenticate_token(self, token: str) -> UserEntity:
        payload = self._token_provider.decode_access_token(token)
        user = self._user_repo.get_by_id(payload.user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("Tài khoản không tồn tại hoặc đã bị vô hiệu hóa.")
        return user
