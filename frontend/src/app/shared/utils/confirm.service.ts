import { Injectable } from '@angular/core';

/**
 * Ponto único para confirmações do usuário. Hoje usa o diálogo nativo; pode ser trocado
 * por um modal próprio sem alterar quem chama.
 */
@Injectable({ providedIn: 'root' })
export class ConfirmService {
  ask(message: string): boolean {
    return window.confirm(message);
  }
}
