import { TestBed } from '@angular/core/testing';

import { ToastService } from './toast.service';

describe('ToastService', () => {
  let service: ToastService;

  beforeEach(() => {
    vi.useFakeTimers();
    service = TestBed.inject(ToastService);
  });

  afterEach(() => vi.useRealTimers());

  it('exibe e remove automaticamente após o tempo do tipo', () => {
    service.success('Salvo.');
    service.error('Falhou.');
    expect(service.toasts().map(toast => toast.message)).toEqual(['Salvo.', 'Falhou.']);

    vi.advanceTimersByTime(3_000);
    expect(service.toasts().map(toast => toast.message)).toEqual(['Falhou.']);

    vi.advanceTimersByTime(2_000);
    expect(service.toasts()).toEqual([]);
  });

  it('não duplica a mesma mensagem visível', () => {
    service.error('Sem conexão.');
    service.error('Sem conexão.');

    expect(service.toasts()).toHaveLength(1);
  });

  it('mantém no máximo 4 notificações', () => {
    ['a', 'b', 'c', 'd', 'e'].forEach(message => service.info(message));

    expect(service.toasts().map(toast => toast.message)).toEqual(['b', 'c', 'd', 'e']);
  });

  it('permite fechar manualmente', () => {
    service.warning('Atenção.');
    service.dismiss(service.toasts()[0].id);

    expect(service.toasts()).toEqual([]);
  });
});
