import { Injectable, signal } from '@angular/core';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: number;
  type: ToastType;
  message: string;
}

const DURATION_MS: Readonly<Record<ToastType, number>> = {
  success: 3_000,
  info: 3_000,
  warning: 4_000,
  error: 5_000,
};

const MAX_VISIBLE = 4;

@Injectable({ providedIn: 'root' })
export class ToastService {
  private readonly _toasts = signal<readonly Toast[]>([]);
  private nextId = 1;

  readonly toasts = this._toasts.asReadonly();

  success(message: string): void {
    this.show('success', message);
  }

  error(message: string): void {
    this.show('error', message);
  }

  warning(message: string): void {
    this.show('warning', message);
  }

  info(message: string): void {
    this.show('info', message);
  }

  dismiss(id: number): void {
    this._toasts.update(toasts => toasts.filter(toast => toast.id !== id));
  }

  private show(type: ToastType, message: string): void {
    // Evita empilhar a mesma mensagem (ex.: várias requisições falhando juntas).
    if (this._toasts().some(toast => toast.type === type && toast.message === message)) {
      return;
    }
    const toast: Toast = { id: this.nextId++, type, message };
    this._toasts.update(toasts => [...toasts, toast].slice(-MAX_VISIBLE));
    setTimeout(() => this.dismiss(toast.id), DURATION_MS[type]);
  }
}
