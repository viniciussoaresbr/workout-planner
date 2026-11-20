from fastapi import APIRouter

from app.api.v1.endpoints import auth, exercicios, pdf, planilha, rotinas

api_router = APIRouter()
for module in (auth, exercicios, rotinas, planilha, pdf):
    api_router.include_router(module.router)
