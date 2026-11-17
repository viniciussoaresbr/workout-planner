import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import ServiceUnavailableError, register_exception_handlers
from app.core.logging import configure_logging
from app.core.request_context import REQUEST_ID_HEADER, RequestIdMiddleware
from app.db.session import engine, ping_database
from app.schemas.common import ApiResponse, HealthStatus

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    try:
        ping_database()
    except SQLAlchemyError as exc:
        # A API sobe mesmo assim; /health/ready reporta o problema.
        logger.error("Banco de dados indisponível na inicialização: %s", exc)
    yield
    engine.dispose()


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition", REQUEST_ID_HEADER],
    )
    app.add_middleware(RequestIdMiddleware)
    register_exception_handlers(app)

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/health", tags=["health"], summary="Liveness")
    def health() -> ApiResponse[HealthStatus]:
        return ApiResponse(message="API disponível.", data=HealthStatus(status="ok"))

    @app.get("/health/ready", tags=["health"], summary="Readiness (verifica o banco)")
    def readiness() -> ApiResponse[HealthStatus]:
        try:
            ping_database()
        except SQLAlchemyError as exc:
            raise ServiceUnavailableError("Banco de dados indisponível.") from exc
        return ApiResponse(message="API pronta.", data=HealthStatus(status="ok"))

    return app


app = create_app()
