from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import DbSession
from app.schemas.common import ApiResponse, Page
from app.schemas.exercicio import ExercicioRead
from app.services import exercicio_service

router = APIRouter(prefix="/exercicios", tags=["exercicios"])


@router.get("")
def list_exercicios(
    db: DbSession,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    nome: Annotated[str | None, Query(max_length=160, description="Busca parcial")] = None,
    musculo: Annotated[str | None, Query(max_length=120, description="Grupo exato")] = None,
) -> ApiResponse[Page[ExercicioRead]]:
    items, total = exercicio_service.list_exercicios(
        db, page=page, page_size=page_size, nome=nome, musculo=musculo
    )
    return ApiResponse(
        message="Exercícios listados com sucesso.",
        data=Page[ExercicioRead](
            items=[ExercicioRead.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        ),
    )


@router.get("/musculos")
def list_musculos(db: DbSession) -> ApiResponse[list[str]]:
    return ApiResponse(
        message="Grupos musculares listados com sucesso.",
        data=exercicio_service.list_musculos(db),
    )
