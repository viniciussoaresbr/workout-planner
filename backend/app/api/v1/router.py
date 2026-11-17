from fastapi import APIRouter

from app.api.v1.endpoints import auth, exercicios, planilha, rotinas

api_router = APIRouter()
for module in (auth, exercicios, rotinas, planilha):
    api_router.include_router(module.router)
