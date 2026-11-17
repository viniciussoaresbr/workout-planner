import { HttpClient } from '@angular/common/http';
import { Injectable, inject, signal } from '@angular/core';
import { Observable, map, tap } from 'rxjs';

import { API_URL, ApiResponse } from '../api/api.models';
import { skipGlobalErrorHandling } from '../http/http-context';
import { CurrentUser, LoginCredentials, RegisterData, TokenResponse } from './auth.models';
import { isTokenValid } from './jwt';
import { TokenStorage } from './token-storage';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly storage = inject(TokenStorage);
  private readonly authUrl = `${inject(API_URL)}/auth`;

  private readonly token = signal<string | null>(this.storage.read());

  /** Token atual, ou `null` se ausente ou expirado. */
  getToken(): string | null {
    const token = this.token();
    return isTokenValid(token) ? token : null;
  }

  isAuthenticated(): boolean {
    return this.getToken() !== null;
  }

  login(credentials: LoginCredentials): Observable<void> {
    return this.authenticate(`${this.authUrl}/login`, credentials);
  }

  register(data: RegisterData): Observable<void> {
    return this.authenticate(`${this.authUrl}/register`, data);
  }

  currentUser(): Observable<CurrentUser> {
    return this.http
      .get<ApiResponse<CurrentUser>>(`${this.authUrl}/me`)
      .pipe(map(response => response.data));
  }

  logout(): void {
    this.storage.clear();
    this.token.set(null);
  }

  private authenticate(url: string, body: LoginCredentials | RegisterData): Observable<void> {
    // Os formulários exibem o próprio erro (ex.: "Credenciais inválidas.").
    return this.http
      .post<ApiResponse<TokenResponse>>(url, body, { context: skipGlobalErrorHandling() })
      .pipe(
        tap(({ data }) => {
          this.storage.write(data.access_token);
          this.token.set(data.access_token);
        }),
        map(() => undefined),
      );
  }
}
