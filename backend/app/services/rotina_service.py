from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import BadRequestError, NotFoundError
from app.models import DiaRotina, Exercicio, ItemRotina, Rotina
from app.schemas.rotina import DiaRotinaInput, RotinaCreate, RotinaUpdate


def _rotinas_do_usuario(usuario_id: UUID) -> Select[tuple[Rotina]]:
    """Consulta base com a árvore completa (dias → itens → exercício) carregada em lote."""
    return (
        select(Rotina)
        .where(Rotina.usuario_id == usuario_id)
        .options(
            selectinload(Rotina.dias).selectinload(DiaRotina.itens).joinedload(ItemRotina.exercicio)
        )
    )


def list_for_user(db: Session, usuario_id: UUID) -> Sequence[Rotina]:
    return db.scalars(
        _rotinas_do_usuario(usuario_id).order_by(Rotina.criado_em.desc(), Rotina.id)
    ).all()


def get_for_user(db: Session, rotina_id: UUID, usuario_id: UUID) -> Rotina:
    rotina = db.scalar(_rotinas_do_usuario(usuario_id).where(Rotina.id == rotina_id))
    if rotina is None:
        raise NotFoundError("Rotina não encontrada.")
    return rotina


def create(db: Session, usuario_id: UUID, data: RotinaCreate) -> Rotina:
    exercicios = _load_exercicios(db, data.exercicio_ids())
    rotina = Rotina(usuario_id=usuario_id, nome=data.nome, dias=_build_dias(data.dias, exercicios))
    db.add(rotina)
    db.commit()
    return get_for_user(db, rotina.id, usuario_id)


def update(db: Session, rotina_id: UUID, usuario_id: UUID, data: RotinaUpdate) -> Rotina:
    rotina = get_for_user(db, rotina_id, usuario_id)

    if data.nome is not None:
        rotina.nome = data.nome
    if data.dias is not None:
        exercicios = _load_exercicios(db, data.exercicio_ids())
        # Remove os dias antigos antes de inserir os novos para não violar
        # a constraint única (rotina_id, ordem).
        rotina.dias.clear()
        db.flush()
        rotina.dias.extend(_build_dias(data.dias, exercicios))
    # `onupdate` só dispara quando colunas da própria rotina mudam.
    rotina.atualizado_em = func.now()

    db.commit()
    return get_for_user(db, rotina_id, usuario_id)


def delete(db: Session, rotina_id: UUID, usuario_id: UUID) -> None:
    rotina = get_for_user(db, rotina_id, usuario_id)
    db.delete(rotina)
    db.commit()


def _load_exercicios(db: Session, ids: set[UUID]) -> dict[UUID, Exercicio]:
    """Busca todos os exercícios referenciados em uma única consulta."""
    if not ids:
        return {}
    exercicios = {e.id: e for e in db.scalars(select(Exercicio).where(Exercicio.id.in_(ids)))}
    missing = ids - exercicios.keys()
    if missing:
        raise BadRequestError(
            "Exercício não encontrado.",
            details={"exercicio_ids": sorted(str(exercicio_id) for exercicio_id in missing)},
        )
    return exercicios


def _build_dias(dias: list[DiaRotinaInput], exercicios: dict[UUID, Exercicio]) -> list[DiaRotina]:
    return [
        DiaRotina(
            nome=dia.nome,
            ordem=dia.ordem,
            itens=[
                ItemRotina(
                    exercicio=exercicios[item.exercicio_id],
                    series=item.series,
                    repeticoes=item.repeticoes,
                    ordem=item.ordem,
                )
                for item in sorted(dia.itens, key=lambda item: item.ordem)
            ],
        )
        for dia in sorted(dias, key=lambda dia: dia.ordem)
    ]
