import { Injectable, signal } from '@angular/core';

export interface ConfirmOptions {
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  /** `danger` destaca ações destrutivas (ex.: excluir). */
  tone?: 'default' | 'danger';
}

export interface ConfirmRequest extends Required<ConfirmOptions> {
  resolve(confirmed: boolean): void;
}

/**
 * Ponto único para confirmações do usuário. O `ConfirmDialog` (montado no componente raiz)
 * exibe a solicitação atual; quem chama recebe uma Promise com a resposta.
 */
@Injectable({ providedIn: 'root' })
export class ConfirmService {
  private readonly _request = signal<ConfirmRequest | null>(null);
  readonly request = this._request.asReadonly();

  ask(options: ConfirmOptions): Promise<boolean> {
    // Uma nova pergunta cancela a anterior, se houver.
    this._request()?.resolve(false);
    return new Promise(resolve => {
      this._request.set({
        confirmLabel: 'Confirmar',
        cancelLabel: 'Cancelar',
        tone: 'default',
        ...options,
        resolve: confirmed => {
          this._request.set(null);
          resolve(confirmed);
        },
      });
    });
  }
}
