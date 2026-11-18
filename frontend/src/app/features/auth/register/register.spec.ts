import { TestBed } from '@angular/core/testing';
import { Router, provideRouter } from '@angular/router';
import { of } from 'rxjs';

import { AuthService } from '../../../core/auth/auth.service';
import { ToastService } from '../../../core/notifications/toast.service';
import { Register } from './register';

describe('Register', () => {
  let auth: { register: ReturnType<typeof vi.fn> };

  async function render() {
    auth = { register: vi.fn(() => of(undefined)) };
    TestBed.configureTestingModule({
      imports: [Register],
      providers: [
        provideRouter([]),
        { provide: AuthService, useValue: auth },
        { provide: ToastService, useValue: { success: vi.fn(), error: vi.fn() } },
      ],
    });
    const fixture = TestBed.createComponent(Register);
    await fixture.whenStable();
    const element = fixture.nativeElement as HTMLElement;
    const input = (selector: string) => element.querySelector<HTMLInputElement>(selector)!;
    return {
      fixture,
      element,
      input,
      async type(selector: string, value: string) {
        input(selector).value = value;
        input(selector).dispatchEvent(new Event('input'));
        input(selector).dispatchEvent(new Event('blur'));
        await fixture.whenStable();
      },
      async submit() {
        element.querySelector<HTMLButtonElement>('button[type=submit]')!.click();
        await fixture.whenStable();
      },
      errorFor(id: string) {
        return element.querySelector(`#${id} [role=alert]`)?.textContent?.trim() ?? null;
      },
    };
  }

  async function fill(page: Awaited<ReturnType<typeof render>>, overrides = {}) {
    const values = {
      name: 'Ana',
      email: 'ana@example.com',
      password: 'senha-segura1',
      confirm: 'senha-segura1',
      ...overrides,
    };
    await page.type('#register-name', values.name);
    await page.type('#register-email', values.email);
    await page.type('#register-password', values.password);
    await page.type('#register-confirm-password', values.confirm);
  }

  it('mostra erro em todos os campos obrigatórios e não chama a API', async () => {
    const page = await render();

    await page.submit();

    expect(auth.register).not.toHaveBeenCalled();
    for (const id of ['name', 'email', 'password', 'confirm-password']) {
      expect(page.errorFor(`register-${id}-error`)).toBe('Campo obrigatório.');
    }
  });

  it('valida nome só com espaços, e-mail sem domínio e senha fraca', async () => {
    const page = await render();

    await fill(page, { name: '   ', email: 'ana@exemplo', password: 'somenteletras' });

    expect(page.errorFor('register-name-error')).toBe('Campo obrigatório.');
    expect(page.errorFor('register-email-error')).toBe('Informe um e-mail válido.');
    expect(page.errorFor('register-password-error')).toBe('Use pelo menos uma letra e um número.');
  });

  it('exige que a confirmação seja igual à senha e revalida quando a senha muda', async () => {
    const page = await render();

    await fill(page, { confirm: 'outra-senha1' });
    expect(page.errorFor('register-confirm-password-error')).toBe('As senhas não coincidem.');

    await page.type('#register-password', 'outra-senha1');
    expect(page.errorFor('register-confirm-password-error')).toBeNull();
  });

  it('mostra a dica da senha enquanto não há erro', async () => {
    const page = await render();

    expect(page.element.querySelector('#register-password-error')?.textContent?.trim()).toBe(
      'Mínimo de 8 caracteres, com letras e números.',
    );
  });

  it('alterna a visibilidade da senha e da confirmação de forma independente', async () => {
    const page = await render();
    const [senha, confirmacao] = page.element.querySelectorAll<HTMLButtonElement>(
      'app-password-toggle button',
    );

    // Nomes acessíveis distintos para o leitor de tela diferenciar os dois botões.
    expect(senha.getAttribute('aria-label')).toBe('Mostrar senha');
    expect(confirmacao.getAttribute('aria-label')).toBe('Mostrar confirmação de senha');

    senha.click();
    await page.fixture.whenStable();

    expect(page.input('#register-password').type).toBe('text');
    expect(page.input('#register-confirm-password').type).toBe('password');
    expect(senha.getAttribute('aria-label')).toBe('Ocultar senha');
    expect(senha.getAttribute('aria-pressed')).toBe('true');

    confirmacao.click();
    senha.click();
    await page.fixture.whenStable();

    expect(page.input('#register-password').type).toBe('password');
    expect(page.input('#register-confirm-password').type).toBe('text');
  });

  it('envia nome e e-mail sem espaços nas pontas, sem a confirmação, e navega', async () => {
    const page = await render();
    const navigate = vi.spyOn(TestBed.inject(Router), 'navigate').mockResolvedValue(true);

    await fill(page, { name: '  Ana Silva ', email: ' ana@example.com ' });
    await page.submit();

    expect(auth.register).toHaveBeenCalledWith({
      name: 'Ana Silva',
      email: 'ana@example.com',
      password: 'senha-segura1',
    });
    expect(navigate).toHaveBeenCalledWith(['/treino']);
  });
});
