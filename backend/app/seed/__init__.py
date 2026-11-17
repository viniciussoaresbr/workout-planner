"""Seed idempotente do catálogo de exercícios. Execute com `python -m app.seed`."""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Exercicio
from app.seed.data import EXERCICIOS


@dataclass(frozen=True)
class SeedResult:
    inseridos: int
    atualizados: int
    total: int


def seed_exercicios(db: Session) -> SeedResult:
    """Insere exercícios novos e atualiza os existentes (chave: nome). Nunca remove registros,
    pois exercícios podem estar referenciados por rotinas de usuários."""
    existentes = {e.nome: e for e in db.scalars(select(Exercicio))}
    inseridos = atualizados = 0

    for seed in EXERCICIOS:
        exercicio = existentes.get(seed.nome)
        if exercicio is None:
            db.add(Exercicio(nome=seed.nome, musculo=seed.musculo, descricao=seed.descricao_final))
            inseridos += 1
        elif (exercicio.musculo, exercicio.descricao) != (seed.musculo, seed.descricao_final):
            exercicio.musculo = seed.musculo
            exercicio.descricao = seed.descricao_final
            atualizados += 1

    db.commit()
    return SeedResult(inseridos, atualizados, total=len(existentes) + inseridos)
