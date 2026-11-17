import zipfile
from io import BytesIO
from uuid import uuid4

from fastapi.testclient import TestClient

from app.models import Exercicio
from app.services.planilha_service import XLSX_MEDIA_TYPE, build_filename
from tests.conftest import API, RegisterFn


def _criar_rotina(
    client: TestClient, headers: dict[str, str], exercicio: Exercicio, nome: str
) -> str:
    payload = {
        "nome": nome,
        "dias": [
            {
                "nome": "Segunda",
                "ordem": 1,
                "itens": [
                    {
                        "exercicio_id": str(exercicio.id),
                        "series": "4",
                        "repeticoes": "8-12",
                        "ordem": 1,
                    }
                ],
            }
        ],
    }
    response = client.post(f"{API}/rotinas", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()["data"]["id"]


def _textos_da_planilha(content: bytes) -> str:
    with zipfile.ZipFile(BytesIO(content)) as xlsx:
        return xlsx.read("xl/sharedStrings.xml").decode()


def test_exporta_planilha_da_rotina(
    client: TestClient, auth_headers: dict[str, str], exercicios: list[Exercicio]
) -> None:
    rotina_id = _criar_rotina(client, auth_headers, exercicios[0], "Treino Pé & Força")

    response = client.post(
        f"{API}/planilha/export", json={"rotina_id": rotina_id}, headers=auth_headers
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == XLSX_MEDIA_TYPE
    assert response.headers["content-disposition"] == (
        'attachment; filename="rotina-treino-pe-forca.xlsx"'
    )
    textos = _textos_da_planilha(response.content)
    for esperado in ("Exercício", "Segunda", "Supino reto com barra", "Peito", "8-12"):
        assert esperado in textos


def test_exportar_rotina_de_outro_usuario_retorna_404(
    client: TestClient,
    auth_headers: dict[str, str],
    exercicios: list[Exercicio],
    register: RegisterFn,
) -> None:
    rotina_id = _criar_rotina(client, auth_headers, exercicios[0], "Treino A")
    outro_usuario = register(email="bruno@example.com")
    url = f"{API}/planilha/export"

    rotina_alheia = client.post(url, json={"rotina_id": rotina_id}, headers=outro_usuario)
    inexistente = client.post(url, json={"rotina_id": str(uuid4())}, headers=auth_headers)

    assert rotina_alheia.status_code == 404
    assert inexistente.status_code == 404


def test_nome_de_arquivo_sem_caracteres_validos() -> None:
    class RotinaFake:
        nome = "💪💪"

    assert build_filename(RotinaFake()) == "rotina-treino.xlsx"  # type: ignore[arg-type]
