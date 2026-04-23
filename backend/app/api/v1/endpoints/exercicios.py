from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Exercicio
from app.schemas.schemas import PaginatedExercicioResponse, SuccessResponse

router = APIRouter(tags=["exercicios"])


@router.get("/", response_model=SuccessResponse[PaginatedExercicioResponse])
def list_exercicios(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    nome: str | None = Query(default=None),
    musculo: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> SuccessResponse[PaginatedExercicioResponse]:
    query = select(Exercicio)
    count_query = select(func.count()).select_from(Exercicio)

    if nome:
        ilike_filter = f"%{nome.strip()}%"
        query = query.where(Exercicio.nome.ilike(ilike_filter))
        count_query = count_query.where(Exercicio.nome.ilike(ilike_filter))

    if musculo:
        query = query.where(Exercicio.musculo.ilike(musculo.strip()))
        count_query = count_query.where(Exercicio.musculo.ilike(musculo.strip()))

    total = db.scalar(count_query) or 0
    items = db.scalars(
        query.order_by(Exercicio.nome).offset((page - 1) * page_size).limit(page_size)
    ).all()

    return SuccessResponse(
        message="Exercícios listados com sucesso.",
        data=PaginatedExercicioResponse(items=items, total=total, page=page, page_size=page_size),
    )


@router.get("/musculos", response_model=SuccessResponse[list[str]])
def list_musculos(db: Session = Depends(get_db)) -> SuccessResponse[list[str]]:
    musculos = db.scalars(select(Exercicio.musculo).distinct().order_by(Exercicio.musculo)).all()
    return SuccessResponse(message="Grupos musculares listados com sucesso.", data=list(musculos))
