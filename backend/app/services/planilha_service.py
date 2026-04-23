from io import BytesIO

from app.models.models import Rotina


def build_workout_workbook(rotina: Rotina) -> BytesIO:
    import pandas as pd

    rows: list[dict[str, object]] = []
    for dia in sorted(rotina.dias, key=lambda item: item.ordem):
        for item in sorted(dia.itens, key=lambda workout_item: workout_item.ordem):
            rows.append(
                {
                    "Dia": dia.nome,
                    "Exercicio": item.exercicio.nome,
                    "Musculo": item.exercicio.musculo,
                    "Series": item.series,
                    "Repeticoes": item.repeticoes,
                }
            )

    dataframe = pd.DataFrame(rows or [{"Dia": "", "Exercicio": "", "Musculo": "", "Series": "", "Repeticoes": ""}])
    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        dataframe.to_excel(writer, sheet_name="Rotina", index=False)
        workbook = writer.book
        worksheet = writer.sheets["Rotina"]

        for column_index, column_name in enumerate(dataframe.columns):
            max_width = max(len(str(column_name)), *(len(str(value)) for value in dataframe[column_name].fillna("")))
            worksheet.set_column(column_index, column_index, min(max_width + 2, 40))

    output.seek(0)
    return output
