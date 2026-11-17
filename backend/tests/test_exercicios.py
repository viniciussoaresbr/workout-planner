import pytest
from fastapi.testclient import TestClient

from app.models import Exercicio
from tests.conftest import API

pytestmark = pytest.mark.usefixtures("exercicios")


def _nomes(response_json: dict) -> list[str]:
    return [item["nome"] for item in response_json["data"]["items"]]


def test_lista_paginada_e_ordenada_por_nome(client: TestClient) -> None:
    primeira = client.get(f"{API}/exercicios", params={"page": 1, "page_size": 3})
    segunda = client.get(f"{API}/exercicios", params={"page": 2, "page_size": 3})

    assert primeira.status_code == 200
    assert _nomes(primeira.json()) == [
        "Agachamento livre",
        "Crucifixo com halteres",
        "Rosca 100%_direta",
    ]
    assert _nomes(segunda.json()) == ["Supino reto com barra"]
    assert primeira.json()["data"] | {"items": None} == {
        "items": None,
        "total": 4,
        "page": 1,
        "page_size": 3,
    }


def test_rota_sem_e_com_barra_final_funcionam(client: TestClient) -> None:
    assert client.get(f"{API}/exercicios", follow_redirects=False).status_code == 200
    assert client.get(f"{API}/exercicios/").status_code == 200


def test_filtro_por_nome_parcial_sem_diferenciar_maiusculas(client: TestClient) -> None:
    response = client.get(f"{API}/exercicios", params={"nome": "  SUPINO "})

    assert _nomes(response.json()) == ["Supino reto com barra"]
    assert response.json()["data"]["total"] == 1


def test_filtro_por_nome_trata_curingas_como_texto(client: TestClient) -> None:
    assert _nomes(client.get(f"{API}/exercicios", params={"nome": "%"}).json()) == [
        "Rosca 100%_direta"
    ]
    assert _nomes(client.get(f"{API}/exercicios", params={"nome": "_"}).json()) == [
        "Rosca 100%_direta"
    ]


def test_filtro_por_musculo_exato(client: TestClient) -> None:
    response = client.get(f"{API}/exercicios", params={"musculo": "peito"})

    assert _nomes(response.json()) == ["Crucifixo com halteres", "Supino reto com barra"]


def test_page_size_maximo(client: TestClient) -> None:
    response = client.get(f"{API}/exercicios", params={"page_size": 101})

    assert response.status_code == 422


def test_lista_musculos_distintos(client: TestClient) -> None:
    response = client.get(f"{API}/exercicios/musculos")

    assert response.json()["data"] == ["Bíceps", "Peito", "Pernas"]


def test_resposta_expoe_campos_do_exercicio(
    client: TestClient, exercicios: list[Exercicio]
) -> None:
    item = client.get(f"{API}/exercicios", params={"nome": "Supino"}).json()["data"]["items"][0]

    assert item["id"] == str(exercicios[0].id)
    assert item["descricao"] == "Peito básico"
    assert set(item) == {"id", "nome", "musculo", "descricao", "criado_em"}
