from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

logger = logging.getLogger(__name__)


def _build_error_response(
    *,
    code: str,
    message: str,
    request_id: str,
    details: object | None = None,
    status_code: int,
) -> JSONResponse:
    payload: dict[str, object] = {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
        }
    }
    if details is not None:
        payload["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=payload)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        request_id = str(uuid4())
        details = exc.detail if isinstance(exc.detail, (dict, list)) else None
        message = exc.detail if isinstance(exc.detail, str) else "Nao foi possivel processar a solicitacao."
        return _build_error_response(
            code="http_error",
            message=message,
            details=details,
            request_id=request_id,
            status_code=exc.status_code,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        request_id = str(uuid4())
        details = [
            {
                "field": ".".join(str(item) for item in error["loc"] if item != "body"),
                "message": error["msg"],
                "type": error["type"],
            }
            for error in exc.errors()
        ]
        return _build_error_response(
            code="validation_error",
            message="Os dados enviados sao invalidos.",
            details=details,
            request_id=request_id,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @app.exception_handler(IntegrityError)
    async def integrity_exception_handler(_: Request, exc: IntegrityError) -> JSONResponse:
        request_id = str(uuid4())
        logger.exception("Integrity error [%s]: %s", request_id, exc)
        return _build_error_response(
            code="integrity_error",
            message="Nao foi possivel concluir a operacao devido a conflito de dados.",
            request_id=request_id,
            status_code=status.HTTP_409_CONFLICT,
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(_: Request, exc: SQLAlchemyError) -> JSONResponse:
        request_id = str(uuid4())
        logger.exception("Database error [%s]: %s", request_id, exc)
        return _build_error_response(
            code="database_error",
            message="Ocorreu um erro ao acessar o banco de dados.",
            request_id=request_id,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        request_id = str(uuid4())
        logger.exception("Unhandled error [%s]: %s", request_id, exc)
        return _build_error_response(
            code="internal_server_error",
            message="Ocorreu um erro interno inesperado.",
            request_id=request_id,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
