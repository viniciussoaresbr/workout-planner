from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1.router import api_router
from app.core.exceptions import register_exception_handlers
from app.db.database import Base, engine
from app.schemas.schemas import HealthcheckResponse, SuccessResponse

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
    except SQLAlchemyError as exc:  # pragma: no cover
        logger.warning("Database startup tasks skipped: %s", exc)
    yield


app = FastAPI(title="Workout Planner API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", response_model=SuccessResponse[HealthcheckResponse])
def healthcheck() -> SuccessResponse[HealthcheckResponse]:
    return SuccessResponse(message="API disponivel.", data=HealthcheckResponse(status="ok"))
