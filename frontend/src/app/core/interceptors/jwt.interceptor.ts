import {
  HttpErrorResponse,
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
} from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { Observable, catchError, throwError } from 'rxjs';

import { BYPASS_GLOBAL_ERROR_HANDLER } from '../tokens/http-context.tokens';
import { HttpErrorService } from '../services/http-error.service';
import { AuthService } from '../services/auth.service';

@Injectable()
export class JwtInterceptor implements HttpInterceptor {
  constructor(
    private readonly authService: AuthService,
    private readonly router: Router,
    private readonly toastr: ToastrService,
    private readonly httpErrorService: HttpErrorService,
  ) {}

  intercept(
    request: HttpRequest<unknown>,
    next: HttpHandler,
  ): Observable<HttpEvent<unknown>> {
    const token = this.authService.getToken();
    const shouldBypassGlobalHandler = request.context.get(
      BYPASS_GLOBAL_ERROR_HANDLER,
    );
    const isAuthRequest = request.url.includes('/auth/login')
      || request.url.includes('/auth/register');

    const requestWithAuth = token
      ? request.clone({
          setHeaders: {
            Authorization: `Bearer ${token}`,
          },
        })
      : request;

    return next.handle(requestWithAuth).pipe(
      catchError((error: HttpErrorResponse) => {
        if (shouldBypassGlobalHandler) {
          return throwError(() => error);
        }

        if ((error.status === 401 || error.status === 403) && !isAuthRequest) {
          this.authService.logout();
          this.toastr.error(this.httpErrorService.getMessage(error));
          this.router.navigate(['/login']);
          return throwError(() => error);
        }

        this.toastr.error(this.httpErrorService.getMessage(error));
        return throwError(() => error);
      }),
    );
  }
}
