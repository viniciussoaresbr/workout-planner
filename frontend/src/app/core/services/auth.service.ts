import { HttpClient, HttpContext } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, map, tap } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  AuthCredentials,
  AuthResponse,
  CurrentUserResponse,
  RegisterPayload,
} from '../models/auth.models';
import { ApiSuccessResponse } from '../models/api.models';
import { BYPASS_GLOBAL_ERROR_HANDLER } from '../tokens/http-context.tokens';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly tokenStorageKey = 'workout_planner_token';
  private readonly authUrl = `${environment.apiUrl}/auth`;

  constructor(private readonly http: HttpClient) {}

  login(credentials: AuthCredentials): Observable<AuthResponse> {
    return this.http
      .post<ApiSuccessResponse<AuthResponse>>(`${this.authUrl}/login`, credentials, {
        context: new HttpContext().set(BYPASS_GLOBAL_ERROR_HANDLER, true),
      })
      .pipe(
        map((response) => response.data),
        tap((response) => this.persistToken(response)),
      );
  }

  register(payload: RegisterPayload): Observable<AuthResponse> {
    return this.http
      .post<ApiSuccessResponse<AuthResponse>>(`${this.authUrl}/register`, payload, {
        context: new HttpContext().set(BYPASS_GLOBAL_ERROR_HANDLER, true),
      })
      .pipe(
        map((response) => response.data),
        tap((response) => this.persistToken(response)),
      );
  }

  logout(): void {
    localStorage.removeItem(this.tokenStorageKey);
  }

  isLoggedIn(): boolean {
    return this.isTokenValid(this.getToken());
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenStorageKey);
  }

  isTokenValid(token: string | null): boolean {
    if (!token) {
      return false;
    }

    const payload = this.decodeJwtPayload(token);

    if (!payload || typeof payload.exp !== 'number') {
      return false;
    }

    return payload.exp * 1000 > Date.now();
  }

  getCurrentUserName(): Observable<string | null> {
    return this.http
      .get<ApiSuccessResponse<CurrentUserResponse>>(`${this.authUrl}/me`)
      .pipe(map((response) => response.data.name ?? response.data.nome ?? null));
  }

  private persistToken(response: AuthResponse): void {
    const token = response.access_token ?? response.token;

    if (token) {
      localStorage.setItem(this.tokenStorageKey, token);
    }
  }

  private decodeJwtPayload(token: string): { exp?: number } | null {
    try {
      const [, payload] = token.split('.');

      if (!payload) {
        return null;
      }

      const normalized = payload.replace(/-/g, '+').replace(/_/g, '/');
      const decodedPayload = atob(normalized);

      return JSON.parse(decodedPayload) as { exp?: number };
    } catch {
      return null;
    }
  }
}
