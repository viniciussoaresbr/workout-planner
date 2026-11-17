import { InjectionToken } from '@angular/core';

import { environment } from '../../../environments/environment';

/** URL base da API; injetável para facilitar testes. */
export const API_URL = new InjectionToken<string>('API_URL', {
  providedIn: 'root',
  factory: () => environment.apiUrl,
});

/** Envelope das respostas de sucesso da API. */
export interface ApiResponse<T> {
  message: string;
  data: T;
}

/** Corpo das respostas de erro da API. */
export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    request_id: string;
    details?: unknown;
  };
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
