# Workout Planner

Aplicação web para pesquisar exercícios, montar rotinas de treino personalizadas e exportá-las em planilhas Excel. O projeto é dividido em backend com FastAPI, frontend com Angular e uma camada de seed/scraping para popular a base inicial de exercícios.

## Funcionalidades

- Cadastro e autenticação de usuários com JWT
- Listagem e filtro de exercícios por nome e grupo muscular
- Criação, edição, consulta e remoção de rotinas de treino
- Exportação de rotinas para arquivo `.xlsx`
- Seed automático de exercícios no startup da API

## Tecnologias Utilizadas

### Backend

- Python
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- `python-jose` para autenticação JWT
- `pandas` e `XlsxWriter` para geração de planilhas
- `BeautifulSoup4` / scripts de scraper e seed

### Frontend

- Angular 14
- TypeScript
- Tailwind CSS
- RxJS
- Angular Router

### Ferramentas de apoio

- Uvicorn
- Pytest
- Karma / Jasmine
- npm

## Estrutura do Projeto

```text
workout-planner/
├── backend/
│   ├── app/
│   ├── scraper/
│   ├── alembic/
│   ├── tests/
│   └── requirements.txt
└── frontend/
    ├── src/
    ├── package.json
    └── angular.json
```

## Como Rodar o Projeto Localmente

### 1. Pré-requisitos

Antes de começar, tenha instalado na máquina:

- Python 3
- Node.js e npm
- PostgreSQL

Opcionalmente, você também pode usar Docker apenas para subir o banco local.

### 2. Clone o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd workout-planner
```

### 3. Suba o banco de dados PostgreSQL

Se você já possui um PostgreSQL local, basta criar um banco chamado `workout_planner`.

Exemplo usando Docker:

```bash
docker run --name workout-planner-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=workout_planner \
  -p 5432:5432 \
  -d postgres:16
```

### 4. Configure e rode o backend

Entre na pasta do backend:

```bash
cd backend
```

Crie e ative um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Crie ou ajuste o arquivo `backend/.env` com valores locais:

```env
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/workout_planner"
JWT_SECRET_KEY="troque-esta-chave-por-um-valor-seguro"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Observações importantes:

- Use uma chave JWT própria no ambiente local.
- Evite versionar credenciais reais no repositório.
- O projeto usa PostgreSQL como banco principal.

Execute as migrações:

```bash
alembic upgrade head
```

Inicie a API:

```bash
uvicorn app.main:app --reload
```

Com a API em execução:

- Backend: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- Healthcheck: `http://localhost:8000/health`

Observação: no startup, a API cria as tabelas necessárias e sincroniza um conjunto inicial de exercícios no banco.

### 5. Configure e rode o frontend

Abra um novo terminal e entre na pasta do frontend:

```bash
cd frontend
```

Instale as dependências:

```bash
npm install
```

Inicie a aplicação Angular:

```bash
npm start
```

O frontend ficará disponível em:

```text
http://localhost:4200
```

Por padrão, o frontend já está configurado para consumir a API em `http://localhost:8000/api/v1`.

### 6. Fluxo esperado para desenvolvimento

Com backend e frontend rodando, o fluxo local fica assim:

1. Acesse `http://localhost:4200`
2. Crie uma conta ou faça login
3. Pesquise exercícios e filtre por grupo muscular
4. Monte sua rotina de treino
5. Exporte a rotina para planilha Excel

## Comandos Úteis

### Backend

Rodar testes:

```bash
pytest
```

### Frontend

Rodar testes:

```bash
npm test
```

Gerar build de produção:

```bash
npm run build
```

## Observações

- O CORS do backend está configurado para permitir `http://localhost:4200`.
- O seed inicial de exercícios é executado automaticamente quando a API sobe.
- Para manter o ambiente consistente, prefira usar as migrações do Alembic antes de iniciar o desenvolvimento.
