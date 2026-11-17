from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, ConflictError
from app.core.security import burn_password_check, hash_password, verify_password
from app.models import Usuario
from app.schemas.auth import LoginRequest, RegisterRequest


def get_by_email(db: Session, email: str) -> Usuario | None:
    return db.scalar(select(Usuario).where(Usuario.email == email))


def register(db: Session, data: RegisterRequest) -> Usuario:
    if get_by_email(db, data.email) is not None:
        raise ConflictError("E-mail já cadastrado.")

    usuario = Usuario(nome=data.nome, email=data.email, senha_hash=hash_password(data.senha))
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError as exc:  # cadastro concorrente com o mesmo e-mail
        db.rollback()
        raise ConflictError("E-mail já cadastrado.") from exc
    return usuario


def authenticate(db: Session, data: LoginRequest) -> Usuario:
    usuario = get_by_email(db, data.email)
    if usuario is None:
        burn_password_check()
        raise AuthenticationError("Credenciais inválidas.")
    if not verify_password(data.senha, usuario.senha_hash):
        raise AuthenticationError("Credenciais inválidas.")
    return usuario
