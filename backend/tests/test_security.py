"""Proteções de segurança: chave JWT, limites de tentativas, docs em produção, CORS e
cabeçalhos HTTP."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app import main
from app.core.config import Settings
from app.core.exceptions import TooManyRequestsError
from app.core.rate_limit import (
    RateLimiter,
    login_account_limiter,
    login_failure_limiter,
    login_ip_limiter,
    register_ip_limiter,
)
from tests.conftest import API, RegisterFn

# ---- Chave JWT ----


@pytest.mark.parametrize(
    "secret",
    [
        "troque-por-um-valor-aleatorio-com-pelo-menos-32-caracteres",  # .env.example atual
        "troque-esta-chave-por-um-valor-seguro-e-bem-mais-longo",
        "a" * 40,
        "abababababababababababababababababab",
    ],
)
def test_settings_rejeita_chave_jwt_de_exemplo_ou_fraca(secret: str) -> None:
    with pytest.raises(ValidationError, match="JWT_SECRET_KEY"):
        Settings(database_url="sqlite://", jwt_secret_key=secret)


_CHAVE_VALIDA = "Zq3-vN8_kP1xR7tY0uW5sL2mC9bH4jG6"


def test_settings_aceita_chave_jwt_aleatoria() -> None:
    settings = Settings(database_url="sqlite://", jwt_secret_key=_CHAVE_VALIDA)
    assert settings.jwt_secret_key.get_secret_value().startswith("Zq3")


# ---- HTTPS em produção ----


def test_producao_exige_origens_cors_https() -> None:
    with pytest.raises(ValidationError, match="https://"):
        Settings(
            database_url="sqlite://",
            jwt_secret_key=_CHAVE_VALIDA,
            environment="production",
            cors_origins=["https://treino.example.com", "http://treino.example.com"],
        )


def test_producao_aceita_origens_https_e_dev_aceita_http() -> None:
    Settings(
        database_url="sqlite://",
        jwt_secret_key=_CHAVE_VALIDA,
        environment="production",
        cors_origins=["https://treino.example.com"],
    )
    Settings(database_url="sqlite://", jwt_secret_key=_CHAVE_VALIDA)  # http://localhost:4200


# ---- RateLimiter ----


class FakeClock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def test_rate_limiter_bloqueia_apos_o_limite_e_libera_na_proxima_janela() -> None:
    clock = FakeClock()
    limiter = RateLimiter(2, window_seconds=60, clock=clock)

    limiter.hit("ip")
    limiter.hit("ip")
    clock.now += 15
    with pytest.raises(TooManyRequestsError) as exc_info:
        limiter.hit("ip")
    assert exc_info.value.headers == {"Retry-After": "45"}

    limiter.hit("outro-ip")  # chaves são independentes
    clock.now += 45
    limiter.hit("ip")  # nova janela


def test_rate_limiter_check_nao_conta_e_clear_zera() -> None:
    limiter = RateLimiter(1, window_seconds=60, clock=FakeClock())

    limiter.check("k")
    limiter.check("k")
    limiter.add("k")
    with pytest.raises(TooManyRequestsError):
        limiter.check("k")

    limiter.clear("k")
    limiter.check("k")


def test_rate_limiter_mantem_memoria_limitada() -> None:
    clock = FakeClock()
    limiter = RateLimiter(5, window_seconds=60, max_keys=3, clock=clock)

    for key in ("a", "b", "c", "d"):
        limiter.add(key)
    assert list(limiter._windows) == ["b", "c", "d"]  # a mais antiga saiu

    clock.now += 60  # todas expiram
    limiter.add("e")
    assert list(limiter._windows) == ["e"]


# ---- Limites nas rotas de autenticação ----


def _login(client: TestClient, email: str, password: str) -> int:
    response = client.post(f"{API}/auth/login", json={"email": email, "password": password})
    return response.status_code


@pytest.fixture
def outro_ip(client: TestClient) -> Iterator[TestClient]:
    """Cliente vindo de outro IP, usando o mesmo banco de teste do fixture `client`."""
    with TestClient(main.app, client=("203.0.113.7", 50000)) as other:
        yield other


def test_login_limitado_por_ip(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(login_ip_limiter, "limit", 2)

    assert _login(client, "a@example.com", "x") == 401
    assert _login(client, "b@example.com", "x") == 401

    response = client.post(f"{API}/auth/login", json={"email": "c@example.com", "password": "x"})
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "too_many_requests"
    assert int(response.headers["retry-after"]) > 0


def test_login_bloqueia_o_ip_que_errou_mesmo_com_senha_correta(
    client: TestClient, register: RegisterFn, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(login_failure_limiter, "limit", 2)
    register(email="ana@example.com", password="senha-segura")

    assert _login(client, "ana@example.com", "errada") == 401
    assert _login(client, "ANA@example.com", "errada") == 401
    assert _login(client, "ana@example.com", "senha-segura") == 429
    # Outras contas não são afetadas.
    assert _login(client, "bia@example.com", "qualquer") == 401


def test_atacante_nao_tranca_a_conta_do_dono(
    client: TestClient,
    outro_ip: TestClient,
    register: RegisterFn,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Falhas de um IP não impedem o dono da conta de entrar a partir de outro IP."""
    monkeypatch.setattr(login_failure_limiter, "limit", 2)
    register(email="ana@example.com", password="senha-segura")

    assert _login(client, "ana@example.com", "errada") == 401
    assert _login(client, "ana@example.com", "errada") == 401
    assert _login(client, "ana@example.com", "errada") == 429

    assert _login(outro_ip, "ana@example.com", "senha-segura") == 200


