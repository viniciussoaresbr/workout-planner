# Workout Planner

Aplicação web para montar rotinas de treino personalizadas e exportá-las em planilha Excel ou PDF. O projeto é dividido em backend com FastAPI, frontend com Angular e um seed para popular a base inicial de exercícios.

![Home](./frontend/src/app/assets/screenshots/rotina.png)
<div align="center">
  <img src="./frontend/src/app/assets/screenshots/login.png" width="32%" alt="Login" />
  <img src="./frontend/src/app/assets/screenshots/sem-rotina.png" width="32%" alt="NoRoutine" />
  <img src="./frontend/src/app/assets/screenshots/drag-and-drop.png" width="32%" alt="DragAndDrop" />
</div>

## Funcionalidades

- Cadastro e autenticação de usuários com JWT
- Listagem e filtro de exercícios por nome e grupo muscular
- Criação, edição, consulta e remoção de rotinas de treino
- Exportação de rotinas para planilha `.xlsx` ou documento `.pdf`
- Seed idempotente do catálogo de exercícios (`python -m app.seed`)

## Tecnologias Utilizadas

### Backend

- Python 3.12+
- FastAPI + Pydantic v2
- SQLAlchemy 2 + Alembic
- PostgreSQL (driver `psycopg` 3)
- `PyJWT` para tokens JWT e `pwdlib` (Argon2) para hash de senhas
- `XlsxWriter` para geração de planilhas e `ReportLab` para geração de PDF

### Frontend

- Angular 22 (componentes standalone, signals, sem zone.js)
- TypeScript 6
- Tailwind CSS 4
- Angular CDK (drag and drop)
- RxJS

### Ferramentas de apoio

- Uvicorn
- Pytest
- Ruff (lint e formatação)
- Vitest
- Prettier
- npm

## Como Rodar o Projeto Localmente

### 1. Pré-requisitos

Antes de começar, tenha instalado na máquina:

- Python 3.12+
- Node.js 24.15+ (há um `.nvmrc` em `frontend/`; com nvm, basta `nvm use`) e npm
- PostgreSQL

Opcionalmente, você também pode usar Docker apenas para subir o banco local.

### 2. Clone o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd workout-planner
```

### 3. Suba o banco de dados PostgreSQL

O `compose.yaml` na raiz do projeto sobe um PostgreSQL 18 com volume persistente e healthcheck:

```bash
docker compose up -d db
docker compose ps        # aguarde o status "healthy"
```

O banco fica acessível apenas em `localhost:5433` (porta escolhida para não conflitar com um PostgreSQL local na 5432), com usuário `postgres`, senha `postgres` e banco `workout_planner`. Esses valores podem ser alterados pelas variáveis `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` e `POSTGRES_PORT` (por exemplo, em um arquivo `.env` na raiz).

Outros comandos úteis:

```bash
docker compose logs -f db                                    # logs do banco
docker compose exec db psql -U postgres -d workout_planner   # console SQL
docker compose down                                          # para o banco (mantém os dados)
docker compose down -v                                       # para e APAGA os dados
```

### 4. Configure e rode o backend

Entre na pasta do backend, crie o ambiente virtual e instale as dependências:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt   # ou requirements.txt para apenas executar
```

Crie o arquivo `backend/.env` a partir do exemplo e ajuste os valores:

```bash
cp .env.example .env
```

| Variável | Descrição |
| --- | --- |
| `DATABASE_URL` | URL do PostgreSQL (`postgresql://...` usa o driver psycopg 3 automaticamente) |
| `ENVIRONMENT` | `development`, `test` ou `production`. Em `production`, `/docs`, `/redoc` e `/openapi.json` ficam desativados |
| `JWT_SECRET_KEY` | Segredo do JWT, com no mínimo 32 caracteres e aleatório. Gere com `python -c "import secrets; print(secrets.token_urlsafe(48))"`; a API não inicia com o valor de exemplo |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Validade do token (padrão: 60) |
| `CORS_ORIGINS` | Lista JSON de origens permitidas (padrão: `["http://localhost:4200"]`). Em `production`, só aceita origens `https://` |
| `LOGIN_RATE_LIMIT_PER_MINUTE` | Tentativas de login por IP por minuto (padrão: 20) |
| `LOGIN_FAILURE_LIMIT` | Falhas de login por e-mail vindas de um mesmo IP a cada 15 minutos antes do bloqueio temporário daquele IP (padrão: 10). O dono da conta continua entrando de outro IP |
| `LOGIN_ACCOUNT_FAILURE_LIMIT` | Falhas de login por e-mail somando todos os IPs a cada hora antes do bloqueio temporário da conta, contra força bruta distribuída (padrão: 100) |
| `REGISTER_RATE_LIMIT_PER_HOUR` | Cadastros por IP por hora (padrão: 10) |
| `PASSWORD_HASH_CONCURRENCY` | Hashes de senha (Argon2, ~64 MiB cada) executados ao mesmo tempo (padrão: 4) |

