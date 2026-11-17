from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
from fastapi.testclient import TestClient

from app.core.config import settings
from tests.conftest import API, RegisterFn


def test_register_aceita_campos_do_frontend_e_retorna_token(client: TestClient) -> None:
    response = client.post(
        f"{API}/auth/register",
        json={"name": "Ana", "email": "ana@example.com", "password": "senha-segura"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["message"] == "Usuário cadastrado com sucesso."
    assert body["data"]["token_type"] == "bearer"
    assert body["data"]["access_token"]


def test_register_aceita_campos_em_portugues(client: TestClient) -> None:
    response = client.post(
        f"{API}/auth/register",
        json={"nome": "Ana", "email": "ana@example.com", "senha": "senha-segura"},
    )
    assert response.status_code == 201


def test_register_rejeita_email_duplicado_sem_diferenciar_maiusculas(
    client: TestClient, register: RegisterFn
) -> None:
    register(email="ana@example.com")

    response = client.post(
        f"{API}/auth/register",
        json={"name": "Outra", "email": "ANA@Example.com", "password": "senha-segura"},
    )

    assert response.status_code == 409
    assert response.json()["error"]["message"] == "E-mail já cadastrado."


def test_register_valida_payload(client: TestClient) -> None:
    response = client.post(
        f"{API}/auth/register", json={"name": "A", "email": "invalido", "password": "123"}
    )

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert {detail["field"] for detail in error["details"]} == {"name", "email", "password"}


def test_login_com_credenciais_validas(client: TestClient, register: RegisterFn) -> None:
    register(email="ana@example.com", password="senha-segura")

    response = client.post(
        f"{API}/auth/login", json={"email": " Ana@Example.com ", "password": "senha-segura"}
    )

    assert response.status_code == 200
    assert response.json()["data"]["access_token"]


def test_login_com_senha_errada_ou_email_inexistente(
    client: TestClient, register: RegisterFn
) -> None:
    register(email="ana@example.com", password="senha-segura")

    for email, password in [("ana@example.com", "errada"), ("ninguem@example.com", "qualquer")]:
        response = client.post(f"{API}/auth/login", json={"email": email, "password": password})
        assert response.status_code == 401
        assert response.json()["error"]["message"] == "Credenciais inválidas."
        assert response.headers["www-authenticate"] == "Bearer"


def test_me_retorna_usuario_com_nome_e_name(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.get(f"{API}/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["nome"] == data["name"] == "Ana"
    assert data["email"] == "ana@example.com"
    assert "senha_hash" not in data


def test_me_sem_token(client: TestClient) -> None:
    response = client.get(f"{API}/auth/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


def _token(**claims: object) -> str:
    return jwt.encode(claims, settings.jwt_secret_key.get_secret_value(), algorithm="HS256")


def test_me_rejeita_tokens_invalidos(client: TestClient) -> None:
    future = datetime.now(UTC) + timedelta(minutes=5)
    tokens = [
        "nao-e-um-jwt",
        _token(sub=str(uuid4()), exp=datetime.now(UTC) - timedelta(minutes=1)),  # expirado
        _token(sub="nao-e-uuid", exp=future),
        _token(exp=future),  # sem sub
        jwt.encode({"sub": str(uuid4()), "exp": future}, "outra-chave-secreta-bem-comprida-aqui"),
    ]
    for token in tokens:
        response = client.get(f"{API}/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401, token


def test_me_com_token_de_usuario_inexistente(client: TestClient) -> None:
    token = _token(sub=str(uuid4()), exp=datetime.now(UTC) + timedelta(minutes=5))

    response = client.get(f"{API}/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json()["error"]["message"] == "Usuário não encontrado."