def test_login_bloqueia_conta_sob_forca_bruta_distribuida(
    client: TestClient,
    outro_ip: TestClient,
    register: RegisterFn,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(login_failure_limiter, "limit", 10)
    monkeypatch.setattr(login_account_limiter, "limit", 3)
    register(email="ana@example.com", password="senha-segura")

    assert _login(client, "ana@example.com", "errada") == 401
    assert _login(outro_ip, "ana@example.com", "errada") == 401
    assert _login(client, "ana@example.com", "errada") == 401
    # Somando os IPs, a conta atingiu o limite: nenhum IP entra até a janela expirar.
    assert _login(outro_ip, "ana@example.com", "senha-segura") == 429
    assert _login(client, "bia@example.com", "qualquer") == 401


def test_login_bloqueia_email_inexistente_do_mesmo_jeito(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Sem diferença de comportamento, o bloqueio não revela quais e-mails estão cadastrados."""
    monkeypatch.setattr(login_failure_limiter, "limit", 1)

    assert _login(client, "ninguem@example.com", "x") == 401
    assert _login(client, "ninguem@example.com", "x") == 429


def test_login_com_sucesso_zera_falhas(
    client: TestClient, register: RegisterFn, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(login_failure_limiter, "limit", 2)
    register(email="ana@example.com", password="senha-segura")

    assert _login(client, "ana@example.com", "errada") == 401
    assert _login(client, "ana@example.com", "senha-segura") == 200
    assert _login(client, "ana@example.com", "errada") == 401
    assert _login(client, "ana@example.com", "senha-segura") == 200


def test_register_limitado_por_ip(
    client: TestClient, register: RegisterFn, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(register_ip_limiter, "limit", 1)
    register(email="ana@example.com")

    response = client.post(
        f"{API}/auth/register",
        json={"name": "Bia", "email": "bia@example.com", "password": "senha-segura"},
    )
    assert response.status_code == 429


def test_register_exige_senha_com_8_caracteres(client: TestClient) -> None:
    response = client.post(
        f"{API}/auth/register",
        json={"name": "Ana", "email": "ana@example.com", "password": "1234567"},
    )
    assert response.status_code == 422


# ---- Documentação e CORS ----


def test_docs_disponiveis_fora_de_producao(client: TestClient) -> None:
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_docs_desativadas_em_producao(monkeypatch: pytest.MonkeyPatch) -> None:
    production = main.settings.model_copy(update={"environment": "production"})
    monkeypatch.setattr(main, "settings", production)

    with TestClient(main.create_app()) as client:
        for path in ("/docs", "/redoc", "/openapi.json"):
            assert client.get(path).status_code == 404, path
        assert client.get("/health").status_code == 200


def test_cors_nao_libera_credenciais(client: TestClient) -> None:
    response = client.options(
        f"{API}/rotinas",
        headers={
            "Origin": "http://localhost:4200",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:4200"
    assert "access-control-allow-credentials" not in response.headers


# ---- Cabeçalhos de segurança ----


def test_respostas_da_api_trazem_cabecalhos_de_seguranca(client: TestClient) -> None:
    for response in (client.get("/health"), client.get(f"{API}/auth/me")):  # 200 e 401
        headers = response.headers
        assert headers["x-content-type-options"] == "nosniff"
        assert headers["x-frame-options"] == "DENY"
        assert headers["referrer-policy"] == "no-referrer"
        assert "default-src 'none'" in headers["content-security-policy"]
        assert "frame-ancestors 'none'" in headers["content-security-policy"]
        # HSTS só é enviado em produção.
        assert "strict-transport-security" not in headers


def test_swagger_fica_fora_da_csp_restritiva(client: TestClient) -> None:
    response = client.get("/docs")

    assert response.status_code == 200
    assert "content-security-policy" not in response.headers
    assert response.headers["x-content-type-options"] == "nosniff"


def test_producao_envia_hsts(monkeypatch: pytest.MonkeyPatch) -> None:
    production = main.settings.model_copy(update={"environment": "production"})
    monkeypatch.setattr(main, "settings", production)

    with TestClient(main.create_app()) as client:
        response = client.get("/health")

    assert response.headers["strict-transport-security"].startswith("max-age=63072000")
    assert "default-src 'none'" in response.headers["content-security-policy"]
