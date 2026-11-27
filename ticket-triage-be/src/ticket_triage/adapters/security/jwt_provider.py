"""PyJWT HS256 implementation of TokenProviderPort."""

from datetime import UTC, datetime, timedelta

import jwt

from ...domain.entities import UserRole
from ...domain.exceptions import AuthenticationError
from ...domain.ports.security import TokenPayload


class PyJwtTokenProvider:
    """Stateless JWT provider compatible with multi-replica cloud deployments."""

    ALGORITHM = "HS256"

    def __init__(self, secret_key: str, expire_minutes: int = 720) -> None:
        self._secret_key = secret_key
        self._expire_minutes = expire_minutes

    def create_access_token(self, user_id: int, email: str, role: UserRole) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": str(user_id),
            "email": email,
            "role": role,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=self._expire_minutes)).timestamp()),
        }
        return jwt.encode(payload, self._secret_key, algorithm=self.ALGORITHM)

    def decode_access_token(self, token: str) -> TokenPayload:
        try:
            decoded = jwt.decode(token, self._secret_key, algorithms=[self.ALGORITHM])
            raw_sub = decoded.get("sub")
            email = str(decoded.get("email", "")).strip()
            role = str(decoded.get("role", "")).strip()
            if raw_sub is None or not email or role not in ("customer", "admin"):
                raise AuthenticationError("Token không hợp lệ hoặc thiếu thông tin định danh.")
            return TokenPayload(
                user_id=int(raw_sub),
                email=email,
                role=role,  # type: ignore[arg-type]
            )
        except jwt.ExpiredSignatureError as exc:
            raise AuthenticationError("Phiên đăng nhập đã hết hạn, vui lòng đăng nhập lại.") from exc
        except (jwt.InvalidTokenError, ValueError, TypeError) as exc:
            raise AuthenticationError("Token xác thực không hợp lệ.") from exc
