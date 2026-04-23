from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import func, select

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.database import SessionLocal
from app.models.models import Exercicio

EXERCICIOS_EXEMPLO = [
# ================= PEITO =================
{"nome": "Supino reto com barra", "musculo_alvo": "Peito", "descricao": "Execução do exercício Supino reto com barra."},
{"nome": "Supino reto com halteres", "musculo_alvo": "Peito", "descricao": "Execução do exercício Supino reto com halteres."},
{"nome": "Supino inclinado com barra", "musculo_alvo": "Peito", "descricao": "Execução do exercício Supino inclinado com barra."},
{"nome": "Supino inclinado com halteres", "musculo_alvo": "Peito", "descricao": "Execução do exercício Supino inclinado com halteres."},
{"nome": "Supino declinado com barra", "musculo_alvo": "Peito", "descricao": "Execução do exercício Supino declinado com barra."},
{"nome": "Crucifixo reto com halteres", "musculo_alvo": "Peito", "descricao": "Execução do exercício Crucifixo reto com halteres."},
{"nome": "Crucifixo inclinado com halteres", "musculo_alvo": "Peito", "descricao": "Execução do exercício Crucifixo inclinado com halteres."},
{"nome": "Crossover na polia alta", "musculo_alvo": "Peito", "descricao": "Execução do exercício Crossover na polia alta."},
{"nome": "Crossover na polia baixa", "musculo_alvo": "Peito", "descricao": "Execução do exercício Crossover na polia baixa."},
{"nome": "Peck deck", "musculo_alvo": "Peito", "descricao": "Execução do exercício Peck deck."},

# ================= COSTAS =================
{"nome": "Puxada frontal na polia", "musculo_alvo": "Costas", "descricao": "Execução do exercício Puxada frontal na polia."},
{"nome": "Puxada aberta na polia", "musculo_alvo": "Costas", "descricao": "Execução do exercício Puxada aberta na polia."},
{"nome": "Puxada supinada na polia", "musculo_alvo": "Costas", "descricao": "Execução do exercício Puxada supinada na polia."},
{"nome": "Remada curvada com barra", "musculo_alvo": "Costas", "descricao": "Execução do exercício Remada curvada com barra."},
{"nome": "Remada com halteres", "musculo_alvo": "Costas", "descricao": "Execução do exercício Remada com halteres."},
{"nome": "Remada unilateral com halter", "musculo_alvo": "Costas", "descricao": "Execução do exercício Remada unilateral com halter."},
{"nome": "Remada baixa na polia", "musculo_alvo": "Costas", "descricao": "Execução do exercício Remada baixa na polia."},
{"nome": "Barra fixa pronada", "musculo_alvo": "Costas", "descricao": "Execução do exercício Barra fixa pronada."},
{"nome": "Barra fixa supinada", "musculo_alvo": "Costas", "descricao": "Execução do exercício Barra fixa supinada."},

# ================= PERNAS =================
{"nome": "Agachamento livre", "musculo_alvo": "Pernas", "descricao": "Execução do exercício Agachamento livre."},
{"nome": "Agachamento com barra", "musculo_alvo": "Pernas", "descricao": "Execução do exercício Agachamento com barra."},
{"nome": "Agachamento no smith", "musculo_alvo": "Pernas", "descricao": "Execução do exercício Agachamento no smith."},
{"nome": "Leg press 45", "musculo_alvo": "Pernas", "descricao": "Execução do exercício Leg press 45."},
{"nome": "Leg press horizontal", "musculo_alvo": "Pernas", "descricao": "Execução do exercício Leg press horizontal."},
{"nome": "Afundo com halteres", "musculo_alvo": "Pernas", "descricao": "Execução do exercício Afundo com halteres."},
{"nome": "Afundo no smith", "musculo_alvo": "Pernas", "descricao": "Execução do exercício Afundo no smith."},
{"nome": "Cadeira extensora", "musculo_alvo": "Pernas", "descricao": "Execução do exercício Cadeira extensora."},
{"nome": "Mesa flexora", "musculo_alvo": "Pernas", "descricao": "Execução do exercício Mesa flexora."},
{"nome": "Stiff com halteres", "musculo_alvo": "Pernas", "descricao": "Execução do exercício Stiff com halteres."},

# ================= OMBROS =================
{"nome": "Desenvolvimento com barra", "musculo_alvo": "Ombros", "descricao": "Execução do exercício Desenvolvimento com barra."},
{"nome": "Desenvolvimento com halteres", "musculo_alvo": "Ombros", "descricao": "Execução do exercício Desenvolvimento com halteres."},
{"nome": "Elevação lateral com halteres", "musculo_alvo": "Ombros", "descricao": "Execução do exercício Elevação lateral com halteres."},
{"nome": "Elevação lateral na polia", "musculo_alvo": "Ombros", "descricao": "Execução do exercício Elevação lateral na polia."},
{"nome": "Elevação frontal com halteres", "musculo_alvo": "Ombros", "descricao": "Execução do exercício Elevação frontal com halteres."},
{"nome": "Face pull na polia", "musculo_alvo": "Ombros", "descricao": "Execução do exercício Face pull na polia."},

# ================= BÍCEPS =================
{"nome": "Rosca direta com barra", "musculo_alvo": "Bíceps", "descricao": "Execução do exercício Rosca direta com barra."},
{"nome": "Rosca direta com barra EZ", "musculo_alvo": "Bíceps", "descricao": "Execução do exercício Rosca direta com barra EZ."},
{"nome": "Rosca alternada com halteres", "musculo_alvo": "Bíceps", "descricao": "Execução do exercício Rosca alternada com halteres."},
{"nome": "Rosca martelo", "musculo_alvo": "Bíceps", "descricao": "Execução do exercício Rosca martelo."},
{"nome": "Rosca concentrada", "musculo_alvo": "Bíceps", "descricao": "Execução do exercício Rosca concentrada."},

# ================= TRÍCEPS =================
{"nome": "Tríceps pulley com corda", "musculo_alvo": "Tríceps", "descricao": "Execução do exercício Tríceps pulley com corda."},
{"nome": "Tríceps pulley com barra", "musculo_alvo": "Tríceps", "descricao": "Execução do exercício Tríceps pulley com barra."},
{"nome": "Tríceps francês com halter", "musculo_alvo": "Tríceps", "descricao": "Execução do exercício Tríceps francês com halter."},
{"nome": "Tríceps testa com barra EZ", "musculo_alvo": "Tríceps", "descricao": "Execução do exercício Tríceps testa com barra EZ."},
{"nome": "Mergulho no banco", "musculo_alvo": "Tríceps", "descricao": "Execução do exercício Mergulho no banco."},

# ================= CORE =================
{"nome": "Prancha isométrica", "musculo_alvo": "Core", "descricao": "Execução do exercício Prancha isométrica."},
{"nome": "Prancha lateral", "musculo_alvo": "Core", "descricao": "Execução do exercício Prancha lateral."},
{"nome": "Crunch abdominal", "musculo_alvo": "Core", "descricao": "Execução do exercício Crunch abdominal."},
{"nome": "Abdominal infra no banco", "musculo_alvo": "Core", "descricao": "Execução do exercício Abdominal infra no banco."},
{"nome": "Elevação de pernas suspenso", "musculo_alvo": "Core", "descricao": "Execução do exercício Elevação de pernas suspenso."},

# ================= GLÚTEOS =================
{"nome": "Hip thrust com barra", "musculo_alvo": "Glúteos", "descricao": "Execução do exercício Hip thrust com barra."},
{"nome": "Ponte de glúteos", "musculo_alvo": "Glúteos", "descricao": "Execução do exercício Ponte de glúteos."},
{"nome": "Glúteo no cabo", "musculo_alvo": "Glúteos", "descricao": "Execução do exercício Glúteo no cabo."},
{"nome": "Afundo búlgaro", "musculo_alvo": "Glúteos", "descricao": "Execução do exercício Afundo búlgaro."},

# ================= PANTURRILHA =================
{"nome": "Panturrilha em pé", "musculo_alvo": "Panturrilha", "descricao": "Execução do exercício Panturrilha em pé."},
{"nome": "Panturrilha sentado", "musculo_alvo": "Panturrilha", "descricao": "Execução do exercício Panturrilha sentado."},
{"nome": "Panturrilha no leg press", "musculo_alvo": "Panturrilha", "descricao": "Execução do exercício Panturrilha no leg press."},
]

