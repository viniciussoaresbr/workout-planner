import { HttpErrorResponse } from '@angular/common/http';
import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';

import { HttpErrorService } from '../../../core/services/http-error.service';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
})
export class LoginComponent {
  readonly form = this.formBuilder.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(6)]],
  });

  isSubmitting = false;

  constructor(
    private readonly formBuilder: FormBuilder,
    private readonly authService: AuthService,
    private readonly httpErrorService: HttpErrorService,
    private readonly router: Router,
    private readonly toastr: ToastrService,
  ) {}

  submit(): void {
    if (this.form.invalid || this.isSubmitting) {
      this.form.markAllAsTouched();
      return;
    }

    this.isSubmitting = true;

    this.authService.login(this.form.getRawValue()).subscribe({
      next: () => {
        this.toastr.success('Login realizado com sucesso.');
        this.router.navigate(['/treino']);
      },
      error: (error: HttpErrorResponse) => {
        this.toastr.error(
          this.httpErrorService.getMessage(
            error,
            'Nao foi possivel realizar o login.',
          ),
        );
        this.isSubmitting = false;
      },
      complete: () => {
        this.isSubmitting = false;
      },
    });
  }
}
