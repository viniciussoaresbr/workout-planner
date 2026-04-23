from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.models import DiaRotina, Exercicio, ItemRotina, Rotina, Usuario
from app.schemas.schemas import MessageResponse, RotinaCreate, RotinaRead, RotinaUpdate, SuccessResponse

router = APIRouter(tags=["rotinas"])


def _get_rotina_or_404(db: Session, rotina_id: UUID, usuario_id: UUID) -> Rotina:
    rotina = db.scalar(
        select(Rotina)
        .options(
            joinedload(Rotina.dias)
            .joinedload(DiaRotina.itens)
            .joinedload(ItemRotina.exercicio)
        )
        .where(Rotina.id == rotina_id, Rotina.usuario_id == usuario_id)
    )
    if rotina is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rotina nao encontrada.")
    return rotina


def _sync_dias(rotina: Rotina, payload: RotinaCreate | RotinaUpdate, db: Session) -> None:
    if payload.dias is None:
        return

    rotina.dias.clear()
    for dia_payload in sorted(payload.dias, key=lambda dia: dia.ordem):
        dia = DiaRotina(nome=dia_payload.nome, ordem=dia_payload.ordem)
        for item_payload in sorted(dia_payload.itens, key=lambda item: item.ordem):
            exercicio = db.get(Exercicio, item_payload.exercicio_id)
            if exercicio is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Exercicio {item_payload.exercicio_id} nao encontrado.",
                )
            dia.itens.append(
                ItemRotina(
                    exercicio_id=item_payload.exercicio_id,
                    series=item_payload.series,
                    repeticoes=item_payload.repeticoes,
                    ordem=item_payload.ordem,
                )
            )
        rotina.dias.append(dia)


@router.post("/", response_model=SuccessResponse[RotinaRead], status_code=status.HTTP_201_CREATED)
def create_rotina(
    payload: RotinaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> SuccessResponse[RotinaRead]:
    rotina = Rotina(
        usuario_id=current_user.id,
        nome=payload.nome,
    )
    _sync_dias(rotina, payload, db)
    db.add(rotina)
    db.commit()
    db.refresh(rotina)
    return SuccessResponse(
        message="Rotina criada com sucesso.",
        data=_get_rotina_or_404(db, rotina.id, current_user.id),
    )


@router.get("/", response_model=SuccessResponse[list[RotinaRead]])
def list_rotinas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> SuccessResponse[list[RotinaRead]]:
    rotinas = db.scalars(
        select(Rotina)
        .options(
            joinedload(Rotina.dias)
            .joinedload(DiaRotina.itens)
            .joinedload(ItemRotina.exercicio)
        )
        .where(Rotina.usuario_id == current_user.id)
        .order_by(Rotina.criado_em.desc())
    ).unique().all()
    return SuccessResponse(message="Rotinas listadas com sucesso.", data=rotinas)


@router.get("/{rotina_id}", response_model=SuccessResponse[RotinaRead])
def get_rotina(
    rotina_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> SuccessResponse[RotinaRead]:
    return SuccessResponse(
        message="Rotina carregada com sucesso.",
        data=_get_rotina_or_404(db, rotina_id, current_user.id),
    )


@router.put("/{rotina_id}", response_model=SuccessResponse[RotinaRead])
def update_rotina(
    rotina_id: UUID,
    payload: RotinaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> SuccessResponse[RotinaRead]:
    rotina = _get_rotina_or_404(db, rotina_id, current_user.id)

    if payload.nome is not None:
        rotina.nome = payload.nome
    if payload.dias is not None:
        _sync_dias(rotina, payload, db)

    db.add(rotina)
    db.commit()
    return SuccessResponse(
        message="Rotina atualizada com sucesso.",
        data=_get_rotina_or_404(db, rotina.id, current_user.id),
    )


@router.delete("/{rotina_id}", response_model=SuccessResponse[MessageResponse])
def delete_rotina(
    rotina_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> SuccessResponse[MessageResponse]:
    rotina = _get_rotina_or_404(db, rotina_id, current_user.id)
    db.delete(rotina)
    db.commit()
    return SuccessResponse(
        message="Rotina removida com sucesso.",
        data=MessageResponse(message="Rotina removida com sucesso."),
    )
