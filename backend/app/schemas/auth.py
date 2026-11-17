from typing import Annotated
from uuid import UUID

from pydantic import AfterValidator, AliasChoices, EmailStr, Field, computed_field

from app.schemas.common import Schema

# E-mails são comparados sem diferenciar maiúsculas de minúsculas.
NormalizedEmail = Annotated[EmailStr, AfterValidator(str.lower)]


class RegisterRequest(Schema):
    # O frontend envia `name`/`password`; `nome`/`senha` continuam aceitos.
    nome: str = Field(min_length=2, max_length=120, validation_alias=AliasChoices("nome", "name"))
    email: NormalizedEmail
    senha: str = Field(
        min_length=6, max_length=128, validation_alias=AliasChoices("senha", "password")
    )


class LoginRequest(Schema):
    email: NormalizedEmail
    senha: str = Field(
        min_length=1, max_length=128, validation_alias=AliasChoices("senha", "password")
    )


class TokenResponse(Schema):
    access_token: str
    token_type: str = "bearer"


class CurrentUserResponse(Schema):
    id: UUID
    nome: str
    email: str

    @computed_field  # type: ignore[prop-decorator]
    @property
    def name(self) -> str:
        """Alias de `nome` mantido por compatibilidade com o frontend."""
        return self.nome
