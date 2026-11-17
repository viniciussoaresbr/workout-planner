import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.exercicio import Exercicio

if TYPE_CHECKING:
    from app.models.usuario import Usuario


class Rotina(Base):
    __tablename__ = "rotinas"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    usuario_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), index=True
    )
    nome: Mapped[str] = mapped_column(String(160))
    criado_em: Mapped[datetime] = mapped_column(server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    usuario: Mapped["Usuario"] = relationship(back_populates="rotinas")
    dias: Mapped[list["DiaRotina"]] = relationship(
        back_populates="rotina",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="DiaRotina.ordem",
    )


class DiaRotina(Base):
    __tablename__ = "dias_rotina"
    __table_args__ = (UniqueConstraint("rotina_id", "ordem"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    rotina_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rotinas.id", ondelete="CASCADE"))
    nome: Mapped[str] = mapped_column(String(120))
    ordem: Mapped[int]

    rotina: Mapped[Rotina] = relationship(back_populates="dias")
    itens: Mapped[list["ItemRotina"]] = relationship(
        back_populates="dia",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="ItemRotina.ordem",
    )


class ItemRotina(Base):
    __tablename__ = "itens_rotina"
    __table_args__ = (UniqueConstraint("dia_rotina_id", "ordem"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dia_rotina_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("dias_rotina.id", ondelete="CASCADE")
    )
    exercicio_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("exercicios.id", ondelete="RESTRICT"), index=True
    )
    series: Mapped[str] = mapped_column(String(50))
    repeticoes: Mapped[str] = mapped_column(String(50))
    ordem: Mapped[int]

    dia: Mapped[DiaRotina] = relationship(back_populates="itens")
    exercicio: Mapped[Exercicio] = relationship()
