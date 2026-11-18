import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { finalize } from 'rxjs';

import { AuthService } from '../../../core/auth/auth.service';
import { getErrorMessage } from '../../../core/http/http-error';
import { ToastService } from '../../../core/notifications/toast.service';
import { FieldError } from '../../../shared/forms/field-error';
import { PasswordToggle } from '../../../shared/forms/password-toggle';
import { AppValidators } from '../../../shared/forms/validators';
import { AuthLayout } from '../auth-layout';
import { AUTH_LIMITS } from '../auth-limits';

@Component({
  selector: 'app-register',
  imports: [ReactiveFormsModule, RouterLink, FieldError, PasswordToggle, AuthLayout],
  templateUrl: './register.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Register {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly toast = inject(ToastService);

  protected readonly passwordHint = `Mínimo de ${AUTH_LIMITS.passwordMin} caracteres, com letras e números.`;
  protected readonly submitting = signal(false);
  protected readonly form = inject(NonNullableFormBuilder).group({
    name: [
      '',
      [
        AppValidators.requiredTrimmed,
        AppValidators.minLengthTrimmed(AUTH_LIMITS.nameMin),
        Validators.maxLength(AUTH_LIMITS.nameMax),
      ],
    ],
    email: [
      '',
      [
        AppValidators.requiredTrimmed,
        AppValidators.email,
        Validators.maxLength(AUTH_LIMITS.emailMax),
      ],
    ],
    password: [
      '',
      [
        Validators.required,
        Validators.minLength(AUTH_LIMITS.passwordMin),
        Validators.maxLength(AUTH_LIMITS.passwordMax),
        AppValidators.noEdgeWhitespace,
        AppValidators.passwordStrength,
      ],
    ],
    confirmPassword: ['', [Validators.required, AppValidators.matches('password')]],
  });

  constructor() {
    // A confirmação depende da senha: revalida quando a senha muda.
    const { password, confirmPassword } = this.form.controls;
    password.valueChanges
      .pipe(takeUntilDestroyed())
      .subscribe(() => confirmPassword.updateValueAndValidity());
  }

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
      .register({ name: name.trim(), email: email.trim(), password })
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
