"""initial schema

Consolida as migrations anteriores (cuja cadeia estava quebrada: a revisão
`ea912a878dad` dependia de `99f47ff69e56`, que não existia no repositório).

Revision ID: 0001
Revises:
Create Date: 2026-11-17
"""

import sqlalchemy as sa

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def _timestamp(name: str) -> sa.Column:
    return sa.Column(name, sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("senha_hash", sa.String(length=255), nullable=False),
        _timestamp("criado_em"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_usuarios")),
        sa.UniqueConstraint("email", name=op.f("uq_usuarios_email")),
    )

    op.create_table(
        "exercicios",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(length=160), nullable=False),
        sa.Column("musculo", sa.String(length=120), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        _timestamp("criado_em"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_exercicios")),
        sa.UniqueConstraint("nome", name=op.f("uq_exercicios_nome")),
    )
    op.create_index(op.f("ix_exercicios_musculo"), "exercicios", ["musculo"])

    op.create_table(
        "rotinas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(length=160), nullable=False),
        _timestamp("criado_em"),
        _timestamp("atualizado_em"),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuarios.id"],
            name=op.f("fk_rotinas_usuario_id_usuarios"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_rotinas")),
    )
    op.create_index(op.f("ix_rotinas_usuario_id"), "rotinas", ["usuario_id"])

    op.create_table(
        "dias_rotina",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("rotina_id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("ordem", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["rotina_id"],
            ["rotinas.id"],
            name=op.f("fk_dias_rotina_rotina_id_rotinas"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_dias_rotina")),
        sa.UniqueConstraint("rotina_id", "ordem", name=op.f("uq_dias_rotina_rotina_id_ordem")),
    )

    op.create_table(
        "itens_rotina",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("dia_rotina_id", sa.Uuid(), nullable=False),
        sa.Column("exercicio_id", sa.Uuid(), nullable=False),
        sa.Column("series", sa.String(length=50), nullable=False),
        sa.Column("repeticoes", sa.String(length=50), nullable=False),
        sa.Column("ordem", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["dia_rotina_id"],
            ["dias_rotina.id"],
            name=op.f("fk_itens_rotina_dia_rotina_id_dias_rotina"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["exercicio_id"],
            ["exercicios.id"],
            name=op.f("fk_itens_rotina_exercicio_id_exercicios"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_itens_rotina")),
        sa.UniqueConstraint(
            "dia_rotina_id", "ordem", name=op.f("uq_itens_rotina_dia_rotina_id_ordem")
        ),
    )
    op.create_index(op.f("ix_itens_rotina_exercicio_id"), "itens_rotina", ["exercicio_id"])


def downgrade() -> None:
    op.drop_table("itens_rotina")
    op.drop_table("dias_rotina")
    op.drop_table("rotinas")
    op.drop_table("exercicios")
    op.drop_table("usuarios")
