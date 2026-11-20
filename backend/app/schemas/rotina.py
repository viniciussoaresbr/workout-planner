from collections.abc import Iterable
from datetime import datetime
from typing import Protocol
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.common import Schema
from app.schemas.exercicio import ExercicioRead


class _Ordenado(Protocol):
    ordem: int


def _ensure_unique_ordem[T: _Ordenado](values: list[T], label: str) -> list[T]:
    ordens = [value.ordem for value in values]
    if len(ordens) != len(set(ordens)):
        raise ValueError(f"Cada {label} precisa ter uma ordem única.")
    return values


# ---- Entrada ----


class ItemRotinaInput(Schema):
    exercicio_id: UUID
    series: str = Field(min_length=1, max_length=50)
    repeticoes: str = Field(min_length=1, max_length=50)
    ordem: int = Field(ge=1)


class DiaRotinaInput(Schema):
    nome: str = Field(min_length=2, max_length=120)
    ordem: int = Field(ge=1)
    itens: list[ItemRotinaInput] = Field(default_factory=list, max_length=50)

    @field_validator("itens")
    @classmethod
    def validar_ordem_itens(cls, itens: list[ItemRotinaInput]) -> list[ItemRotinaInput]:
        return _ensure_unique_ordem(itens, "exercício do dia")


class RotinaCreate(Schema):
    nome: str = Field(min_length=2, max_length=160)
    dias: list[DiaRotinaInput] = Field(default_factory=list, max_length=14)

    @field_validator("dias")
    @classmethod
    def validar_ordem_dias(cls, dias: list[DiaRotinaInput]) -> list[DiaRotinaInput]:
        return _ensure_unique_ordem(dias, "dia")

    def exercicio_ids(self) -> set[UUID]:
        return _exercicio_ids(self.dias)


class RotinaUpdate(Schema):
    """Atualização parcial: campos omitidos não são alterados; `dias` substitui todos os dias."""

    nome: str | None = Field(default=None, min_length=2, max_length=160)
    dias: list[DiaRotinaInput] | None = Field(default=None, max_length=14)

    @field_validator("dias")
    @classmethod
    def validar_ordem_dias(cls, dias: list[DiaRotinaInput] | None) -> list[DiaRotinaInput] | None:
        return None if dias is None else _ensure_unique_ordem(dias, "dia")

    def exercicio_ids(self) -> set[UUID]:
        return _exercicio_ids(self.dias or [])


def _exercicio_ids(dias: Iterable[DiaRotinaInput]) -> set[UUID]:
    return {item.exercicio_id for dia in dias for item in dia.itens}


# ---- Saída ----


class ItemRotinaRead(Schema):
    id: UUID
    series: str
    repeticoes: str
    ordem: int
    exercicio: ExercicioRead


class DiaRotinaRead(Schema):
    id: UUID
    nome: str
    ordem: int
    itens: list[ItemRotinaRead]


class RotinaRead(Schema):
    id: UUID
    usuario_id: UUID
    nome: str
    criado_em: datetime
    atualizado_em: datetime
    dias: list[DiaRotinaRead]


class RotinaExportRequest(Schema):
    rotina_id: UUID
