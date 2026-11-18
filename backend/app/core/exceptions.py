"""Erros de domínio e tradução de exceções para o formato de erro padrão da API.

Toda resposta de erro segue o formato:
    {"error": {"code": str, "message": str, "request_id": str, "details"?: any}}
"""

import logging
from typing import Any, ClassVar

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.request_context import get_request_id

logger = logging.getLogger(__name__)


class AppError(Exception):
    status_code: ClassVar[int] = status.HTTP_500_INTERNAL_SERVER_ERROR
    code: ClassVar[str] = "internal_server_error"
    default_message: ClassVar[str] = "Ocorreu um erro interno inesperado."
    default_headers: ClassVar[dict[str, str] | None] = None

    def __init__(
        self,
        message: str | None = None,
        *,
        details: Any = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.message = message or self.default_message
        self.details = details
        self.headers = headers if headers is not None else self.default_headers
        super().__init__(self.message)


class BadRequestError(AppError):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "bad_request"
    default_message = "A requisição enviada é inválida."


class AuthenticationError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "unauthorized"
    default_message = "Não autenticado."
    default_headers: ClassVar[dict[str, str] | None] = {"WWW-Authenticate": "Bearer"}


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"
    default_message = "Recurso não encontrado."


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT
    code = "conflict"
    default_message = "O recurso entrou em conflito com outro registro."


class TooManyRequestsError(AppError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    code = "too_many_requests"
    default_message = "Muitas tentativas. Aguarde um pouco e tente novamente."

    def __init__(self, message: str | None = None, *, retry_after: int) -> None:
        super().__init__(
            message, details={"retry_after": retry_after}, headers={"Retry-After": str(retry_after)}
        )


class ServiceUnavailableError(AppError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = "service_unavailable"
    default_message = "Serviço temporariamente indisponível."


def error_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    message: str,
    details: Any = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    error: dict[str, Any] = {
        "code": code,
        "message": message,
        "request_id": get_request_id(request),
    }
    if details is not None:
        error["details"] = details
    return JSONResponse(status_code=status_code, content={"error": error}, headers=headers)


async def _app_error_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, AppError)
    return error_response(
        request,
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        details=exc.details,
        headers=exc.headers,
    )


async def _http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, StarletteHTTPException)
    detail = exc.detail
    return error_response(
        request,
        status_code=exc.status_code,
        code="http_error",
        message=detail if isinstance(detail, str) else "Não foi possível processar a solicitação.",
        details=detail if isinstance(detail, dict | list) else None,
        headers=exc.headers,
    )


async def _validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    details = [
        {
            "field": ".".join(str(part) for part in error["loc"] if part != "body"),
            "message": error["msg"],
            "type": error["type"],
        }
        for error in exc.errors()
    ]
    return error_response(
        request,
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        code="validation_error",
        message="Os dados enviados são inválidos.",
        details=details,
    )


async def _integrity_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.warning("Violação de integridade [%s]: %s", get_request_id(request), exc)
    return error_response(
        request,
        status_code=status.HTTP_409_CONFLICT,
        code="integrity_error",
        message="Não foi possível concluir a operação devido a um conflito de dados.",
    )


async def _database_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Erro de banco de dados [%s]", get_request_id(request), exc_info=exc)
    return error_response(
        request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="database_error",
        message="Ocorreu um erro ao acessar o banco de dados.",
    )


async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Erro não tratado [%s]", get_request_id(request), exc_info=exc)
    return error_response(
        request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code=AppError.code,
        message=AppError.default_message,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, _app_error_handler)
    app.add_exception_handler(StarletteHTTPException, _http_exception_handler)
    app.add_exception_handler(RequestValidationError, _validation_exception_handler)
    app.add_exception_handler(IntegrityError, _integrity_error_handler)
    app.add_exception_handler(SQLAlchemyError, _database_error_handler)
    app.add_exception_handler(Exception, _unhandled_exception_handler)
