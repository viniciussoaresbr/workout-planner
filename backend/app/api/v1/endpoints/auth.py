from collections.abc import Callable

from fastapi import APIRouter, Depends, Request, status

from app.api.deps import CurrentUser, DbSession
from app.core.rate_limit import RateLimiter, client_ip, login_ip_limiter, register_ip_limiter
from app.core.security import create_access_token
from app.schemas.auth import CurrentUserResponse, LoginRequest, RegisterRequest, TokenResponse
from app.schemas.common import ApiResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


def _limit_by_ip(limiter: RateLimiter) -> Callable[[Request], None]:
    """Conta a requisição pelo IP do cliente."""

    def dependency(request: Request) -> None:
        limiter.hit(client_ip(request))

    return dependency


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(_limit_by_ip(register_ip_limiter))],
)
def register(payload: RegisterRequest, db: DbSession) -> ApiResponse[TokenResponse]:
    usuario = auth_service.register(db, payload)
    return ApiResponse(
        message="Usuário cadastrado com sucesso.",
        data=TokenResponse(access_token=create_access_token(usuario.id)),
    )


@router.post("/login", dependencies=[Depends(_limit_by_ip(login_ip_limiter))])
def login(payload: LoginRequest, db: DbSession, request: Request) -> ApiResponse[TokenResponse]:
    usuario = auth_service.authenticate(db, payload, client_ip(request))
    return ApiResponse(
        message="Login realizado com sucesso.",
        data=TokenResponse(access_token=create_access_token(usuario.id)),
    )


@router.get("/me")
def read_current_user(current_user: CurrentUser) -> ApiResponse[CurrentUserResponse]:
    return ApiResponse(
        message="Usuário autenticado carregado com sucesso.",
        data=CurrentUserResponse.model_validate(current_user),
    )
