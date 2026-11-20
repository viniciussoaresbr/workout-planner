from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]

# Valores de exemplo já publicados no repositório (atual e versões anteriores do .env.example).
_PLACEHOLDER_SECRETS = frozenset(
    {
        "troque-por-um-valor-aleatorio-com-pelo-menos-32-caracteres",
        "troque-esta-chave-por-um-valor-seguro",
    }
)


class Settings(BaseSettings):
    """Configuração da aplicação carregada de variáveis de ambiente e do arquivo .env."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Workout Planner API"
    app_version: str = "2.0.0"
    environment: Literal["development", "test", "production"] = "development"
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"

    database_url: str
    database_echo: bool = False

    jwt_secret_key: SecretStr = Field(min_length=32)
    jwt_algorithm: Literal["HS256", "HS384", "HS512"] = "HS256"
    access_token_expire_minutes: int = Field(default=60, gt=0)

    cors_origins: list[str] = ["http://localhost:4200"]

    # Limites contra força bruta e abuso do hash de senha (contados por processo).
    login_rate_limit_per_minute: int = Field(default=20, gt=0)
    # Falhas por e-mail vindas de um mesmo IP a cada 15 min. Bloqueia só aquele IP, para que
    # um atacante não consiga trancar a conta do dono.
    login_failure_limit: int = Field(default=10, gt=0)
    # Falhas por e-mail somando todos os IPs a cada hora (força bruta distribuída). Um único
    # IP fica limitado a ~4x `login_failure_limit` por hora, então bloquear uma conta exige
    # vários IPs atacando ao mesmo tempo.
    login_account_failure_limit: int = Field(default=100, gt=0)
    register_rate_limit_per_hour: int = Field(default=10, gt=0)
    # Cada hash Argon2 usa ~64 MiB; limita quantos rodam ao mesmo tempo.
    password_hash_concurrency: int = Field(default=4, gt=0)

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def docs_enabled(self) -> bool:
        """Swagger/ReDoc/OpenAPI ficam desativados em produção."""
        return not self.is_production

    @model_validator(mode="after")
    def require_https_origins_in_production(self) -> "Settings":
        """Em produção o frontend precisa ser servido por HTTPS: senha e token não podem
        trafegar em texto puro."""
        if self.is_production:
            inseguras = [
                origin for origin in self.cors_origins if not origin.startswith("https://")
            ]
            if inseguras:
                raise ValueError(
                    f"Em produção, CORS_ORIGINS só aceita origens https:// (recebido: {inseguras})."
                )
        return self

    @field_validator("jwt_secret_key")
    @classmethod
    def reject_placeholder_secret(cls, value: SecretStr) -> SecretStr:
        """Impede subir a API com o valor de exemplo (público) como chave de assinatura."""
        secret = value.get_secret_value()
        if secret in _PLACEHOLDER_SECRETS or secret.lower().startswith("troque"):
            raise ValueError(
                "JWT_SECRET_KEY ainda é o valor de exemplo. Gere um novo com: "
                'python -c "import secrets; print(secrets.token_urlsafe(48))"'
            )
        if len(set(secret)) < 10:
            raise ValueError("JWT_SECRET_KEY tem pouca variação de caracteres; gere um aleatório.")
        return value

    @field_validator("database_url")
    @classmethod
    def use_psycopg_driver(cls, value: str) -> str:
        """Aceita URLs no formato padrão do PostgreSQL e força o driver psycopg 3."""
        for prefix in ("postgres://", "postgresql://"):
            if value.startswith(prefix):
                return "postgresql+psycopg://" + value.removeprefix(prefix)
        return value

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]  # valores obrigatórios vêm do ambiente


settings = get_settings()
