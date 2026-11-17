import { TestBed } from '@angular/core/testing';

import { SUPINO } from '../../../../testing/rotina-fixtures';
import { createItem } from '../data/rotina.mapper';
import { DiaTreino } from '../data/rotina.models';
import { DiaTreinoCard, ItemChange, parseCountInput } from './dia-treino';

describe('parseCountInput', () => {
  it.each([
    ['12', '12', 12],
    ['1a2', '12', 12],
    ['-3', '3', 3],
    ['1234', '123', 123],
    ['', '', null],
    ['abc', '', null],
  ])('"%s" → texto "%s", valor %s', (raw, text, value) => {
    expect(parseCountInput(raw)).toEqual({ text, value });
  });
});

describe('DiaTreinoCard', () => {
  async function render(dia: DiaTreino) {
    const fixture = TestBed.createComponent(DiaTreinoCard);
    fixture.componentRef.setInput('dia', dia);
    await fixture.whenStable();
    return { fixture, element: fixture.nativeElement as HTMLElement };
  }

  it('mostra o estado vazio', async () => {
    const { element } = await render({ key: 'd1', nome: 'Segunda', itens: [] });

    expect(element.textContent).toContain('Solte exercícios aqui');
    expect(element.textContent).toContain('0/10');
  });

  it('emite alterações já sanitizadas e corrige o campo', async () => {
    const item = createItem(SUPINO, 4, 12);
    const { fixture, element } = await render({ key: 'd1', nome: 'Segunda', itens: [item] });
    const changes: ItemChange[] = [];
    fixture.componentInstance.changed.subscribe(change => changes.push(change));

    const [series] = element.querySelectorAll<HTMLInputElement>('input');
    series.value = '5x';
    series.dispatchEvent(new Event('input'));

    expect(series.value).toBe('5');
    expect(changes).toEqual([{ uid: item.uid, campo: 'series', valor: 5 }]);
  });

  it('emite a remoção com o uid do item', async () => {
    const item = createItem(SUPINO);
    const { fixture, element } = await render({ key: 'd1', nome: 'Segunda', itens: [item] });
    const removed = vi.fn();
    fixture.componentInstance.removed.subscribe(removed);

    element.querySelector<HTMLButtonElement>('button[aria-label^="Remover"]')!.click();

    expect(removed).toHaveBeenCalledWith(item.uid);
  });
});
