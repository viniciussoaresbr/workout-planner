import { HttpContext, HttpContextToken } from '@angular/common/http';

/**
 * Quando verdadeiro, o interceptor global não exibe toast nem redireciona em 401:
 * quem fez a requisição trata o erro (ex.: formulário de login).
 */
export const SKIP_GLOBAL_ERROR_HANDLING = new HttpContextToken<boolean>(() => false);

export function skipGlobalErrorHandling(): HttpContext {
  return new HttpContext().set(SKIP_GLOBAL_ERROR_HANDLING, true);
}
