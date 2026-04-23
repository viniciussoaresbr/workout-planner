"""initial

Revision ID: 20260404_0001
Revises:
Create Date: 2026-04-04 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260404_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("senha_hash", sa.String(length=255), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_usuarios_email"), "usuarios", ["email"], unique=True)

    op.create_table(
        "exercicios",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("nome", sa.String(length=160), nullable=False),
        sa.Column("musculo", sa.String(length=120), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_exercicios_musculo"), "exercicios", ["musculo"], unique=False)
    op.create_index(op.f("ix_exercicios_nome"), "exercicios", ["nome"], unique=False)

    op.create_table(
        "rotinas",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("usuario_id", sa.UUID(), nullable=False),
        sa.Column("nome", sa.String(length=160), nullable=False),
        sa.Column("objetivo", sa.String(length=255), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "dias_rotina",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("rotina_id", sa.UUID(), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("ordem", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["rotina_id"], ["rotinas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("rotina_id", "ordem", name="uq_dias_rotina_ordem"),
    )

    op.create_table(
        "itens_rotina",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("dia_rotina_id", sa.UUID(), nullable=False),
        sa.Column("exercicio_id", sa.UUID(), nullable=False),
        sa.Column("series", sa.String(length=50), nullable=False),
        sa.Column("repeticoes", sa.String(length=50), nullable=False),
        sa.Column("descanso_segundos", sa.Integer(), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("ordem", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["dia_rotina_id"], ["dias_rotina.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["exercicio_id"], ["exercicios.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("dia_rotina_id", "ordem", name="uq_itens_rotina_ordem"),
    )


def downgrade() -> None:
    op.drop_table("itens_rotina")
    op.drop_table("dias_rotina")
    op.drop_table("rotinas")
    op.drop_index(op.f("ix_exercicios_nome"), table_name="exercicios")
    op.drop_index(op.f("ix_exercicios_musculo"), table_name="exercicios")
    op.drop_table("exercicios")
    op.drop_index(op.f("ix_usuarios_email"), table_name="usuarios")
    op.drop_table("usuarios")
