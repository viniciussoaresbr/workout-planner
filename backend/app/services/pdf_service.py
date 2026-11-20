"""Geração do PDF de uma rotina (reportlab), com uma tabela de exercícios por dia."""

from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    Flowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.models import DiaRotina, Rotina
from app.services import exportacao

PDF_MEDIA_TYPE = "application/pdf"

_MARGEM = 18 * mm
_COLUNAS = ("#", "Exercício", "Músculo", "Séries", "Repetições")
# Larguras somam a área útil do A4 (210 mm - 2 margens = 174 mm).
_LARGURAS = (10 * mm, 70 * mm, 42 * mm, 24 * mm, 28 * mm)

# Paleta pensada para impressão: tons do acento da interface sobre fundo branco.
_TEXTO = colors.HexColor("#0F172A")
_TEXTO_SUAVE = colors.HexColor("#64748B")
_ACENTO = colors.HexColor("#0E6170")
_ACENTO_FUNDO = colors.HexColor("#E3F3F5")
_LINHA = colors.HexColor("#CBD5E1")
_ZEBRA = colors.HexColor("#F8FAFC")

_TITULO = ParagraphStyle(
    "Titulo", fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=_TEXTO
)
_RESUMO = ParagraphStyle(
    "Resumo", fontName="Helvetica", fontSize=10, leading=14, textColor=_TEXTO_SUAVE
)
_DIA = ParagraphStyle(
    "Dia", fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=_ACENTO, spaceAfter=6
)
_CELULA = ParagraphStyle("Celula", fontName="Helvetica", fontSize=10, leading=13, textColor=_TEXTO)
_CELULA_CENTRO = ParagraphStyle("CelulaCentro", parent=_CELULA, alignment=TA_CENTER)
_CABECALHO = ParagraphStyle(
    "Cabecalho", parent=_CELULA, fontName="Helvetica-Bold", textColor=_ACENTO
)
_CABECALHO_CENTRO = ParagraphStyle("CabecalhoCentro", parent=_CABECALHO, alignment=TA_CENTER)

# Colunas numéricas (#, séries e repetições) ficam centralizadas.
_CENTRALIZADAS = {0, 3, 4}


def build_pdf(rotina: Rotina) -> bytes:
    output = BytesIO()
    doc = SimpleDocTemplate(
        output,
        pagesize=A4,
        leftMargin=_MARGEM,
        rightMargin=_MARGEM,
        topMargin=_MARGEM,
        bottomMargin=_MARGEM + 6 * mm,  # espaço para o rodapé
        title=rotina.nome,
        author="Workout Planner",
        creator="Workout Planner",
    )
    doc.build(_conteudo(rotina), onFirstPage=_rodape, onLaterPages=_rodape)
    return output.getvalue()


def build_filename(rotina: Rotina) -> str:
    return exportacao.build_filename(rotina, "pdf")


def _conteudo(rotina: Rotina) -> list[Flowable]:
    dias = [dia for dia in rotina.dias if dia.itens]  # já ordenados pelo relacionamento
    total = sum(len(dia.itens) for dia in dias)

    story: list[Flowable] = [
        Paragraph(_texto(rotina.nome), _TITULO),
        Spacer(0, 2 * mm),
        Paragraph(_resumo(total, len(dias)), _RESUMO),
        Spacer(0, 8 * mm),
    ]
    if not dias:
        story.append(Paragraph("Esta rotina ainda não tem exercícios.", _CELULA))

    for dia in dias:
        # Mantém o título do dia junto da tabela; tabelas longas ainda podem quebrar de página.
        story.append(KeepTogether([Paragraph(_texto(dia.nome), _DIA), _tabela(dia)]))
        story.append(Spacer(0, 7 * mm))
    return story


def _tabela(dia: DiaRotina) -> Table:
    linhas = [
        (str(posicao), item.exercicio.nome, item.exercicio.musculo, item.series, item.repeticoes)
        for posicao, item in enumerate(dia.itens, start=1)
    ]
    dados = [_linha(_COLUNAS, _CABECALHO, _CABECALHO_CENTRO)]
    dados += [_linha(linha, _CELULA, _CELULA_CENTRO) for linha in linhas]

    tabela = Table(dados, colWidths=_LARGURAS, repeatRows=1)
    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), _ACENTO_FUNDO),
                ("LINEBELOW", (0, 0), (-1, 0), 0.75, _ACENTO),
                ("LINEBELOW", (0, 1), (-1, -1), 0.25, _LINHA),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _ZEBRA]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return tabela


def _linha(
    valores: tuple[str, ...], estilo: ParagraphStyle, estilo_centro: ParagraphStyle
) -> list[Paragraph]:
    # Paragraph quebra textos longos dentro da célula em vez de transbordar a coluna.
    return [
        Paragraph(_texto(valor), estilo_centro if coluna in _CENTRALIZADAS else estilo)
        for coluna, valor in enumerate(valores)
    ]


def _resumo(exercicios: int, dias: int) -> str:
    rotulo_exercicios = "exercício" if exercicios == 1 else "exercícios"
    rotulo_dias = "dia" if dias == 1 else "dias"
    return f"{exercicios} {rotulo_exercicios} em {dias} {rotulo_dias}"


def _texto(valor: str) -> str:
    """Prepara texto do usuário para um Paragraph.

    As fontes padrão do PDF (Helvetica) só cobrem o cp1252: caracteres fora dele, como emojis,
    seriam desenhados como quadrados pretos e por isso são descartados. O Paragraph também
    interpreta marcação XML, então o texto precisa ser escapado.
    """
    suportado = "".join(char for char in valor if _no_cp1252(char))
    return escape(" ".join(suportado.split()) or "-")


def _no_cp1252(char: str) -> bool:
    try:
        char.encode("cp1252")
    except UnicodeEncodeError:
        return False
    return True


def _rodape(canvas: Canvas, doc: SimpleDocTemplate) -> None:
    largura, _ = doc.pagesize
    y = _MARGEM - 4 * mm
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(_TEXTO_SUAVE)
    canvas.drawString(_MARGEM, y, "Workout Planner")
    canvas.drawRightString(largura - _MARGEM, y, f"Página {doc.page}")
    canvas.restoreState()
