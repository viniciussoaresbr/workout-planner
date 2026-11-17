"""Hash de senhas (Argon2 via pwdlib) e emissão/validação de tokens JWT (PyJWT)."""

from datetime import UTC, datetime, timedelta
from functools import lru_cache
from uuid import UUID

import jwt
from pwdlib import PasswordHash

from app.core.config import settings
from app.core.exceptions import AuthenticationError

_password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _password_hash.verify(password, password_hash)


@lru_cache(maxsize=1)
def _dummy_hash() -> str:
    return _password_hash.hash("senha-ficticia-para-tempo-constante")


def burn_password_check() -> None:
    """Executa uma verificação descartável para que o login de um e-mail inexistente
    leve o mesmo tempo de um e-mail existente (evita enumeração de usuários por timing)."""
    _password_hash.verify("senha-invalida", _dummy_hash())


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
