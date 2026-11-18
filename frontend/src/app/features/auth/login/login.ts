import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
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
  selector: 'app-login',
  imports: [ReactiveFormsModule, RouterLink, FieldError, PasswordToggle, AuthLayout],
  templateUrl: './login.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Login {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly toast = inject(ToastService);

  protected readonly submitting = signal(false);
  protected readonly form = inject(NonNullableFormBuilder).group({
    email: [
      '',
      [
        AppValidators.requiredTrimmed,
        AppValidators.email,
        Validators.maxLength(AUTH_LIMITS.emailMax),
      ],
    ],
    password: ['', [Validators.required, Validators.maxLength(AUTH_LIMITS.passwordMax)]],
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
    const { email, password } = this.form.getRawValue();
    this.auth
      .login({ email: email.trim(), password })
      .pipe(finalize(() => this.submitting.set(false)))
      .subscribe({
        next: () => {
          this.toast.success('Login realizado com sucesso.');
          void this.router.navigate(['/treino']);
        },
        error: (error: unknown) =>
          this.toast.error(getErrorMessage(error, 'Não foi possível realizar o login.')),
      });
  }
}
