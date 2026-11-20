/**
 * Build de produção (`npm run build`). A URL é relativa: a API é servida pelo mesmo domínio
 * do frontend, atrás do proxy reverso com HTTPS. Assim as requisições herdam o `https://` da
 * página e o navegador não precisa de CORS. Para uma API em outro domínio, use a URL
 * completa com `https://`.
 */
export const environment = {
  apiUrl: '/api/v1',
};
