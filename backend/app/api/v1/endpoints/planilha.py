from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.models import DiaRotina, ItemRotina, Rotina, Usuario
from app.schemas.schemas import PlanilhaExportRequest
from app.services.planilha_service import build_workout_workbook

router = APIRouter(tags=["planilha"])


@router.post("/export")
def export_planilha(
    payload: PlanilhaExportRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> StreamingResponse:
    rotina = db.scalar(
        select(Rotina)
        .options(
            joinedload(Rotina.dias)
            .joinedload(DiaRotina.itens)
            .joinedload(ItemRotina.exercicio)
        )
        .where(Rotina.id == payload.rotina_id, Rotina.usuario_id == current_user.id)
    )
    if rotina is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rotina nao encontrada.")

    workbook_io = build_workout_workbook(rotina)
    filename = f"rotina-{rotina.nome.lower().replace(' ', '-')}.xlsx"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        workbook_io,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
