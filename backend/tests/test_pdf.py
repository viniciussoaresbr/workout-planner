from io import BytesIO
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient
from pypdf import PdfReader

from app.models import Exercicio
from app.services.pdf_service import PDF_MEDIA_TYPE, build_filename, build_pdf
from tests.conftest import API, RegisterFn, criar_rotina


def _texto_do_pdf(content: bytes) -> str:
    return "\n".join(page.extract_text() for page in PdfReader(BytesIO(content)).pages)


def test_exporta_pdf_da_rotina(
    client: TestClient, auth_headers: dict[str, str], exercicios: list[Exercicio]
) -> None:
    rotina_id = criar_rotina(client, auth_headers, exercicios[0], "Treino Pé & Força")

    response = client.post(f"{API}/pdf/export", json={"rotina_id": rotina_id}, headers=auth_headers)

    assert response.status_code == 200
    assert response.headers["content-type"] == PDF_MEDIA_TYPE
    assert response.headers["content-disposition"] == (
        'attachment; filename="rotina-treino-pe-forca.pdf"'
    )
    assert PdfReader(BytesIO(response.content)).metadata.title == "Treino Pé & Força"
    texto = _texto_do_pdf(response.content)
    for esperado in (
        "Treino Pé & Força",
        "1 exercício em 1 dia",
        "Segunda",
        "Exercício",
        "Supino reto com barra",
        "Peito",
        "8-12",
    ):
        assert esperado in texto


def test_exportar_pdf_de_rotina_de_outro_usuario_retorna_404(
    client: TestClient,
    auth_headers: dict[str, str],
    exercicios: list[Exercicio],
    register: RegisterFn,
) -> None:
    rotina_id = criar_rotina(client, auth_headers, exercicios[0], "Treino A")
    outro_usuario = register(email="bruno@example.com")
    url = f"{API}/pdf/export"

    rotina_alheia = client.post(url, json={"rotina_id": rotina_id}, headers=outro_usuario)
    inexistente = client.post(url, json={"rotina_id": str(uuid4())}, headers=auth_headers)
    sem_login = client.post(url, json={"rotina_id": rotina_id})

    assert rotina_alheia.status_code == 404
    assert inexistente.status_code == 404
    assert sem_login.status_code == 401


def _rotina_fake(nome: str, *dias: tuple[str, list[str]]) -> SimpleNamespace:
    def item(exercicio: str) -> SimpleNamespace:
        return SimpleNamespace(
            exercicio=SimpleNamespace(nome=exercicio, musculo="Peito"),
            series="4",
            repeticoes="10",
        )

    return SimpleNamespace(
        nome=nome,
        dias=[SimpleNamespace(nome=dia, itens=[item(e) for e in itens]) for dia, itens in dias],
    )


def test_pdf_omite_dias_vazios_e_trata_textos_especiais() -> None:
    rotina = _rotina_fake(
        "Treino <b>A</b> 💪",
        ("Segunda", ["Supino <i>& crucifixo</i>"]),
        ("Terça", []),
    )

    texto = _texto_do_pdf(build_pdf(rotina))  # type: ignore[arg-type]

    # Marcação vira texto literal e emojis (fora das fontes padrão do PDF) são descartados.
    assert "Treino <b>A</b>" in texto
    assert "💪" not in texto
    assert "Supino <i>& crucifixo</i>" in texto
    assert "Segunda" in texto
    assert "Terça" not in texto
    assert "1 exercício em 1 dia" in texto


def test_pdf_de_rotina_sem_exercicios() -> None:
    rotina = _rotina_fake("Vazia", ("Segunda", []))

    texto = _texto_do_pdf(build_pdf(rotina))  # type: ignore[arg-type]

    assert "Esta rotina ainda não tem exercícios." in texto
    assert "0 exercícios em 0 dias" in texto


def test_nome_do_pdf_sem_caracteres_validos() -> None:
    assert build_filename(SimpleNamespace(nome="💪💪")) == "rotina-treino.pdf"  # type: ignore[arg-type]
