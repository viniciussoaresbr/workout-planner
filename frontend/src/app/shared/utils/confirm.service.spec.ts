import { TestBed } from '@angular/core/testing';

import { ConfirmDialog } from './confirm-dialog';
import { ConfirmService } from './confirm.service';

describe('ConfirmService', () => {
  let service: ConfirmService;

  beforeEach(() => {
    service = TestBed.inject(ConfirmService);
  });

  it('expõe a pergunta com valores padrão e resolve com a resposta', async () => {
    const answer = service.ask({ title: 'Excluir?', message: 'Não dá para desfazer.' });

    expect(service.request()).toMatchObject({
      title: 'Excluir?',
      confirmLabel: 'Confirmar',
      cancelLabel: 'Cancelar',
      tone: 'default',
    });

    service.request()!.resolve(true);

    await expect(answer).resolves.toBe(true);
    expect(service.request()).toBeNull();
  });

  it('uma nova pergunta cancela a anterior', async () => {
    const first = service.ask({ title: 'A', message: 'a' });
    const second = service.ask({ title: 'B', message: 'b' });

    await expect(first).resolves.toBe(false);
    expect(service.request()?.title).toBe('B');

    service.request()!.resolve(true);
    await expect(second).resolves.toBe(true);
  });
});

describe('ConfirmDialog', () => {
  it('mostra a pergunta e devolve a escolha do usuário', async () => {
    const fixture = TestBed.createComponent(ConfirmDialog);
    const service = TestBed.inject(ConfirmService);
    await fixture.whenStable();

    const answer = service.ask({
      title: 'Excluir rotina?',
      message: '"Treino A" será removida.',
      confirmLabel: 'Excluir rotina',
      tone: 'danger',
    });
    await fixture.whenStable();

    const element = fixture.nativeElement as HTMLElement;
    expect(element.querySelector('#confirm-title')?.textContent?.trim()).toBe('Excluir rotina?');
    const buttons = [...element.querySelectorAll('button')];
    const confirmar = buttons.find(button => button.textContent?.trim() === 'Excluir rotina')!;
    expect(confirmar.classList).toContain('btn-danger-solid');

    confirmar.click();

    await expect(answer).resolves.toBe(true);
  });
});
