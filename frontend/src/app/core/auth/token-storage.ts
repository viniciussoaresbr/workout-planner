import { Injectable } from '@angular/core';

const TOKEN_KEY = 'workout_planner_token';

/** Persistência do token. Falhas do localStorage (ex.: modo privado) não quebram a aplicação. */
@Injectable({ providedIn: 'root' })
export class TokenStorage {
  read(): string | null {
    try {
      return localStorage.getItem(TOKEN_KEY);
    } catch {
      return null;
    }
  }

  write(token: string): void {
    try {
      localStorage.setItem(TOKEN_KEY, token);
    } catch {
      // Sem persistência a sessão continua válida enquanto a aba estiver aberta.
    }
  }

  clear(): void {
    try {
      localStorage.removeItem(TOKEN_KEY);
    } catch {
      // Nada a limpar.
    }
  }
}
