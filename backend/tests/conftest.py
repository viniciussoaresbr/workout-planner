import os

# Precisa vir antes de qualquer import de `app`, pois as configurações são lidas no import.
os.environ.update(
    ENVIRONMENT="test",
    DATABASE_URL="sqlite://",
    JWT_SECRET_KEY="chave-de-teste-com-tamanho-suficiente-para-hs256",
    LOG_LEVEL="WARNING",
)

from collections.abc import Callable, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.rate_limit import ALL_LIMITERS
from app.db.base import Base
from app.db.session import build_engine, get_db
from app.main import app
from app.models import Exercicio

API = "/api/v1"


@pytest.fixture(autouse=True)
def reset_rate_limits() -> Iterator[None]:
    """Os limitadores guardam estado no processo; cada teste começa do zero."""
    for limiter in ALL_LIMITERS:
        limiter.reset()
    yield


@pytest.fixture
def engine() -> Iterator[Engine]:
    # StaticPool: todas as sessões compartilham o mesmo banco SQLite em memória.
    test_engine = build_engine("sqlite://", poolclass=StaticPool)
    Base.metadata.create_all(test_engine)
    yield test_engine
    test_engine.dispose()


@pytest.fixture
def db(engine: Engine) -> Iterator[Session]:
    with sessionmaker(bind=engine, autoflush=False)() as session:
        yield session


@pytest.fixture
def client(engine: Engine) -> Iterator[TestClient]:
    session_factory = sessionmaker(bind=engine, autoflush=False)

    def override_get_db() -> Iterator[Session]:
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def exercicios(db: Session) -> list[Exercicio]:
    items = [
        Exercicio(nome="Supino reto com barra", musculo="Peito", descricao="Peito básico"),
        Exercicio(nome="Crucifixo com halteres", musculo="Peito"),
        Exercicio(nome="Agachamento livre", musculo="Pernas"),
        Exercicio(nome="Rosca 100%_direta", musculo="Bíceps"),
    ]
    db.add_all(items)
    db.commit()
    return items


RegisterFn = Callable[..., dict[str, str]]


@pytest.fixture
def register(client: TestClient) -> RegisterFn:
    """Cadastra um usuário e devolve os headers de autenticação."""

    def _register(email: str = "ana@example.com", password: str = "senha-segura") -> dict[str, str]:
        response = client.post(
            f"{API}/auth/register", json={"name": "Ana", "email": email, "password": password}
        )
        assert response.status_code == 201, response.text
        return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}

    return _register


@pytest.fixture
def auth_headers(register: RegisterFn) -> dict[str, str]:
    return register()