GRUPOS_OBRIGATORIOS = {
    "Peito",
    "Costas",
    "Pernas",
    "Ombros",
    "Bíceps",
    "Tríceps",
    "Core",
    "Glúteos",
    "Panturrilha",
}

LEGACY_EXERCISE_NAMES = {
    "Supino reto",
    "Supino inclinado",
    "Crucifixo com halteres",
    "Puxada frontal",
    "Remada curvada",
    "Remada baixa",
    "Leg press",
    "Cadeira extensora",
    "Mesa flexora",
    "Levantamento terra romeno",
    "Desenvolvimento com halteres",
    "Elevacao lateral",
    "Face pull",
    "Rosca direta",
    "Rosca martelo",
    "Triceps pulley",
    "Triceps frances",
    "Prancha",
    "Abdominal infra",
}


def validar_seed() -> None:
    grupos_presentes = {item["musculo_alvo"] for item in EXERCICIOS_EXEMPLO}
    grupos_faltantes = GRUPOS_OBRIGATORIOS - grupos_presentes

    if len(EXERCICIOS_EXEMPLO) < 30:
        raise ValueError("O seed precisa conter no mínimo 30 exercícios.")
    if grupos_faltantes:
        raise ValueError(f"Grupos musculares faltando no seed: {sorted(grupos_faltantes)}")


