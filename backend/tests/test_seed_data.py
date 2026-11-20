"""Consistência do catálogo do seed: nada de exercícios duplicados, nem com outro nome."""

import unicodedata
from collections import Counter

from app.seed.data import EXERCICIOS, SINONIMOS


def _normalizar(nome: str) -> str:
    """Ignora maiúsculas, acentos, hífens e espaços extras ao comparar nomes."""
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return " ".join(sem_acento.casefold().replace("-", " ").split())


NOMES = {_normalizar(exercicio.nome) for exercicio in EXERCICIOS}


def test_catalogo_sem_nomes_repetidos() -> None:
    repetidos = [
        nome
        for nome, total in Counter(_normalizar(e.nome) for e in EXERCICIOS).items()
        if total > 1
    ]
    assert repetidos == []


def test_sinonimos_nao_estao_cadastrados_como_exercicios() -> None:
    cadastrados = [sinonimo for sinonimo in SINONIMOS if _normalizar(sinonimo) in NOMES]
    assert cadastrados == []


def test_sinonimos_apontam_para_exercicios_do_catalogo() -> None:
    sem_destino = [nome for nome in SINONIMOS.values() if _normalizar(nome) not in NOMES]
    assert sem_destino == []


def test_exercicios_tem_grupo_e_descricao() -> None:
    for exercicio in EXERCICIOS:
        assert exercicio.musculo.strip(), exercicio.nome
        assert len(exercicio.nome) <= 160, exercicio.nome
        assert exercicio.descricao_final.endswith("."), exercicio.nome