Os limites de tentativas ficam em memória e valem por processo: com vários workers ou réplicas, cada um conta separadamente. Atrás de um proxy reverso, inicie o uvicorn com `--proxy-headers --forwarded-allow-ips=<ip do proxy>` para que os limites usem o IP real do cliente, e não o do proxy.

Aplique as migrações e popule o catálogo de exercícios (o seed é idempotente e pode ser executado novamente sempre que o catálogo mudar):

```bash
alembic upgrade head
python -m app.seed
```

Inicie a API:

```bash
uvicorn app.main:app --reload
```

Com a API em execução:

- Backend: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs` (desativado com `ENVIRONMENT=production`)
- Health checks: `GET /health` (processo no ar) e `GET /health/ready` (verifica o banco)

### 5. Configure e rode o frontend

Abra um novo terminal e entre na pasta do frontend:

```bash
cd frontend
nvm use   # opcional: seleciona a versão do Node definida em .nvmrc
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

Em desenvolvimento (`npm start`), o frontend consome a API em `http://localhost:8000/api/v1` (`src/environments/environment.ts`). O build de produção (`npm run build`) usa `src/environments/environment.prod.ts`, que aponta para `/api/v1` no mesmo domínio do frontend (veja [Produção](#produção)).

### 6. Fluxo esperado para desenvolvimento

Com backend e frontend rodando, o fluxo local fica assim:

1. Acesse `http://localhost:4200`
2. Crie uma conta ou faça login
3. Pesquise exercícios e filtre por grupo muscular
4. Monte sua rotina de treino
5. Exporte a rotina para planilha Excel ou PDF

## Comandos Úteis

### Backend

Dentro de `backend/`, com o ambiente virtual ativo:

```bash
pytest                 # testes (usam SQLite em memória, não precisam de banco)
ruff check .           # lint
ruff format .          # formatação
alembic check          # confere se os modelos estão em sincronia com as migrações
```

### Frontend

Dentro de `frontend/`:

```bash
npm test               # testes unitários (Vitest)
npm run build          # build de produção em dist/
npm run format         # formata o código com Prettier
npm run format:check   # confere a formatação (útil em CI)
```

## Produção

Sem HTTPS, a senha e o token trafegam em texto puro. Em produção, sirva o frontend e a API pelo mesmo domínio, atrás de um proxy reverso com TLS:

- `ENVIRONMENT=production` desativa a documentação interativa, ativa o cabeçalho HSTS na API e exige origens `https://` em `CORS_ORIGINS`.
- O build de produção chama a API em `/api/v1`, que herda o `https://` da página e dispensa CORS. Para hospedar a API em outro domínio, troque `apiUrl` em `environment.prod.ts` pela URL completa com `https://` e libere a origem do frontend em `CORS_ORIGINS`.
- Inicie o uvicorn com `--proxy-headers --forwarded-allow-ips=<ip do proxy>` para que os limites de tentativas usem o IP real do cliente.

A API já envia os próprios cabeçalhos de segurança (`Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy` e, em produção, `Strict-Transport-Security`). O build do frontend embute uma CSP para scripts (`security.autoCsp` em `angular.json`), mas os demais cabeçalhos da página precisam vir do servidor web. Exemplo com nginx:

```nginx
server {
    listen 443 ssl;
    server_name treino.example.com;
    # ssl_certificate / ssl_certificate_key: ex.: certificados do Let's Encrypt

    root /srv/workout-planner/frontend/dist/frontend/browser;

    location / {
        try_files $uri $uri/ /index.html;
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-Frame-Options "DENY" always;
        add_header Referrer-Policy "no-referrer" always;
        add_header Content-Security-Policy "frame-ancestors 'none'" always;
    }

    # A API define os próprios cabeçalhos de segurança.
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name treino.example.com;
    return 301 https://$host$request_uri;
}
```

## Observações

- O CORS do backend está configurado para permitir `http://localhost:4200`.
- A API não cria tabelas nem executa o seed ao subir: use `alembic upgrade head` e `python -m app.seed`.
- Para manter o ambiente consistente, prefira usar as migrações do Alembic antes de iniciar o desenvolvimento.
