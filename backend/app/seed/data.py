"""Catálogo inicial de exercícios usado pelo seed."""

from typing import NamedTuple


class ExercicioSeed(NamedTuple):
    nome: str
    musculo: str
    descricao: str | None = None

    @property
    def descricao_final(self) -> str:
        return self.descricao or f"Execução do exercício {self.nome}."


EXERCICIOS: tuple[ExercicioSeed, ...] = (
    # Peito
    ExercicioSeed("Supino reto com barra", "Peito"),
    ExercicioSeed("Supino reto com halteres", "Peito"),
    ExercicioSeed("Supino inclinado com barra", "Peito"),
    ExercicioSeed("Supino inclinado com halteres", "Peito"),
    ExercicioSeed("Supino declinado com barra", "Peito"),
    ExercicioSeed("Crucifixo reto com halteres", "Peito"),
    ExercicioSeed("Crucifixo inclinado com halteres", "Peito"),
    ExercicioSeed("Crossover na polia alta", "Peito"),
    ExercicioSeed("Crossover na polia baixa", "Peito"),
    ExercicioSeed("Peck deck", "Peito"),
    ExercicioSeed(
        "Supino inclinado na máquina",
        "Peito",
        "Execução do exercício Supino inclinado em máquina guiada.",
    ),
    ExercicioSeed(
        "Crossover com banco",
        "Peito",
        "Execução do exercício Crossover com apoio em banco para melhor isolamento do peitoral.",
    ),
    ExercicioSeed(
        "Paralela para peito",
        "Peito",
        "Execução de paralela com inclinação do tronco para foco em peitoral.",
    ),
    ExercicioSeed(
        "Crucifixo inclinado no crossover",
        "Peito",
        "Execução do exercício Crucifixo inclinado utilizando polia crossover.",
    ),
    ExercicioSeed(
        "Supino declinado na máquina",
        "Peito",
        "Execução do exercício Supino declinado em máquina guiada.",
    ),
    # Costas
    ExercicioSeed("Puxada frontal na polia", "Costas"),
    ExercicioSeed("Puxada aberta na polia", "Costas"),
    ExercicioSeed("Puxada supinada na polia", "Costas"),
    ExercicioSeed("Remada curvada com barra", "Costas"),
    ExercicioSeed("Remada com halteres", "Costas"),
    ExercicioSeed("Remada unilateral com halter", "Costas"),
    ExercicioSeed("Remada baixa na polia", "Costas"),
    ExercicioSeed("Barra fixa pronada", "Costas"),
    ExercicioSeed("Barra fixa supinada", "Costas"),
    ExercicioSeed(
        "Puxada alta convergente",
        "Costas",
        "Execução do exercício Puxada alta em máquina convergente.",
    ),
    ExercicioSeed(
        "Remada máquina unilateral",
        "Costas",
        "Execução do exercício Remada em máquina de forma unilateral.",
    ),
    ExercicioSeed(
        "Puxada fechada com triângulo",
        "Costas",
        "Execução do exercício Puxada fechada na polia utilizando triângulo.",
    ),
    # Pernas
    ExercicioSeed("Agachamento livre", "Pernas"),
    ExercicioSeed("Agachamento com barra", "Pernas"),
    ExercicioSeed("Agachamento no smith", "Pernas"),
    ExercicioSeed("Leg press 45", "Pernas"),
    ExercicioSeed("Leg press horizontal", "Pernas"),
    ExercicioSeed("Afundo com halteres", "Pernas"),
    ExercicioSeed("Afundo no smith", "Pernas"),
    ExercicioSeed("Cadeira extensora", "Pernas"),
    ExercicioSeed("Mesa flexora", "Pernas"),
    ExercicioSeed("Stiff com halteres", "Pernas"),
    ExercicioSeed(
        "Levantamento sumô na máquina",
        "Pernas",
        "Execução do exercício Levantamento sumô em máquina guiada.",
    ),
    ExercicioSeed("Stiff com barra", "Pernas"),
    ExercicioSeed(
        "Agachamento hack 45",
        "Pernas",
        "Execução do exercício Agachamento hack na máquina 45 graus.",
    ),
    ExercicioSeed(
        "Cadeira flexora", "Pernas", "Execução do exercício Cadeira flexora para isquiotibiais."
    ),
    ExercicioSeed(
        "Flexora em pé unilateral",
        "Pernas",
        "Execução do exercício Flexora em pé de forma unilateral.",
    ),
    # Ombros
    ExercicioSeed("Desenvolvimento com barra", "Ombros"),
    ExercicioSeed("Desenvolvimento com halteres", "Ombros"),
    ExercicioSeed("Elevação lateral com halteres", "Ombros"),
    ExercicioSeed("Elevação lateral na polia", "Ombros"),
    ExercicioSeed("Elevação frontal com halteres", "Ombros"),
    ExercicioSeed("Face pull na polia", "Ombros"),
    # Bíceps
    ExercicioSeed("Rosca direta com barra", "Bíceps"),
    ExercicioSeed("Rosca direta com barra EZ", "Bíceps"),
    ExercicioSeed("Rosca alternada com halteres", "Bíceps"),
    ExercicioSeed("Rosca martelo", "Bíceps"),
    ExercicioSeed("Rosca concentrada", "Bíceps"),
    ExercicioSeed(
        "Rosca Scott na máquina", "Bíceps", "Execução do exercício Rosca Scott em máquina ou polia."
    ),
    ExercicioSeed(
        "Rosca 45",
        "Bíceps",
        "Execução do exercício Rosca 45 graus com halteres no banco inclinado.",
    ),
    # Tríceps
    ExercicioSeed("Tríceps pulley com corda", "Tríceps"),
    ExercicioSeed("Tríceps pulley com barra", "Tríceps"),
    ExercicioSeed("Tríceps francês com halter", "Tríceps"),
    ExercicioSeed("Tríceps testa com barra EZ", "Tríceps"),
    ExercicioSeed("Mergulho no banco", "Tríceps"),
    ExercicioSeed(
        "Tríceps coice na polia", "Tríceps", "Execução do exercício Tríceps coice utilizando polia."
    ),
    # Core
    ExercicioSeed("Prancha isométrica", "Core"),
    ExercicioSeed("Prancha lateral", "Core"),
    ExercicioSeed("Crunch abdominal", "Core"),
    ExercicioSeed("Abdominal infra no banco", "Core"),
    ExercicioSeed("Elevação de pernas suspenso", "Core"),
    # Glúteos
    ExercicioSeed("Hip thrust com barra", "Glúteos"),
    ExercicioSeed("Ponte de glúteos", "Glúteos"),
    ExercicioSeed("Glúteo no cabo", "Glúteos"),
    ExercicioSeed("Afundo búlgaro", "Glúteos"),
    ExercicioSeed(
        "Elevação pélvica na máquina",
        "Glúteos",
        "Execução do exercício Elevação pélvica em máquina.",
    ),
    # Panturrilha
    ExercicioSeed("Panturrilha em pé", "Panturrilha"),
    ExercicioSeed("Panturrilha sentado", "Panturrilha"),
    ExercicioSeed("Panturrilha no leg press", "Panturrilha"),
)
