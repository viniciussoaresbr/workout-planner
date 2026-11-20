"""Utilidades compartilhadas pelos formatos de exportação de rotina (planilha e PDF)."""

import re
import unicodedata

from app.models import Rotina


def build_filename(rotina: Rotina, extensao: str) -> str:
    """Nome de arquivo seguro para o cabeçalho Content-Disposition (somente ASCII)."""
    ascii_name = unicodedata.normalize("NFKD", rotina.nome).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-") or "treino"
    return f"rotina-{slug[:80]}.{extensao}"


def content_disposition(filename: str) -> str:
    return f'attachment; filename="{filename}"'
