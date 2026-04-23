from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_token, get_current_user, get_password_hash, verify_password
from app.db.database import get_db
from app.models.models import Usuario
from app.schemas.schemas import CurrentUserResponse, SuccessResponse, TokenResponse, UsuarioCreate, UsuarioLogin

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=SuccessResponse[TokenResponse], status_code=status.HTTP_201_CREATED)
def register(payload: UsuarioCreate, db: Session = Depends(get_db)) -> SuccessResponse[TokenResponse]:
    existing_user = db.scalar(select(Usuario).where(Usuario.email == payload.email))
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email ja cadastrado.")

    user = Usuario(
        nome=payload.nome,
        email=payload.email,
        senha_hash=get_password_hash(payload.senha),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return SuccessResponse(
        message="Usuario cadastrado com sucesso.",
        data=TokenResponse(access_token=create_token(str(user.id), {"email": user.email})),
    )


@router.post("/login", response_model=SuccessResponse[TokenResponse])
def login(payload: UsuarioLogin, db: Session = Depends(get_db)) -> SuccessResponse[TokenResponse]:
    user = db.scalar(select(Usuario).where(Usuario.email == payload.email))
    if user is None or not verify_password(payload.senha, user.senha_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais invalidas.")

    return SuccessResponse(
        message="Login realizado com sucesso.",
        data=TokenResponse(access_token=create_token(str(user.id), {"email": user.email})),
    )


@router.get("/me", response_model=SuccessResponse[CurrentUserResponse])
def read_current_user(current_user: Usuario = Depends(get_current_user)) -> SuccessResponse[CurrentUserResponse]:
    return SuccessResponse(
        message="Usuario autenticado carregado com sucesso.",
        data=CurrentUserResponse(
            id=current_user.id,
            nome=current_user.nome,
            name=current_user.nome,
            email=current_user.email,
        ),
    )
