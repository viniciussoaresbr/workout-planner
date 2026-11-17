import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { finalize } from 'rxjs';

import { AuthService } from '../../../core/auth/auth.service';
import { getErrorMessage } from '../../../core/http/http-error';
import { ToastService } from '../../../core/notifications/toast.service';
import { FieldError } from '../../../shared/forms/field-error';
import { INPUT_CLASSES } from '../../../shared/forms/form-styles';

/** Limites alinhados às validações da API. */
export const REGISTER_LIMITS = {
  nameMin: 3,
  nameMax: 120,
  passwordMin: 8,
  passwordMax: 128,
} as const;

@Component({
  selector: 'app-register',
  imports: [ReactiveFormsModule, RouterLink, FieldError],
  templateUrl: './register.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Register {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly toast = inject(ToastService);

  protected readonly inputClasses = `${INPUT_CLASSES} focus:border-emerald-400`;
  protected readonly submitting = signal(false);
  protected readonly form = inject(NonNullableFormBuilder).group({
    name: [
      '',
      [
        Validators.required,
        Validators.minLength(REGISTER_LIMITS.nameMin),
        Validators.maxLength(REGISTER_LIMITS.nameMax),
      ],
    ],
    email: ['', [Validators.required, Validators.email]],
    password: [
      '',
      [
        Validators.required,
        Validators.minLength(REGISTER_LIMITS.passwordMin),
        Validators.maxLength(REGISTER_LIMITS.passwordMax),
      ],
    ],
  });

  protected submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    if (this.submitting()) {
      return;
    }

    this.submitting.set(true);
    const { name, email, password } = this.form.getRawValue();
    this.auth
      .register({ name: name.trim(), email, password })
      .pipe(finalize(() => this.submitting.set(false)))
      .subscribe({
        next: () => {
          this.toast.success('Cadastro realizado com sucesso.');
          void this.router.navigate(['/treino']);
        },
        error: (error: unknown) =>
          this.toast.error(getErrorMessage(error, 'Não foi possível concluir o cadastro.')),
      });
  }
}
