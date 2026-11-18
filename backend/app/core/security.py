"""Hash de senhas (Argon2 via pwdlib) e emissão/validação de tokens JWT (PyJWT)."""

from datetime import UTC, datetime, timedelta
from functools import lru_cache
from threading import BoundedSemaphore
from uuid import UUID

import jwt
from pwdlib import PasswordHash

from app.core.config import settings
from app.core.exceptions import AuthenticationError

_password_hash = PasswordHash.recommended()
# Argon2 (padrão do pwdlib) usa ~64 MiB por operação. Sem um teto, uma rajada de logins
# ocupa todas as threads do servidor e esgota a memória.
_hash_slots = BoundedSemaphore(settings.password_hash_concurrency)


def hash_password(password: str) -> str:
    with _hash_slots:
        return _password_hash.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    with _hash_slots:
        return _password_hash.verify(password, password_hash)


@lru_cache(maxsize=1)
def _dummy_hash() -> str:
    return hash_password("senha-ficticia-para-tempo-constante")


def burn_password_check() -> None:
    """Executa uma verificação descartável para que o login de um e-mail inexistente
    leve o mesmo tempo de um e-mail existente (evita enumeração de usuários por timing)."""
    verify_password("senha-invalida", _dummy_hash())


def create_access_token(user_id: UUID) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(
        payload, settings.jwt_secret_key.get_secret_value(), algorithm=settings.jwt_algorithm
    )


def decode_access_token(token: str) -> UUID:
    """Valida o token e retorna o id do usuário (claim `sub`)."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "sub"]},
        )
        return UUID(payload["sub"])
    except (jwt.InvalidTokenError, ValueError) as exc:
        raise AuthenticationError("Token inválido ou expirado.") from exc
