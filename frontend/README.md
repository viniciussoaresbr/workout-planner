# Workout Planner — Frontend

Aplicação Angular 22 (standalone, signals, sem zone.js) com Tailwind CSS 4.
Instruções completas de execução no [README principal](../README.md).

## Comandos

```bash
nvm use              # Node definido em .nvmrc (Angular 22 exige Node 24.15+)
npm install
npm start            # http://localhost:4200
npm test             # testes unitários (Vitest)
npm run build        # build de produção em dist/
npm run format       # Prettier
```

A URL da API fica em `src/environments/environment.ts`.

## Estrutura

```
src/app/
  core/                      Infraestrutura usada pela aplicação inteira
    api/                     Envelope de resposta da API e token API_URL
    auth/                    AuthService, guards, interceptor do token, leitura de JWT
    http/                    Interceptor global de erros e extração de mensagens
    notifications/           Toasts (serviço com signals + contêiner)
  shared/                    Peças reutilizáveis sem regra de negócio
    forms/                   Exibição de erros de validação
    utils/                   Confirmação e download de arquivos
  features/
    auth/                    Telas de login e cadastro
    rotina/
      data/                  Modelos, DTOs da API, mapeamento e clientes HTTP
      state/                 RotinaEditorStore: estado e regras do editor (signals)
      rotina-builder/        Página: compõe os componentes e liga o drag and drop ao store
      exercicio-library/     Biblioteca com filtro por grupo muscular e busca
      dia-treino/            Card de um dia com séries/repetições editáveis
      rotinas-salvas/        Faixa de cards das rotinas salvas
src/testing/                 Utilitários e dados de teste
```

### Convenções

- **Estado**: a página fornece o `RotinaEditorStore`; os componentes filhos são
  apresentacionais (`input()`/`output()`) e não acessam a API diretamente — exceto a
  biblioteca, que é autocontida.
- **Erros HTTP**: o `errorInterceptor` exibe a mensagem enviada pela API e encerra a sessão
  em 401. Requisições que tratam o próprio erro usam `skipGlobalErrorHandling()`.
- **Componentes**: `ChangeDetectionStrategy.OnPush`, controle de fluxo nativo
  (`@if`/`@for`) e rotas com `loadComponent` (carregamento sob demanda).
