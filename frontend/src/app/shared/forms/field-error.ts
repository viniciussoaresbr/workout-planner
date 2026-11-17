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
  return 'Valor inválido.';
}

/** Exibe o erro de validação de um controle depois que o usuário interagiu com ele. */
@Component({
  selector: 'app-field-error',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (message(); as text) {
      <p class="mt-2 text-xs text-rose-300" [id]="id()" role="alert">{{ text }}</p>
    }
  `,
})
export class FieldError {
  readonly control = input.required<AbstractControl>();
  readonly id = input<string>();

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
