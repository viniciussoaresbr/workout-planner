from fastapi import APIRouter

from app.api.v1.endpoints import auth, exercicios, planilha, rotinas

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(exercicios.router, prefix="/exercicios")
api_router.include_router(rotinas.router, prefix="/rotinas")
api_router.include_router(planilha.router, prefix="/planilha")
