from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import DiaRotina, Exercicio, ItemRotina
from tests.conftest import API, RegisterFn


def _item(exercicio: Exercicio, ordem: int, series: str = "3", repeticoes: str = "10") -> dict:
    return {
        "exercicio_id": str(exercicio.id),
        "series": series,
        "repeticoes": repeticoes,
        "ordem": ordem,
    }


def _payload(exercicios: list[Exercicio], nome: str = "Treino A") -> dict[str, Any]:
    supino, crucifixo, agachamento, _ = exercicios
    return {
        "nome": nome,
        "dias": [
            # Enviados fora de ordem de propósito: a API deve devolver ordenado.
            {"nome": "Quarta", "ordem": 2, "itens": [_item(agachamento, 1, "5", "5")]},
            {"nome": "Segunda", "ordem": 1, "itens": [_item(crucifixo, 2), _item(supino, 1)]},
        ],
    }


@pytest.fixture
def rotina(
    client: TestClient, auth_headers: dict[str, str], exercicios: list[Exercicio]
) -> dict[str, Any]:
    response = client.post(f"{API}/rotinas", json=_payload(exercicios), headers=auth_headers)
    assert response.status_code == 201, response.text
    return response.json()["data"]


def test_cria_rotina_com_dias_e_itens_ordenados(rotina: dict[str, Any]) -> None:
    assert rotina["nome"] == "Treino A"
    assert [dia["nome"] for dia in rotina["dias"]] == ["Segunda", "Quarta"]
    segunda = rotina["dias"][0]
    assert [item["exercicio"]["nome"] for item in segunda["itens"]] == [
        "Supino reto com barra",
        "Crucifixo com halteres",
    ]
    assert segunda["itens"][0]["exercicio"]["musculo"] == "Peito"


def test_lista_apenas_rotinas_do_usuario(
    client: TestClient,
    rotina: dict[str, Any],
    register: RegisterFn,
) -> None:
    outro_usuario = register(email="bruno@example.com")

    assert client.get(f"{API}/rotinas", headers=outro_usuario).json()["data"] == []


def test_busca_rotina_por_id(
    client: TestClient, auth_headers: dict[str, str], rotina: dict[str, Any]
) -> None:
    response = client.get(f"{API}/rotinas/{rotina['id']}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["data"] == rotina


def test_rotina_de_outro_usuario_retorna_404(
    client: TestClient, rotina: dict[str, Any], register: RegisterFn
) -> None:
    outro_usuario = register(email="bruno@example.com")
    url = f"{API}/rotinas/{rotina['id']}"

    assert client.get(url, headers=outro_usuario).status_code == 404
    assert client.put(url, json={"nome": "Hack"}, headers=outro_usuario).status_code == 404
    assert client.delete(url, headers=outro_usuario).status_code == 404


def test_atualizacao_substitui_dias_varias_vezes(
    client: TestClient,
    auth_headers: dict[str, str],
    rotina: dict[str, Any],
    exercicios: list[Exercicio],
    db: Session,
) -> None:
    """Regressão: substituir dias com a mesma `ordem` não pode violar a constraint única."""
    url = f"{API}/rotinas/{rotina['id']}"
    supino = exercicios[0]

    for series in ("4", "5"):
        payload = {
            "nome": "Treino A Ajustado",
            "dias": [{"nome": "Segunda", "ordem": 1, "itens": [_item(supino, 1, series, "12")]}],
        }
        response = client.put(url, json=payload, headers=auth_headers)
        assert response.status_code == 200, response.text

    data = response.json()["data"]
    assert data["nome"] == "Treino A Ajustado"
    assert len(data["dias"]) == 1
    assert data["dias"][0]["itens"][0]["series"] == "5"
    assert data["atualizado_em"] >= rotina["atualizado_em"]
    # Dias e itens antigos foram removidos de fato (sem órfãos).
    assert db.scalar(select(func.count(DiaRotina.id))) == 1
    assert db.scalar(select(func.count(ItemRotina.id))) == 1


def test_atualizacao_parcial_mantem_dias(
    client: TestClient, auth_headers: dict[str, str], rotina: dict[str, Any]
) -> None:
    response = client.put(
        f"{API}/rotinas/{rotina['id']}", json={"nome": "Só o nome"}, headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["data"]["nome"] == "Só o nome"
    assert response.json()["data"]["dias"] == rotina["dias"]


def test_remove_rotina_em_cascata(
    client: TestClient, auth_headers: dict[str, str], rotina: dict[str, Any], db: Session
) -> None:
    url = f"{API}/rotinas/{rotina['id']}"

    response = client.delete(url, headers=auth_headers)

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(url, headers=auth_headers).status_code == 404
    assert db.scalar(select(func.count(DiaRotina.id))) == 0
    assert db.scalar(select(func.count(ItemRotina.id))) == 0


def test_exercicio_inexistente_retorna_400(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    inexistente = str(uuid4())
    payload = {
        "nome": "Treino",
        "dias": [
            {
                "nome": "Segunda",
                "ordem": 1,
                "itens": [
                    {"exercicio_id": inexistente, "series": "3", "repeticoes": "10", "ordem": 1}
                ],
            }
        ],
    }

    response = client.post(f"{API}/rotinas", json=payload, headers=auth_headers)

    assert response.status_code == 400
    assert response.json()["error"]["details"] == {"exercicio_ids": [inexistente]}


@pytest.mark.parametrize("nivel", ["dias", "itens"])
def test_ordem_duplicada_retorna_422(
    client: TestClient,
    auth_headers: dict[str, str],
    exercicios: list[Exercicio],
    nivel: str,
) -> None:
    payload = _payload(exercicios)
    if nivel == "dias":
        payload["dias"][1]["ordem"] = 2
    else:
        payload["dias"][1]["itens"][0]["ordem"] = 1

    response = client.post(f"{API}/rotinas", json=payload, headers=auth_headers)

    assert response.status_code == 422
    assert "ordem única" in response.json()["error"]["details"][0]["message"]


def test_rotas_de_rotina_exigem_autenticacao(client: TestClient) -> None:
    assert client.get(f"{API}/rotinas").status_code == 401
    assert client.post(f"{API}/rotinas", json={"nome": "X"}).status_code == 401


def test_id_invalido_retorna_422(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.get(f"{API}/rotinas/nao-e-uuid", headers=auth_headers)

    assert response.status_code == 422
