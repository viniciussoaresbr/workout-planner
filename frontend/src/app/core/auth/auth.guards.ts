import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { AuthService } from './auth.service';

/** Libera a rota apenas para usuários autenticados. */
export const authGuard: CanActivateFn = () =>
  inject(AuthService).isAuthenticated() || inject(Router).createUrlTree(['/login']);

/** Libera a rota apenas para visitantes (login/cadastro). */
export const guestGuard: CanActivateFn = () =>
  !inject(AuthService).isAuthenticated() || inject(Router).createUrlTree(['/treino']);
