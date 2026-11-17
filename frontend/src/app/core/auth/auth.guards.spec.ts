import { TestBed } from '@angular/core/testing';
import {
  ActivatedRouteSnapshot,
  CanActivateFn,
  Router,
  RouterStateSnapshot,
  UrlTree,
} from '@angular/router';

import { authGuard, guestGuard } from './auth.guards';
import { AuthService } from './auth.service';

describe('guards de autenticação', () => {
  function run(guard: CanActivateFn, authenticated: boolean): boolean | UrlTree {
    TestBed.configureTestingModule({
      providers: [{ provide: AuthService, useValue: { isAuthenticated: () => authenticated } }],
    });
    return TestBed.runInInjectionContext(
      () => guard({} as ActivatedRouteSnapshot, {} as RouterStateSnapshot) as boolean | UrlTree,
    );
  }

  function urlOf(result: boolean | UrlTree): string {
    return TestBed.inject(Router).serializeUrl(result as UrlTree);
  }

  it('authGuard libera usuário autenticado', () => {
    expect(run(authGuard, true)).toBe(true);
  });

  it('authGuard manda visitante para o login', () => {
    expect(urlOf(run(authGuard, false))).toBe('/login');
  });

  it('guestGuard libera visitante', () => {
    expect(run(guestGuard, false)).toBe(true);
  });

  it('guestGuard manda usuário autenticado para o treino', () => {
    expect(urlOf(run(guestGuard, true))).toBe('/treino');
  });
});
