from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DbSession
from app.core.security import create_access_token
from app.schemas.auth import CurrentUserResponse, LoginRequest, RegisterRequest, TokenResponse
from app.schemas.common import ApiResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: DbSession) -> ApiResponse[TokenResponse]:
    usuario = auth_service.register(db, payload)
    return ApiResponse(
        message="Usuário cadastrado com sucesso.",
        data=TokenResponse(access_token=create_access_token(usuario.id)),
    )


@router.post("/login")
def login(payload: LoginRequest, db: DbSession) -> ApiResponse[TokenResponse]:
    usuario = auth_service.authenticate(db, payload)
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
