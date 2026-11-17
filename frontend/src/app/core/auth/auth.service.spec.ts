import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { TEST_API_URL, fakeJwt } from '../../../testing/jwt';
import { API_URL } from '../api/api.models';
import { SKIP_GLOBAL_ERROR_HANDLING } from '../http/http-context';
import { AuthService } from './auth.service';
import { TokenStorage } from './token-storage';

describe('AuthService', () => {
  let http: HttpTestingController;

  function setup(storedToken: string | null = null): AuthService {
    localStorage.clear();
    if (storedToken) {
      localStorage.setItem('workout_planner_token', storedToken);
    }
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: API_URL, useValue: TEST_API_URL },
      ],
    });
    http = TestBed.inject(HttpTestingController);
    return TestBed.inject(AuthService);
  }

  afterEach(() => {
    http.verify();
    localStorage.clear();
  });

  it('restaura a sessão a partir de um token válido salvo', () => {
    const token = fakeJwt();
    const auth = setup(token);

    expect(auth.isAuthenticated()).toBe(true);
    expect(auth.getToken()).toBe(token);
  });

  it('ignora token salvo expirado', () => {
    const auth = setup(fakeJwt(-60));

    expect(auth.isAuthenticated()).toBe(false);
    expect(auth.getToken()).toBeNull();
  });

  it('faz login, persiste o token e não aciona o tratamento global de erro', () => {
    const auth = setup();
    const token = fakeJwt();
    const done = vi.fn();

    auth.login({ email: 'ana@example.com', password: 'segredo' }).subscribe(done);

    const request = http.expectOne(`${TEST_API_URL}/auth/login`);
    expect(request.request.body).toEqual({ email: 'ana@example.com', password: 'segredo' });
    expect(request.request.context.get(SKIP_GLOBAL_ERROR_HANDLING)).toBe(true);
    request.flush({ message: 'ok', data: { access_token: token, token_type: 'bearer' } });

    expect(done).toHaveBeenCalled();
    expect(auth.getToken()).toBe(token);
    expect(TestBed.inject(TokenStorage).read()).toBe(token);
  });

  it('cadastra com os campos esperados pela API', () => {
    const auth = setup();

    auth.register({ name: 'Ana', email: 'ana@example.com', password: 'segredo123' }).subscribe();

    const request = http.expectOne(`${TEST_API_URL}/auth/register`);
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({
      name: 'Ana',
      email: 'ana@example.com',
      password: 'segredo123',
    });
    request.flush({ message: 'ok', data: { access_token: fakeJwt(), token_type: 'bearer' } });
    expect(auth.isAuthenticated()).toBe(true);
  });

  it('logout limpa o token da memória e do armazenamento', () => {
    const auth = setup(fakeJwt());

    auth.logout();

    expect(auth.isAuthenticated()).toBe(false);
    expect(localStorage.getItem('workout_planner_token')).toBeNull();
  });
});
