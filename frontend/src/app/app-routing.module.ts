import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { AuthGuard } from './core/guards/auth.guard';
import { AuthRedirectGuard } from './core/guards/auth-redirect.guard';
import { LoginComponent } from './features/auth/login/login.component';
import { RegisterComponent } from './features/auth/register/register.component';
import { RotinaBuilderComponent } from './features/rotina/rotina-builder/rotina-builder.component';

const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    canActivate: [AuthRedirectGuard],
    component: LoginComponent,
  },
  {
    path: 'login',
    canActivate: [AuthRedirectGuard],
    component: LoginComponent,
  },
  {
    path: 'register',
    canActivate: [AuthRedirectGuard],
    component: RegisterComponent,
  },
  {
    path: 'treino',
    canActivate: [AuthGuard],
    component: RotinaBuilderComponent,
  },
  {
    path: '**',
    redirectTo: '',
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
