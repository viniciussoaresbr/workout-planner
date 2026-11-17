"""Modelos ORM. Importar este pacote registra todas as tabelas em Base.metadata."""

from app.models.exercicio import Exercicio
from app.models.rotina import DiaRotina, ItemRotina, Rotina
from app.models.usuario import Usuario

__all__ = ["DiaRotina", "Exercicio", "ItemRotina", "Rotina", "Usuario"]
