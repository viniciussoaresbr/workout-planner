import { Routes } from '@angular/router';

import { authGuard, guestGuard } from './core/auth/auth.guards';

const APP_NAME = 'Workout Planner';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'treino' },
  {
    path: 'login',
    title: `Entrar · ${APP_NAME}`,
    canActivate: [guestGuard],
    loadComponent: () => import('./features/auth/login/login').then(m => m.Login),
  },
  {
    path: 'register',
    title: `Criar conta · ${APP_NAME}`,
    canActivate: [guestGuard],
    loadComponent: () => import('./features/auth/register/register').then(m => m.Register),
  },
  {
    path: 'treino',
    title: `Rotina de treino · ${APP_NAME}`,
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/rotina/rotina-builder/rotina-builder').then(m => m.RotinaBuilder),
  },
  { path: '**', redirectTo: 'treino' },
];
