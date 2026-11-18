from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, ConflictError
from app.core.rate_limit import login_failure_limiter
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
    # Bloqueia o e-mail após várias falhas, mesmo que venham de IPs diferentes.
    # Vale também para e-mails inexistentes, para não revelar quais contas existem.
    login_failure_limiter.check(data.email)

    usuario = get_by_email(db, data.email)
    if usuario is None:
        burn_password_check()
    elif verify_password(data.senha, usuario.senha_hash):
        login_failure_limiter.clear(data.email)
        return usuario

    login_failure_limiter.add(data.email)
    raise AuthenticationError("Credenciais inválidas.")
