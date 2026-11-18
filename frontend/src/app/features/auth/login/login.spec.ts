import { HttpErrorResponse } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { Router, provideRouter } from '@angular/router';
import { of, throwError } from 'rxjs';

import { AuthService } from '../../../core/auth/auth.service';
import { ToastService } from '../../../core/notifications/toast.service';
import { Login } from './login';

describe('Login', () => {
  let auth: { login: ReturnType<typeof vi.fn> };
  let toast: { success: ReturnType<typeof vi.fn>; error: ReturnType<typeof vi.fn> };

  async function render() {
    auth = { login: vi.fn(() => of(undefined)) };
    toast = { success: vi.fn(), error: vi.fn() };
    TestBed.configureTestingModule({
      imports: [Login],
      providers: [
        provideRouter([]),
        { provide: AuthService, useValue: auth },
        { provide: ToastService, useValue: toast },
      ],
    });
    const fixture = TestBed.createComponent(Login);
    await fixture.whenStable();
    const element = fixture.nativeElement as HTMLElement;
    return {
      fixture,
      element,
      type(selector: string, value: string) {
        const input = element.querySelector<HTMLInputElement>(selector)!;
        input.value = value;
        input.dispatchEvent(new Event('input'));
      },
      async submit() {
        element.querySelector<HTMLButtonElement>('button[type=submit]')!.click();
        await fixture.whenStable();
      },
    };
  }

  it('mostra os erros de validação e não chama a API com o formulário inválido', async () => {
    const page = await render();

    await page.submit();

    expect(auth.login).not.toHaveBeenCalled();
    const errors = [...page.element.querySelectorAll('[role=alert]')].map(e =>
      e.textContent?.trim(),
    );
    expect(errors).toEqual(['Campo obrigatório.', 'Campo obrigatório.']);
  });

  it('reserva o espaço do erro abaixo de cada campo mesmo sem erro', async () => {
    const page = await render();

    const slots = page.element.querySelectorAll('app-field-error');
    expect(slots).toHaveLength(2);
    for (const slot of slots) {
      expect(slot.classList).toContain('min-h-6');
      expect(slot.querySelector('[role=alert]')).toBeNull();
    }
  });

  it('rejeita e-mail sem domínio completo', async () => {
    const page = await render();

    page.type('#login-email', 'ana@exemplo');
    page.type('#login-password', 'segredo');
    await page.submit();

    expect(auth.login).not.toHaveBeenCalled();
    expect(page.element.querySelector('#login-email-error')?.textContent?.trim()).toBe(
      'Informe um e-mail válido.',
    );
  });

  it('alterna a visibilidade da senha', async () => {
    const page = await render();
    const input = page.element.querySelector<HTMLInputElement>('#login-password')!;
    const toggle = page.element.querySelector<HTMLButtonElement>('app-password-toggle button')!;

    expect(input.type).toBe('password');
    expect(toggle.getAttribute('aria-label')).toBe('Mostrar senha');
    expect(toggle.getAttribute('aria-controls')).toBe('login-password');

    toggle.click();
    await page.fixture.whenStable();
    expect(input.type).toBe('text');

    toggle.click();
    await page.fixture.whenStable();
    expect(input.type).toBe('password');
  });

  it('faz login e navega para o treino', async () => {
    const page = await render();
    const navigate = vi.spyOn(TestBed.inject(Router), 'navigate').mockResolvedValue(true);

    page.type('#login-email', 'ana@example.com');
    page.type('#login-password', 'segredo');
    await page.submit();

    expect(auth.login).toHaveBeenCalledWith({ email: 'ana@example.com', password: 'segredo' });
    expect(navigate).toHaveBeenCalledWith(['/treino']);
    expect(toast.success).toHaveBeenCalled();
  });

  it('exibe a mensagem de erro devolvida pela API e reabilita o botão', async () => {
    const page = await render();
    auth.login.mockReturnValue(
      throwError(
        () =>
          new HttpErrorResponse({
            status: 401,
            error: { error: { code: 'unauthorized', message: 'Credenciais inválidas.' } },
          }),
      ),
    );

    page.type('#login-email', 'ana@example.com');
    page.type('#login-password', 'errada');
    await page.submit();

    expect(toast.error).toHaveBeenCalledWith('Credenciais inválidas.');
    const button = page.element.querySelector<HTMLButtonElement>('button[type=submit]')!;
    expect(button.disabled).toBe(false);
    expect(button.textContent?.trim()).toBe('Entrar');
  });
});
