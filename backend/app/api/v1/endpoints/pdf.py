from fastapi import APIRouter, Response

from app.api.deps import CurrentUser, DbSession
from app.schemas.rotina import RotinaExportRequest
from app.services import exportacao, pdf_service, rotina_service

router = APIRouter(prefix="/pdf", tags=["pdf"])


@router.post(
    "/export",
    response_class=Response,
    responses={200: {"content": {pdf_service.PDF_MEDIA_TYPE: {}}}},
)
def export_pdf(payload: RotinaExportRequest, db: DbSession, current_user: CurrentUser) -> Response:
    rotina = rotina_service.get_for_user(db, payload.rotina_id, current_user.id)
    return Response(
        content=pdf_service.build_pdf(rotina),
        media_type=pdf_service.PDF_MEDIA_TYPE,
        headers={
            "Content-Disposition": exportacao.content_disposition(
                pdf_service.build_filename(rotina)
            )
        },
    )
