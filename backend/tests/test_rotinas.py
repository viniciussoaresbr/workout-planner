from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.v1.endpoints.rotinas import create_rotina, update_rotina
from app.db.database import Base
from app.models.models import Exercicio, Usuario
from app.schemas.schemas import DiaRotinaCreate, ItemRotinaCreate, RotinaCreate, RotinaUpdate


def test_update_rotina_can_replace_existing_days_without_integrity_conflict() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)

    with Session(bind=engine) as db:
        user = Usuario(nome="Teste", email="teste@example.com", senha_hash="hash")
        exercicio = Exercicio(nome="Supino reto com barra", musculo="Peito", descricao="Descricao")
        db.add_all([user, exercicio])
        db.commit()
        db.refresh(user)
        db.refresh(exercicio)

        rotina_criada = create_rotina(
            payload=RotinaCreate(
                nome="Treino A",
                dias=[
                    DiaRotinaCreate(
                        nome="Segunda",
                        ordem=1,
                        itens=[
                            ItemRotinaCreate(
                                exercicio_id=exercicio.id,
                                series="3",
                                repeticoes="10",
                                ordem=1,
                            )
                        ],
                    )
                ],
            ),
            db=db,
            current_user=user,
        ).data

        primeira_edicao = update_rotina(
            rotina_id=rotina_criada.id,
            payload=RotinaUpdate(
                nome="Treino A Ajustado",
                dias=[
                    DiaRotinaCreate(
                        nome="Segunda",
                        ordem=1,
                        itens=[
                            ItemRotinaCreate(
                                exercicio_id=exercicio.id,
                                series="4",
                                repeticoes="12",
                                ordem=1,
                            )
                        ],
                    )
                ],
            ),
            db=db,
            current_user=user,
        ).data

        assert primeira_edicao.nome == "Treino A Ajustado"
        assert primeira_edicao.dias[0].itens[0].series == "4"
        assert primeira_edicao.dias[0].itens[0].repeticoes == "12"

        segunda_edicao = update_rotina(
            rotina_id=rotina_criada.id,
            payload=RotinaUpdate(
                nome="Treino A Ajustado",
                dias=[
                    DiaRotinaCreate(
                        nome="Segunda",
                        ordem=1,
                        itens=[
                            ItemRotinaCreate(
                                exercicio_id=exercicio.id,
                                series="5",
                                repeticoes="15",
                                ordem=1,
                            )
                        ],
                    )
                ],
            ),
            db=db,
            current_user=user,
        ).data

    assert segunda_edicao.dias[0].itens[0].series == "5"
    assert segunda_edicao.dias[0].itens[0].repeticoes == "15"
