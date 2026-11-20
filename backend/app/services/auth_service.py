from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, ConflictError
from app.core.rate_limit import login_account_limiter, login_failure_key, login_failure_limiter
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


def authenticate(db: Session, data: LoginRequest, client_ip: str) -> Usuario:
    # Os bloqueios valem também para e-mails inexistentes, para não revelar quais contas
    # existem. O bloqueio por e-mail + IP só afeta quem errou; o por conta (todos os IPs)
    # tem limite alto e só é atingido por força bruta distribuída.
    failure_key = login_failure_key(data.email, client_ip)
    login_failure_limiter.check(failure_key)
    login_account_limiter.check(data.email)

    usuario = get_by_email(db, data.email)
    if usuario is None:
        burn_password_check()
    elif verify_password(data.senha, usuario.senha_hash):
        # O contador da conta não é zerado: um login legítimo no meio de um ataque
        # distribuído não deve devolver tentativas aos atacantes.
        login_failure_limiter.clear(failure_key)
        return usuario

    login_failure_limiter.add(failure_key)
    login_account_limiter.add(data.email)
    raise AuthenticationError("Credenciais inválidas.")
