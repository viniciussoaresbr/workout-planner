from collections.abc import Sequence

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.orm import Session

from app.models import Exercicio


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _filters(nome: str | None, musculo: str | None) -> list[ColumnElement[bool]]:
    filters: list[ColumnElement[bool]] = []
    if nome and nome.strip():
        filters.append(Exercicio.nome.ilike(f"%{_escape_like(nome.strip())}%", escape="\\"))
    if musculo and musculo.strip():
        filters.append(func.lower(Exercicio.musculo) == musculo.strip().lower())
    return filters


def list_exercicios(
    db: Session,
    *,
    page: int,
    page_size: int,
    nome: str | None = None,
    musculo: str | None = None,
) -> tuple[Sequence[Exercicio], int]:
    filters = _filters(nome, musculo)
    total = db.scalar(select(func.count(Exercicio.id)).where(*filters)) or 0
    items = db.scalars(
        select(Exercicio)
        .where(*filters)
        .order_by(Exercicio.nome)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return items, total


def list_musculos(db: Session) -> list[str]:
    return list(db.scalars(select(Exercicio.musculo).distinct().order_by(Exercicio.musculo)))
