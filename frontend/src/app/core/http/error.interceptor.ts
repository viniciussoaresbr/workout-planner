import { HttpErrorResponse, HttpInterceptorFn, HttpStatusCode } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, catchError, from, switchMap, throwError } from 'rxjs';

import { AuthService } from '../auth/auth.service';
import { ToastService } from '../notifications/toast.service';
import { SKIP_GLOBAL_ERROR_HANDLING } from './http-context';
import { getErrorMessage } from './http-error';

/**
 * Tratamento global de erros HTTP:
 * - converte corpos de erro JSON recebidos como Blob (ex.: download de planilha);
 * - em 401, encerra a sessão e volta para o login;
 * - nos demais casos, exibe a mensagem da API em um toast.
 */
export const errorInterceptor: HttpInterceptorFn = (request, next) => {
  const auth = inject(AuthService);
  const router = inject(Router);
  const toast = inject(ToastService);
  const skipGlobalHandling = request.context.get(SKIP_GLOBAL_ERROR_HANDLING);

  return next(request).pipe(
    catchError((error: unknown) =>
      parseBlobError(error).pipe(
        switchMap(parsed => {
          if (!skipGlobalHandling && parsed instanceof HttpErrorResponse) {
            if (parsed.status === HttpStatusCode.Unauthorized) {
              auth.logout();
              toast.error(getErrorMessage(parsed));
              void router.navigate(['/login']);
            } else {
              toast.error(getErrorMessage(parsed));
            }
          }
          return throwError(() => parsed);
        }),
      ),
    ),
  );
};

function parseBlobError(error: unknown): Observable<unknown> {
  const isJsonBlob =
    error instanceof HttpErrorResponse &&
    error.error instanceof Blob &&
    error.error.type.includes('json');
  if (!isJsonBlob) {
    return from([error]);
  }
  return from(
    (error.error as Blob).text().then(
      text =>
        new HttpErrorResponse({
          error: safeJsonParse(text),
          headers: error.headers,
          status: error.status,
          statusText: error.statusText,
          url: error.url ?? undefined,
        }),
      () => error,
    ),
  );
}

function safeJsonParse(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}
