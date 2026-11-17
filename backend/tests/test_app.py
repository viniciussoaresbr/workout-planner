from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool, Pool, QueuePool

from app.db.session import build_engine
from app.main import app
from app.models import Exercicio
from app.seed import seed_exercicios
from app.seed.data import EXERCICIOS
from tests.conftest import API


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"message": "API disponível.", "data": {"status": "ok"}}


def test_readiness_com_banco_disponivel(client: TestClient) -> None:
    assert client.get("/health/ready").status_code == 200


def test_readiness_com_banco_indisponivel(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def falha() -> None:
        raise OperationalError("SELECT 1", {}, Exception("connection refused"))

    monkeypatch.setattr("app.main.ping_database", falha)

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "service_unavailable"


def test_request_id_e_propagado_ou_gerado(client: TestClient) -> None:
    proprio = client.get("/health", headers={"X-Request-ID": "abc-123"})
    gerado = client.get("/health", headers={"X-Request-ID": "invalido com espaco"})

    assert proprio.headers["x-request-id"] == "abc-123"
    assert gerado.headers["x-request-id"] not in ("", "invalido com espaco")


def test_rota_inexistente_usa_formato_de_erro_padrao(client: TestClient) -> None:
    response = client.get(f"{API}/nao-existe", headers={"X-Request-ID": "req-1"})

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "http_error", "message": "Not Found", "request_id": "req-1"}
    }


@pytest.fixture
def client_sem_excecoes_propagadas() -> Iterator[TestClient]:
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


def test_erro_inesperado_retorna_500_sem_vazar_detalhes(
    client_sem_excecoes_propagadas: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def explode(*_: object, **__: object) -> None:
        raise RuntimeError("segredo interno")

    monkeypatch.setattr("app.services.exercicio_service.list_musculos", explode)

    response = client_sem_excecoes_propagadas.get(f"{API}/exercicios/musculos")

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_server_error"
    assert "segredo" not in response.text


def test_seed_e_idempotente_e_atualiza_divergencias(db: Session) -> None:
    primeira = seed_exercicios(db)
    assert (primeira.inseridos, primeira.atualizados, primeira.total) == (len(EXERCICIOS), 0, 74)

    exercicio = db.scalar(select(Exercicio).where(Exercicio.nome == EXERCICIOS[0].nome))
    assert exercicio is not None
    exercicio.musculo = "Errado"
    db.commit()

    segunda = seed_exercicios(db)
    assert (segunda.inseridos, segunda.atualizados, segunda.total) == (0, 1, 74)
    db.refresh(exercicio)
    assert exercicio.musculo == EXERCICIOS[0].musculo


@pytest.mark.parametrize("poolclass", [None, NullPool])
def test_build_engine_postgres_aceita_pool_customizado(poolclass: type[Pool] | None) -> None:
    """Regressão: o Alembic usa NullPool, que não aceita pool_size/max_overflow."""
    kwargs = {"poolclass": poolclass} if poolclass else {}
    engine = build_engine("postgresql+psycopg://u:p@localhost:1/db", **kwargs)
    assert isinstance(engine.pool, poolclass or QueuePool)
    engine.dispose()
