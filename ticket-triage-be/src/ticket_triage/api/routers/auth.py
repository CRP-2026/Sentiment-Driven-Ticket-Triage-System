"""Authentication router: register, login, and current-user profile."""

from fastapi import APIRouter, Depends, status

from ...application.auth_service import AuthService
from ...domain.entities import UserEntity
from ..dependencies import get_auth_service, get_current_user
from ..mappers import to_user_out
from ..schemas import AuthResponse, LoginIn, RegisterIn, UserOut

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterIn,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    """Đăng ký tài khoản khách hàng mới và cấp phát JWT access token."""
    token, user = auth_service.register(
        email=payload.email,
        full_name=payload.full_name,
        password=payload.password,
    )
    return AuthResponse(access_token=token, user=to_user_out(user))


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginIn,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    """Đăng nhập bằng email và mật khẩu (hỗ trợ cả customer và admin)."""
    token, user = auth_service.login(email=payload.email, password=payload.password)
    return AuthResponse(access_token=token, user=to_user_out(user))


@router.get("/me", response_model=UserOut)
def get_me(current_user: UserEntity = Depends(get_current_user)) -> UserOut:
    """Trả về thông tin tài khoản hiện đang đăng nhập."""
    return to_user_out(current_user)
