from app.db.session import SessionLocal
from app.seed import seed_exercicios


def main() -> None:
    with SessionLocal() as db:
        result = seed_exercicios(db)
    print(
        f"Seed concluído. Inseridos: {result.inseridos}, atualizados: {result.atualizados}, "
        f"total no banco: {result.total}"
    )


if __name__ == "__main__":
    main()
