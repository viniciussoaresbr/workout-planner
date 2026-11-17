from datetime import datetime
from uuid import UUID

from app.schemas.common import Schema


class ExercicioRead(Schema):
    id: UUID
    nome: str
    musculo: str
    descricao: str | None
    criado_em: datetime
