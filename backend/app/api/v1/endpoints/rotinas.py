from uuid import UUID

from fastapi import APIRouter, Response, status

from app.api.deps import CurrentUser, DbSession
from app.schemas.common import ApiResponse
from app.schemas.rotina import RotinaCreate, RotinaRead, RotinaUpdate
from app.services import rotina_service

router = APIRouter(prefix="/rotinas", tags=["rotinas"])


@router.get("")
def list_rotinas(db: DbSession, current_user: CurrentUser) -> ApiResponse[list[RotinaRead]]:
    rotinas = rotina_service.list_for_user(db, current_user.id)
    return ApiResponse(
        message="Rotinas listadas com sucesso.",
        data=[RotinaRead.model_validate(rotina) for rotina in rotinas],
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_rotina(
    payload: RotinaCreate, db: DbSession, current_user: CurrentUser
) -> ApiResponse[RotinaRead]:
    rotina = rotina_service.create(db, current_user.id, payload)
    return ApiResponse(message="Rotina criada com sucesso.", data=RotinaRead.model_validate(rotina))


@router.get("/{rotina_id}")
def get_rotina(
    rotina_id: UUID, db: DbSession, current_user: CurrentUser
) -> ApiResponse[RotinaRead]:
    rotina = rotina_service.get_for_user(db, rotina_id, current_user.id)
    return ApiResponse(
        message="Rotina carregada com sucesso.", data=RotinaRead.model_validate(rotina)
    )


@router.put("/{rotina_id}")
def update_rotina(
    rotina_id: UUID, payload: RotinaUpdate, db: DbSession, current_user: CurrentUser
) -> ApiResponse[RotinaRead]:
    rotina = rotina_service.update(db, rotina_id, current_user.id, payload)
    return ApiResponse(
        message="Rotina atualizada com sucesso.", data=RotinaRead.model_validate(rotina)
    )


@router.delete("/{rotina_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rotina(rotina_id: UUID, db: DbSession, current_user: CurrentUser) -> Response:
    rotina_service.delete(db, rotina_id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
