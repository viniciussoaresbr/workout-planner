from pydantic import BaseModel, ConfigDict


class Schema(BaseModel):
    """Base de todos os schemas: remove espaços nas pontas e lê atributos de objetos ORM."""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


class ApiResponse[T](Schema):
    """Envelope padrão das respostas de sucesso."""

    message: str
    data: T


class Page[T](Schema):
    items: list[T]
    total: int
    page: int
    page_size: int


class HealthStatus(Schema):
    status: str
