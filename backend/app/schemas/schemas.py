from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class ORMBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    message: str
    data: T


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioBase(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    email: EmailStr

    @model_validator(mode="before")
    @classmethod
    def normalize_name_alias(cls, data: object) -> object:
        if isinstance(data, dict) and "nome" not in data and "name" in data:
            data = {**data, "nome": data["name"]}
        return data


class UsuarioCreate(UsuarioBase):
    senha: str = Field(min_length=6, max_length=128)

    @model_validator(mode="before")
    @classmethod
    def normalize_password_alias(cls, data: object) -> object:
        if isinstance(data, dict) and "senha" not in data and "password" in data:
            data = {**data, "senha": data["password"]}
        return data


class UsuarioRead(ORMBaseSchema, UsuarioBase):
    id: UUID
    criado_em: datetime


class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str

    @model_validator(mode="before")
    @classmethod
    def normalize_password_alias(cls, data: object) -> object:
        if isinstance(data, dict) and "senha" not in data and "password" in data:
            data = {**data, "senha": data["password"]}
        return data


class CurrentUserResponse(BaseModel):
    id: UUID
    nome: str
    name: str
    email: EmailStr


class ExercicioBase(BaseModel):
    nome: str = Field(min_length=2, max_length=160)
    musculo: str = Field(min_length=2, max_length=120)
    descricao: str | None = None


class ExercicioCreate(ExercicioBase):
    pass


class ExercicioUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=160)
    musculo: str | None = Field(default=None, min_length=2, max_length=120)
    descricao: str | None = None


class ExercicioRead(ORMBaseSchema, ExercicioBase):
    id: UUID
    criado_em: datetime


class ItemRotinaBase(BaseModel):
    exercicio_id: UUID
    series: str = Field(min_length=1, max_length=50)
    repeticoes: str = Field(min_length=1, max_length=50)
    ordem: int = Field(ge=1)


class ItemRotinaCreate(ItemRotinaBase):
    pass


class ItemRotinaUpdate(BaseModel):
    exercicio_id: UUID | None = None
    series: str | None = Field(default=None, min_length=1, max_length=50)
    repeticoes: str | None = Field(default=None, min_length=1, max_length=50)
    ordem: int | None = Field(default=None, ge=1)


class ItemRotinaRead(ORMBaseSchema):
    id: UUID
    series: str
    repeticoes: str
    ordem: int
    exercicio: ExercicioRead


class DiaRotinaBase(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    ordem: int = Field(ge=1)
    itens: list[ItemRotinaCreate] = Field(default_factory=list)


class DiaRotinaCreate(DiaRotinaBase):
    pass


class DiaRotinaUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=120)
    ordem: int | None = Field(default=None, ge=1)
    itens: list[ItemRotinaCreate] | None = None


class DiaRotinaRead(ORMBaseSchema):
    id: UUID
    nome: str
    ordem: int
    itens: list[ItemRotinaRead]


class RotinaBase(BaseModel):
    nome: str = Field(min_length=2, max_length=160)


class RotinaCreate(RotinaBase):
    dias: list[DiaRotinaCreate] = Field(default_factory=list)


class RotinaUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=160)
    dias: list[DiaRotinaCreate] | None = None


class RotinaRead(ORMBaseSchema, RotinaBase):
    id: UUID
    usuario_id: UUID
    criado_em: datetime
    atualizado_em: datetime
    dias: list[DiaRotinaRead]


class PaginatedExercicioResponse(BaseModel):
    items: list[ExercicioRead]
    total: int
    page: int
    page_size: int


class PlanilhaExportRequest(BaseModel):
    rotina_id: UUID


class PlanilhaRow(BaseModel):
    dia: str
    exercicio: str
    musculo: str
    series: str
    repeticoes: str


class MessageResponse(BaseModel):
    message: str
    data: dict[str, Any] | None = None


class HealthcheckResponse(BaseModel):
    status: str
