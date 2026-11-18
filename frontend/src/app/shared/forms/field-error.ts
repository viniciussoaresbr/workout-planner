import { ChangeDetectionStrategy, Component, computed, effect, input, signal } from '@angular/core';
import { AbstractControl, ValidationErrors } from '@angular/forms';

/** Mensagens padrão para os validadores usados nos formulários. */
export function validationMessage(errors: ValidationErrors | null): string | null {
  if (!errors) {
    return null;
  }
  if (errors['required']) {
    return 'Campo obrigatório.';
  }
  if (errors['email']) {
    return 'Informe um e-mail válido.';
  }
  if (errors['minlength']) {
    return `Use pelo menos ${errors['minlength'].requiredLength} caracteres.`;
  }
  if (errors['maxlength']) {
    return `Use no máximo ${errors['maxlength'].requiredLength} caracteres.`;
  }
  if (errors['edgeWhitespace']) {
    return 'Não use espaços no início ou no fim.';
  }
  if (errors['passwordStrength']) {
    return 'Use pelo menos uma letra e um número.';
  }
  if (errors['mismatch']) {
    return 'As senhas não coincidem.';
  }
  return 'Valor inválido.';
}

/**
 * Linha abaixo do campo com o erro de validação (depois que o usuário interagiu com ele) ou,
 * sem erro, uma dica opcional. A altura é sempre reservada, então o layout não pula quando
 * um erro aparece. O `id` do host serve de alvo para o `aria-describedby` do campo.
 */
@Component({
  selector: 'app-field-error',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: { class: 'block min-h-6 pt-1 text-xs leading-5' },
  template: `
    @if (message(); as text) {
      <p class="text-rose-300" role="alert">{{ text }}</p>
    } @else if (hint()) {
      <p class="text-slate-500">{{ hint() }}</p>
    }
  `,
})
export class FieldError {
  readonly control = input.required<AbstractControl>();
  /** Texto exibido no espaço reservado enquanto não há erro. */
  readonly hint = input<string>();

  /** Incrementado a cada evento do controle (valor, status, touched) para reavaliar a mensagem. */
  private readonly version = signal(0);

  protected readonly message = computed(() => {
    this.version();
    const control = this.control();
    return control.touched ? validationMessage(control.errors) : null;
  });

  constructor() {
    effect(onCleanup => {
      const subscription = this.control().events.subscribe(() => this.version.update(v => v + 1));
      onCleanup(() => subscription.unsubscribe());
    });
  }
}
