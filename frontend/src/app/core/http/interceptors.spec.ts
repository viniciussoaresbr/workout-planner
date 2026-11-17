import { HttpClient, provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { TEST_API_URL, fakeJwt } from '../../../testing/jwt';
import { API_URL } from '../api/api.models';
import { authInterceptor } from '../auth/auth.interceptor';
import { AuthService } from '../auth/auth.service';
import { ToastService } from '../notifications/toast.service';
import { skipGlobalErrorHandling } from './http-context';
import { errorInterceptor } from './error.interceptor';

describe('interceptors HTTP', () => {
  let http: HttpClient;
  let backend: HttpTestingController;
  let auth: { getToken: ReturnType<typeof vi.fn>; logout: ReturnType<typeof vi.fn> };
  let toast: { error: ReturnType<typeof vi.fn> };
  let router: { navigate: ReturnType<typeof vi.fn> };
  const token = fakeJwt();

  beforeEach(() => {
    auth = { getToken: vi.fn(() => token), logout: vi.fn() };
    toast = { error: vi.fn() };
    router = { navigate: vi.fn(() => Promise.resolve(true)) };

    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([authInterceptor, errorInterceptor])),
        provideHttpClientTesting(),
        { provide: API_URL, useValue: TEST_API_URL },
        { provide: AuthService, useValue: auth },
        { provide: ToastService, useValue: toast },
        { provide: Router, useValue: router },
      ],
    });
    http = TestBed.inject(HttpClient);
    backend = TestBed.inject(HttpTestingController);
  });

  afterEach(() => backend.verify());

  function apiError(message: string) {
    return { error: { code: 'x', message, request_id: 'r' } };
  }

  describe('authInterceptor', () => {
    it('envia o token para a API', () => {
      http.get(`${TEST_API_URL}/rotinas`).subscribe();

      const request = backend.expectOne(`${TEST_API_URL}/rotinas`);
      expect(request.request.headers.get('Authorization')).toBe(`Bearer ${token}`);
      request.flush({});
    });

    it('não vaza o token para outros domínios', () => {
      http.get('https://outro-site.com/dados').subscribe();

      const request = backend.expectOne('https://outro-site.com/dados');
      expect(request.request.headers.has('Authorization')).toBe(false);
      request.flush({});
    });

    it('não envia cabeçalho quando não há sessão', () => {
      auth.getToken.mockReturnValue(null);
      http.get(`${TEST_API_URL}/exercicios`).subscribe();

      const request = backend.expectOne(`${TEST_API_URL}/exercicios`);
      expect(request.request.headers.has('Authorization')).toBe(false);
      request.flush({});
    });
  });

  describe('errorInterceptor', () => {
    it('exibe a mensagem da API em um toast e repassa o erro', () => {
      const onError = vi.fn();
      http.get(`${TEST_API_URL}/rotinas/1`).subscribe({ error: onError });

      backend
        .expectOne(`${TEST_API_URL}/rotinas/1`)
        .flush(apiError('Rotina não encontrada.'), { status: 404, statusText: 'Not Found' });

      expect(toast.error).toHaveBeenCalledWith('Rotina não encontrada.');
      expect(onError).toHaveBeenCalled();
      expect(auth.logout).not.toHaveBeenCalled();
    });

    it('encerra a sessão e volta ao login em 401', () => {
      http.get(`${TEST_API_URL}/rotinas`).subscribe({ error: () => undefined });

      backend.expectOne(`${TEST_API_URL}/rotinas`).flush(apiError('Token inválido ou expirado.'), {
        status: 401,
        statusText: 'Unauthorized',
      });

      expect(auth.logout).toHaveBeenCalled();
      expect(router.navigate).toHaveBeenCalledWith(['/login']);
      expect(toast.error).toHaveBeenCalledWith('Token inválido ou expirado.');
    });

    it('não interfere quando a requisição pede para tratar o próprio erro', () => {
      http
        .post(`${TEST_API_URL}/auth/login`, {}, { context: skipGlobalErrorHandling() })
        .subscribe({ error: () => undefined });

      backend
        .expectOne(`${TEST_API_URL}/auth/login`)
        .flush(apiError('Credenciais inválidas.'), { status: 401, statusText: 'Unauthorized' });

      expect(toast.error).not.toHaveBeenCalled();
      expect(auth.logout).not.toHaveBeenCalled();
    });

    it('lê a mensagem de erro de respostas Blob (download de planilha)', async () => {
      const onError = vi.fn();
      http
        .post(`${TEST_API_URL}/planilha/export`, {}, { responseType: 'blob' })
        .subscribe({ error: onError });

      const body = new Blob([JSON.stringify(apiError('Rotina não encontrada.'))], {
        type: 'application/json',
      });
      backend
        .expectOne(`${TEST_API_URL}/planilha/export`)
        .flush(body, { status: 404, statusText: 'Not Found' });

      await vi.waitFor(() => expect(onError).toHaveBeenCalled());
      expect(toast.error).toHaveBeenCalledWith('Rotina não encontrada.');
      expect(onError.mock.calls[0][0].error).toEqual(apiError('Rotina não encontrada.'));
    });
  });
});
