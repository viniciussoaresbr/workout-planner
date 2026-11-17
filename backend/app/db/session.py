from collections.abc import Iterator
from typing import Any

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


def build_engine(database_url: str, *, echo: bool = False, **kwargs: Any) -> Engine:
    if database_url.startswith("sqlite"):
        sqlite_engine = create_engine(
            database_url, echo=echo, connect_args={"check_same_thread": False}, **kwargs
        )
        event.listen(sqlite_engine, "connect", _enable_sqlite_foreign_keys)
        return sqlite_engine
    kwargs.setdefault("pool_pre_ping", True)
    if "poolclass" not in kwargs:  # dimensionamento só se aplica ao QueuePool padrão
        kwargs.setdefault("pool_size", 10)
        kwargs.setdefault("max_overflow", 20)
    return create_engine(database_url, echo=echo, **kwargs)


def _enable_sqlite_foreign_keys(dbapi_connection: Any, _: Any) -> None:
    """SQLite ignora FKs (e ON DELETE CASCADE) a menos que isso seja ativado por conexão."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


engine = build_engine(settings.database_url, echo=settings.database_echo)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


def get_db() -> Iterator[Session]:
    """Fornece uma sessão por requisição; alterações não confirmadas são descartadas."""
    with SessionLocal() as session:
        yield session


def ping_database(db_engine: Engine = engine) -> None:
    with db_engine.connect() as connection:
        connection.execute(text("SELECT 1"))
