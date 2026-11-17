from fastapi import APIRouter, Response

from app.api.deps import CurrentUser, DbSession
from app.schemas.rotina import PlanilhaExportRequest
from app.services import planilha_service, rotina_service

router = APIRouter(prefix="/planilha", tags=["planilha"])


@router.post(
    "/export",
    response_class=Response,
    responses={200: {"content": {planilha_service.XLSX_MEDIA_TYPE: {}}}},
)
def export_planilha(
    payload: PlanilhaExportRequest, db: DbSession, current_user: CurrentUser
) -> Response:
    rotina = rotina_service.get_for_user(db, payload.rotina_id, current_user.id)
    filename = planilha_service.build_filename(rotina)
    return Response(
        content=planilha_service.build_workbook(rotina),
        media_type=planilha_service.XLSX_MEDIA_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
