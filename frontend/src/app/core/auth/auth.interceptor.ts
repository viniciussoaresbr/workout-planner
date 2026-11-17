import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';

import { API_URL } from '../api/api.models';
import { AuthService } from './auth.service';

/** Anexa o token apenas a requisições para a própria API (nunca para terceiros). */
export const authInterceptor: HttpInterceptorFn = (request, next) => {
  const apiUrl = inject(API_URL);
  const token = inject(AuthService).getToken();

  if (!token || !request.url.startsWith(apiUrl)) {
    return next(request);
  }
  return next(request.clone({ setHeaders: { Authorization: `Bearer ${token}` } }));
};
