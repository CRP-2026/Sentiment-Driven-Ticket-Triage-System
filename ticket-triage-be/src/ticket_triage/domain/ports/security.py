"""Security abstraction ports (hashing and stateless token issuance)."""

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ..entities import UserRole


@dataclass(frozen=True)
class TokenPayload:
    user_id: int
    email: str
    role: UserRole


@runtime_checkable
class PasswordHasherPort(Protocol):
    def hash_password(self, plain_password: str) -> str:
        ...

    def verify_password(self, plain_password: str, password_hash: str) -> bool:
        ...


@runtime_checkable
class TokenProviderPort(Protocol):
    def create_access_token(self, user_id: int, email: str, role: UserRole) -> str:
        ...

    def decode_access_token(self, token: str) -> TokenPayload:
        ...
