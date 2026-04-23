import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    rotinas: Mapped[list["Rotina"]] = relationship(back_populates="usuario", cascade="all, delete-orphan")


class Exercicio(Base):
    __tablename__ = "exercicios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    musculo: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    descricao: Mapped[str | None] = mapped_column(Text(), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    itens_rotina: Mapped[list["ItemRotina"]] = relationship(back_populates="exercicio")


class Rotina(Base):
    __tablename__ = "rotinas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"))
    nome: Mapped[str] = mapped_column(String(160), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="rotinas")
    dias: Mapped[list["DiaRotina"]] = relationship(back_populates="rotina", cascade="all, delete-orphan")


class DiaRotina(Base):
    __tablename__ = "dias_rotina"
    __table_args__ = (UniqueConstraint("rotina_id", "ordem", name="uq_dias_rotina_ordem"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rotina_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("rotinas.id", ondelete="CASCADE"))
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False)

    rotina: Mapped["Rotina"] = relationship(back_populates="dias")
    itens: Mapped[list["ItemRotina"]] = relationship(back_populates="dia", cascade="all, delete-orphan")


class ItemRotina(Base):
    __tablename__ = "itens_rotina"
    __table_args__ = (UniqueConstraint("dia_rotina_id", "ordem", name="uq_itens_rotina_ordem"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dia_rotina_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("dias_rotina.id", ondelete="CASCADE"))
    exercicio_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("exercicios.id", ondelete="RESTRICT"))
    series: Mapped[str] = mapped_column(String(50), nullable=False)
    repeticoes: Mapped[str] = mapped_column(String(50), nullable=False)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False)

    dia: Mapped["DiaRotina"] = relationship(back_populates="itens")
    exercicio: Mapped["Exercicio"] = relationship(back_populates="itens_rotina")
