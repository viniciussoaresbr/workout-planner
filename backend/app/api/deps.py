from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models import Usuario

# HTTPBearer permite colar o token direto no botão "Authorize" do Swagger.
_bearer_scheme = HTTPBearer(auto_error=False)

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
) -> Usuario:
    if credentials is None:
        raise AuthenticationError()
    usuario = db.get(Usuario, decode_access_token(credentials.credentials))
    if usuario is None:
        raise AuthenticationError("Usuário não encontrado.")
    return usuario


CurrentUser = Annotated[Usuario, Depends(get_current_user)]
