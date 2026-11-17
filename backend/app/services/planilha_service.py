"""Geração da planilha Excel de uma rotina (xlsxwriter, sem dependência de pandas)."""

import re
import unicodedata
from io import BytesIO

import xlsxwriter

from app.models import Rotina

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

_COLUNAS = ("Dia", "Exercício", "Músculo", "Séries", "Repetições")
_MAX_COLUMN_WIDTH = 40


def build_workbook(rotina: Rotina) -> bytes:
    linhas = [
        (dia.nome, item.exercicio.nome, item.exercicio.musculo, item.series, item.repeticoes)
        for dia in rotina.dias  # dias e itens já vêm ordenados pelo relacionamento
        for item in dia.itens
    ]

    output = BytesIO()
    with xlsxwriter.Workbook(output, {"in_memory": True}) as workbook:
        worksheet = workbook.add_worksheet("Rotina")
        header = workbook.add_format({"bold": True, "bg_color": "#E2E8F0", "border": 1})

        worksheet.write_row(0, 0, _COLUNAS, header)
        for row, linha in enumerate(linhas, start=1):
            for col, valor in enumerate(linha):
                # Séries/repetições numéricas viram números de verdade no Excel.
                if isinstance(valor, str) and valor.isdigit():
                    worksheet.write_number(row, col, int(valor))
                else:
                    worksheet.write_string(row, col, valor)

        for col, titulo in enumerate(_COLUNAS):
            largura = max([len(titulo), *(len(str(linha[col])) for linha in linhas)])
            worksheet.set_column(col, col, min(largura + 2, _MAX_COLUMN_WIDTH))

        worksheet.freeze_panes(1, 0)
        if linhas:
            worksheet.autofilter(0, 0, len(linhas), len(_COLUNAS) - 1)

    return output.getvalue()


def build_filename(rotina: Rotina) -> str:
    """Nome de arquivo seguro para o cabeçalho Content-Disposition (somente ASCII)."""
    ascii_name = unicodedata.normalize("NFKD", rotina.nome).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-") or "treino"
    return f"rotina-{slug[:80]}.xlsx"