# Mapeamento de nomes antigos para nomes novos para preservar integridade referencial
NAME_UPDATES = {
    "Supino reto com barra": "Supino reto com barra", # Mantido
    "Supino inclinado com halteres": "Supino inclinado com halteres", # Mantido
    "Crucifixo reto com halteres": "Crucifixo reto com halteres", # Mantido
    "Puxada frontal na polia": "Puxada frontal na polia", # Mantido
    "Remada curvada com barra": "Remada curvada com barra", # Mantido
    "Remada baixa na polia": "Remada baixa na polia", # Mantido
    "Barra fixa pronada": "Barra fixa pronada", # Mantido
    "Agachamento livre": "Agachamento livre", # Mantido
    "Leg press 45": "Leg press 45", # Mantido
    "Cadeira extensora": "Cadeira extensora", # Mantido
    "Mesa flexora": "Mesa flexora", # Mantido
    "Desenvolvimento militar com barra": "Desenvolvimento com barra",
    "Elevação lateral com halteres": "Elevação lateral com halteres", # Mantido
    "Elevação frontal com halteres": "Elevação frontal com halteres", # Mantido
    "Face pull na polia": "Face pull na polia", # Mantido
    "Rosca direta com barra": "Rosca direta com barra", # Mantido
    "Rosca alternada com halteres": "Rosca alternada com halteres", # Mantido
    "Rosca martelo": "Rosca martelo", # Mantido
    "Rosca concentrada": "Rosca concentrada", # Mantido
    "Tríceps pulley com corda": "Tríceps pulley com corda", # Mantido
    "Tríceps francês com halter": "Tríceps francês com halter", # Mantido
    "Tríceps testa com barra EZ": "Tríceps testa com barra EZ", # Mantido
    "Mergulho no banco": "Mergulho no banco", # Mantido
    "Prancha isométrica": "Prancha isométrica", # Mantido
    "Abdominal infra no banco": "Abdominal infra no banco", # Mantido
    "Crunch abdominal": "Crunch abdominal", # Mantido
    "Elevação de pernas suspenso": "Elevação de pernas suspenso", # Mantido
    "Hip thrust com barra": "Hip thrust com barra", # Mantido
    "Glúteo no cabo": "Glúteo no cabo", # Mantido
    "Afundo búlgaro": "Afundo búlgaro", # Mantido
    "Ponte de glúteos": "Ponte de glúteos", # Mantido
}


def seed_exercicios() -> tuple[int, int, int, int]:
    validar_seed()

    db = SessionLocal()
    inseridos = 0
    atualizados = 0
    removidos_legado = 0

    try:
        # 1. Remover exercícios legados que não estão em EXERCICIOS_EXEMPLO nem no NAME_UPDATES
        exemplos_nomes = {item["nome"] for item in EXERCICIOS_EXEMPLO}
        updates_velhos_nomes = set(NAME_UPDATES.keys())
        
        # Só deletamos se não estiver nos planos de atualização
        for exercicio in db.scalars(select(Exercicio).where(Exercicio.nome.in_(LEGACY_EXERCISE_NAMES))).all():
            if exercicio.nome not in exemplos_nomes and exercicio.nome not in updates_velhos_nomes:
                db.delete(exercicio)
                removidos_legado += 1
        db.flush()

        # 2. Processar NAME_UPDATES primeiro para renomear exercícios existentes
        existentes = {
            exercicio.nome: exercicio
            for exercicio in db.scalars(select(Exercicio)).all()
        }

        for velho_nome, novo_nome in NAME_UPDATES.items():
            if velho_nome in existentes and velho_nome != novo_nome:
                exercicio = existentes[velho_nome]
                exercicio.nome = novo_nome
                db.flush()
                # Atualizar nosso dicionário local de existentes
                existentes[novo_nome] = exercicio
                del existentes[velho_nome]

        # 3. Sincronizar com EXERCICIOS_EXEMPLO
        for item in EXERCICIOS_EXEMPLO:
            exercicio = existentes.get(item["nome"])
            if exercicio is None:
                db.add(
                    Exercicio(
                        nome=item["nome"],
                        musculo=item["musculo_alvo"],
                        descricao=item["descricao"],
                    )
                )
                inseridos += 1
                continue

            exercicio.musculo = item["musculo_alvo"]
            exercicio.descricao = item["descricao"]
            atualizados += 1

        db.commit()
        total = db.scalar(select(func.count()).select_from(Exercicio)) or 0
        return inseridos, atualizados, removidos_legado, total
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    inseridos, atualizados, removidos_legado, total = seed_exercicios()
    print(
        "Seed concluído com sucesso. "
        f"Inseridos: {inseridos}, atualizados: {atualizados}, removidos legados: {removidos_legado}, total no banco: {total}"
    )
