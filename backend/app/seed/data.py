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
        "Voador",
        "Peito",
        "Na máquina, segurando os pegadores com os braços quase estendidos, una as mãos à frente "
        "do peito. Diferente do peck deck, em que os antebraços ficam apoiados nas almofadas.",
    ),
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
    ExercicioSeed(
        "Supino declinado com halteres",
        "Peito",
        "Supino em banco declinado com halteres, com ênfase na porção inferior do peitoral.",
    ),
    ExercicioSeed(
        "Supino reto na máquina",
        "Peito",
        "Supino em máquina guiada com o encosto reto. Também chamado de chest press.",
    ),
    ExercicioSeed("Supino reto no smith", "Peito", "Supino reto com a barra guiada do smith."),
    ExercicioSeed(
        "Supino inclinado no smith",
        "Peito",
        "Supino em banco inclinado com a barra guiada do smith, com ênfase na porção superior do peitoral.",
    ),
    ExercicioSeed(
        "Pullover com halter",
        "Peito",
        "Deitado no banco, leve o halter de trás da cabeça até acima do peito com os braços quase estendidos.",
    ),
    ExercicioSeed(
        "Flexão de braço",
        "Peito",
        "Flexão no solo com o peso do corpo e as mãos um pouco além da largura dos ombros.",
    ),
    ExercicioSeed(
        "Crossover na polia média",
        "Peito",
        "Crucifixo em pé com as polias na altura do peito, unindo as mãos à frente do corpo.",
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
    ExercicioSeed(
        "Levantamento terra",
        "Costas",
        "Levantamento da barra do chão até a extensão completa do quadril, com a coluna neutra. Também chamado de deadlift.",
    ),
    ExercicioSeed(
        "Remada cavalinho",
        "Costas",
        "Remada com a barra presa em uma das pontas, puxando o pegador em direção ao abdômen. Também chamada de remada T.",
    ),
    ExercicioSeed(
        "Pulldown com braços estendidos na polia",
        "Costas",
        "Em pé na polia alta, leve a barra ou a corda até as coxas com os cotovelos quase estendidos. Também chamado de pullover na polia.",
    ),
    ExercicioSeed(
        "Extensão lombar no banco romano",
        "Costas",
        "Extensão do tronco no banco romano (banco 45°) com o quadril apoiado. Também chamada de hiperextensão lombar.",
    ),
    ExercicioSeed(
        "Remada invertida",
        "Costas",
        "Remada com o peso do corpo, deitado sob uma barra baixa, puxando o peito até ela. Também chamada de remada australiana.",
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
    ExercicioSeed(
        "Agachamento frontal com barra",
        "Pernas",
        "Agachamento com a barra apoiada na frente dos ombros, tronco mais vertical e ênfase nos quadríceps.",
    ),
    ExercicioSeed(
        "Agachamento goblet",
        "Pernas",
        "Agachamento segurando um halter ou kettlebell junto ao peito.",
    ),
    ExercicioSeed(
        "Agachamento sumô com halter",
        "Pernas",
        "Agachamento com os pés afastados e as pontas para fora, segurando um halter entre as pernas. Também chamado de agachamento plié.",
    ),
    ExercicioSeed(
        "Passada com halteres",
        "Pernas",
        "Passos largos à frente, alternando as pernas e descendo o joelho de trás em direção ao chão. Ao contrário do afundo, o corpo se desloca a cada repetição.",
    ),
    ExercicioSeed(
        "Subida no banco com halteres",
        "Pernas",
        "Subida em um banco ou caixa, uma perna de cada vez, segurando halteres. Também chamada de step-up.",
    ),
    ExercicioSeed(
        "Cadeira adutora",
        "Pernas",
        "Na máquina, aproxime as pernas contra a resistência, trabalhando os adutores da coxa.",
    ),
    ExercicioSeed(
        "Levantamento terra sumô com barra",
        "Pernas",
        "Levantamento terra com os pés bem afastados e as mãos por dentro das pernas.",
    ),
    ExercicioSeed(
        "Good morning com barra",
        "Pernas",
        "Com a barra nas costas e os joelhos levemente flexionados, incline o tronco à frente a partir do quadril. Também chamado de bom dia.",
    ),
    ExercicioSeed(
        "Agachamento sissy",
        "Pernas",
        "Agachamento com os calcanhares elevados e o tronco inclinado para trás, levando os joelhos à frente para isolar os quadríceps.",
    ),
    ExercicioSeed(
        "Flexão nórdica",
        "Pernas",
        "Ajoelhado com os tornozelos presos, desça o tronco à frente devagar, controlando com os isquiotibiais.",
    ),
    # Ombros
    ExercicioSeed("Desenvolvimento com barra", "Ombros"),
    ExercicioSeed("Desenvolvimento com halteres", "Ombros"),
    ExercicioSeed("Elevação lateral com halteres", "Ombros"),
    ExercicioSeed("Elevação lateral na polia", "Ombros"),
    ExercicioSeed("Elevação frontal com halteres", "Ombros"),
    ExercicioSeed("Face pull na polia", "Ombros"),
    ExercicioSeed(
        "Desenvolvimento na máquina", "Ombros", "Desenvolvimento sentado em máquina guiada."
    ),
    ExercicioSeed(
        "Desenvolvimento Arnold",
        "Ombros",
        "Desenvolvimento com halteres que começa com as palmas voltadas para o rosto e gira os punhos durante a subida.",
    ),
    ExercicioSeed(
        "Desenvolvimento no smith", "Ombros", "Desenvolvimento sentado com a barra guiada do smith."
    ),
    ExercicioSeed(
        "Elevação lateral na máquina",
        "Ombros",
        "Elevação lateral em máquina com apoio para os braços.",
    ),
    ExercicioSeed(
        "Elevação frontal na polia",
        "Ombros",
        "Elevação frontal na polia baixa, com barra ou corda.",
    ),
    ExercicioSeed(
        "Elevação frontal com anilha",
        "Ombros",
        "Elevação frontal segurando uma anilha com as duas mãos.",
    ),
    ExercicioSeed(
        "Crucifixo invertido com halteres",
        "Ombros",
        "Com o tronco inclinado à frente, abra os braços para os lados, focando no deltoide posterior. Também chamado de crucifixo inverso.",
    ),
    ExercicioSeed(
        "Crucifixo invertido na máquina",
        "Ombros",
        "No peck deck, sentado de frente para o encosto, abra os braços para trás. Também chamado de voador invertido.",
    ),
    ExercicioSeed(
        "Crucifixo invertido na polia",
        "Ombros",
        "Em pé entre as polias altas, com os cabos cruzados, abra os braços para trás, focando no deltoide posterior.",
    ),
    ExercicioSeed(
        "Remada alta com barra",
        "Ombros",
        "Puxe a barra rente ao corpo até a altura do peito, com os cotovelos acima dos punhos.",
    ),
    ExercicioSeed(
        "Encolhimento com barra",
        "Ombros",
        "Eleve os ombros em direção às orelhas segurando a barra à frente do corpo, trabalhando o trapézio.",
    ),
    ExercicioSeed(
        "Encolhimento com halteres",
        "Ombros",
        "Eleve os ombros em direção às orelhas com um halter em cada mão, trabalhando o trapézio.",
    ),
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
    ExercicioSeed(
        "Rosca Scott com barra EZ",
        "Bíceps",
        "Rosca no banco Scott com a barra EZ e os braços apoiados.",
    ),
    ExercicioSeed(
        "Rosca direta na polia", "Bíceps", "Rosca em pé na polia baixa, com barra reta ou EZ."
    ),
    # Antebraço
    ExercicioSeed(
        "Rosca de punho com barra",
        "Antebraço",
        "Com os antebraços apoiados e as palmas para cima, flexione os punhos levantando a barra.",
    ),
    ExercicioSeed(
        "Rosca de punho invertida com barra",
        "Antebraço",
        "Com os antebraços apoiados e as palmas para baixo, estenda os punhos levantando a barra.",
    ),
    ExercicioSeed(
        "Rosca inversa com barra",
        "Antebraço",
        "Rosca com a pegada pronada (palmas para baixo), com ênfase no braquiorradial.",
    ),
    ExercicioSeed(
        "Caminhada do fazendeiro",
        "Antebraço",
        "Caminhe segurando halteres ou kettlebells pesados ao lado do corpo, trabalhando a pegada. Também chamada de farmer's walk.",
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
    ExercicioSeed(
        "Supino fechado com barra",
        "Tríceps",
        "Supino reto com as mãos na largura dos ombros e os cotovelos junto ao corpo, com ênfase no tríceps.",
    ),
    ExercicioSeed(
        "Tríceps francês na polia com corda",
        "Tríceps",
        "De costas para a polia, estenda os cotovelos levando a corda de trás da cabeça para a frente.",
    ),
    ExercicioSeed(
        "Tríceps coice com halter",
        "Tríceps",
        "Com o tronco inclinado e o braço junto ao corpo, estenda o cotovelo levando o halter para trás.",
    ),
    ExercicioSeed(
        "Tríceps pulley com pegada supinada",
        "Tríceps",
        "Tríceps na polia alta com a barra em pegada supinada (palmas para cima). Também chamado de tríceps pulley inverso.",
    ),
    # Core
    ExercicioSeed("Prancha isométrica", "Core"),
    ExercicioSeed("Prancha lateral", "Core"),
    ExercicioSeed("Crunch abdominal", "Core"),
    ExercicioSeed("Abdominal infra no banco", "Core"),
    ExercicioSeed("Elevação de pernas suspenso", "Core"),
    ExercicioSeed(
        "Abdominal na polia",
        "Core",
        "Ajoelhado de frente para a polia alta, flexione o tronco puxando a corda em direção aos joelhos.",
    ),
    ExercicioSeed(
        "Abdominal oblíquo",
        "Core",
        "Abdominal com rotação do tronco, levando o ombro em direção ao joelho oposto.",
    ),
    ExercicioSeed(
        "Abdominal remador",
        "Core",
        "Deitado, suba o tronco e flexione os joelhos ao mesmo tempo, levando os braços à frente.",
    ),
    ExercicioSeed(
        "Abdominal bicicleta",
        "Core",
        "Deitado, leve o cotovelo em direção ao joelho oposto enquanto estende a outra perna, alternando os lados.",
    ),
    ExercicioSeed(
        "Roda abdominal",
        "Core",
        "Ajoelhado, role a roda à frente estendendo o corpo e volte usando o abdômen.",
    ),
    ExercicioSeed(
        "Abdominal canivete",
        "Core",
        "Deitado, eleve o tronco e as pernas estendidas ao mesmo tempo, levando as mãos aos pés. Também chamado de V-up.",
    ),
    ExercicioSeed(
        "Rotação russa",
        "Core",
        "Sentado com o tronco inclinado para trás, gire o tronco de um lado para o outro, com ou sem peso. Também chamada de russian twist.",
    ),
    ExercicioSeed(
        "Pallof press na polia",
        "Core",
        "Em pé, de lado para a polia, estenda os braços à frente do peito e resista à rotação do tronco.",
    ),
    ExercicioSeed(
        "Escalador",
        "Core",
        "Em prancha alta, leve os joelhos alternadamente em direção ao peito. Também chamado de mountain climber.",
    ),
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
    ExercicioSeed(
        "Cadeira abdutora",
        "Glúteos",
        "Na máquina, afaste as pernas contra a resistência, trabalhando o glúteo médio.",
    ),
    ExercicioSeed(
        "Caminhada lateral com miniband",
        "Glúteos",
        "Com um elástico em volta das pernas e os joelhos semiflexionados, dê passos laterais mantendo a tensão.",
    ),
    # Panturrilha
    ExercicioSeed("Panturrilha em pé", "Panturrilha"),
    ExercicioSeed("Panturrilha sentado", "Panturrilha"),
    ExercicioSeed("Panturrilha no leg press", "Panturrilha"),
    ExercicioSeed(
        "Panturrilha burrinho",
        "Panturrilha",
        "Elevação dos calcanhares com o tronco inclinado à frente e o quadril flexionado. Também chamada de donkey calf raise.",
    ),
)

# Outros nomes usados nas academias para exercícios que já estão no catálogo. Antes de incluir
# um exercício, confira esta lista: cadastrar um sinônimo duplicaria o exercício na biblioteca.
# Os testes garantem que nenhum destes nomes vire um exercício e que todo destino exista.
SINONIMOS: dict[str, str] = {
    # Peito
    "Crucifixo na máquina": "Voador",
    "Chest press": "Supino reto na máquina",
    # Costas
    "Pulley frente": "Puxada frontal na polia",
    "Puxada alta": "Puxada frontal na polia",
    "Pulldown": "Puxada frontal na polia",
    "Remada serrote": "Remada unilateral com halter",
    "Remada sentada na polia": "Remada baixa na polia",
    "Remada T": "Remada cavalinho",
    "Pullover na polia": "Pulldown com braços estendidos na polia",
    "Hiperextensão lombar": "Extensão lombar no banco romano",
    "Remada australiana": "Remada invertida",
    "Deadlift": "Levantamento terra",
    # Pernas: o terra romeno e o stiff diferem só no quanto os joelhos flexionam.
    "Levantamento terra romeno": "Stiff com barra",
    "Flexora deitada": "Mesa flexora",
    "Flexora sentada": "Cadeira flexora",
    "Bom dia": "Good morning com barra",
    "Agachamento plié": "Agachamento sumô com halter",
    "Step-up": "Subida no banco com halteres",
    # Ombros
    "Desenvolvimento militar": "Desenvolvimento com barra",
    "Crucifixo inverso com halteres": "Crucifixo invertido com halteres",
    "Voador invertido": "Crucifixo invertido na máquina",
    # Bíceps e antebraço
    "Rosca inclinada com halteres": "Rosca 45",
    "Farmer's walk": "Caminhada do fazendeiro",
    # Tríceps: a paralela muda só a inclinação do tronco entre peito e tríceps.
    "Paralela para tríceps": "Paralela para peito",
    "Mergulho nas paralelas": "Paralela para peito",
    "Tríceps banco": "Mergulho no banco",
    "Tríceps pulley inverso": "Tríceps pulley com pegada supinada",
    # Core
    "Abdominal supra": "Crunch abdominal",
    "Russian twist": "Rotação russa",
    "Mountain climber": "Escalador",
    # Glúteos
    "Agachamento búlgaro": "Afundo búlgaro",
    "Elevação pélvica com barra": "Hip thrust com barra",
    "Glute bridge": "Ponte de glúteos",
    # Panturrilha
    "Elevação de panturrilha em pé": "Panturrilha em pé",
}
