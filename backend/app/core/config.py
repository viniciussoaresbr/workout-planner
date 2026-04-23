import os
from pathlib import Path

from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_FILE)

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:  # pragma: no cover
    from pydantic import BaseModel

    class BaseSettings(BaseModel):
        def __init__(self, **data):
            merged_data = {
                "database_url": data.get("database_url") or os.getenv("DATABASE_URL"),
                "jwt_secret_key": data.get("jwt_secret_key") or os.getenv("JWT_SECRET_KEY"),
                "jwt_algorithm": data.get("jwt_algorithm") or os.getenv("JWT_ALGORITHM", "HS256"),
                "access_token_expire_minutes": data.get("access_token_expire_minutes")
                or int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
            }
            super().__init__(**merged_data)

    def SettingsConfigDict(**kwargs):
        return kwargs


class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def resolved_database_url(self) -> str:
        if "[YOURPASSWORD]" in self.database_url:
            return "sqlite:///./workout_planner.db"
        return self.database_url


settings = Settings()
