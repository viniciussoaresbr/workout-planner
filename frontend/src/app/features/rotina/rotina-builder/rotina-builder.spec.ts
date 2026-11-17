import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';

import { SUPINO } from '../../../../testing/rotina-fixtures';
import { ToastService } from '../../../core/notifications/toast.service';
import { createItem } from '../data/rotina.mapper';
import { ExerciciosApi, RotinasApi } from '../data/rotinas.api';
import { BIBLIOTECA_LIST, RotinaDrop } from '../drag-drop';
import { RotinaEditorStore } from '../state/rotina-editor.store';
import { RotinaBuilder } from './rotina-builder';

/** Expõe os métodos protegidos usados pelo template. */
type BuilderHarness = {
  onDrop(event: RotinaDrop): void;
  addExercicio(exercicio: typeof SUPINO): void;
};

function dropEvent(from: string, to: string, data: unknown, previousIndex = 0, currentIndex = 0) {
  return {
    previousContainer: { data: from },
    container: { data: to },
    item: { data },
    previousIndex,
    currentIndex,
  } as unknown as RotinaDrop;
}

describe('RotinaBuilder', () => {
  let store: RotinaEditorStore;
  let builder: BuilderHarness;
  let toast: { success: ReturnType<typeof vi.fn>; warning: ReturnType<typeof vi.fn> };

  beforeEach(async () => {
    toast = { success: vi.fn(), warning: vi.fn() };
    TestBed.configureTestingModule({
      imports: [RotinaBuilder],
      providers: [
        provideRouter([]),
        { provide: ToastService, useValue: toast },
        { provide: RotinasApi, useValue: { listar: () => of([]) } },
        {
          provide: ExerciciosApi,
          useValue: { listar: () => of([SUPINO]), listarMusculos: () => of(['Peito']) },
        },
      ],
    });
    const fixture = TestBed.createComponent(RotinaBuilder);
    await fixture.whenStable();
    store = fixture.debugElement.injector.get(RotinaEditorStore);
    builder = fixture.componentInstance as unknown as BuilderHarness;
  });

  it('copia o exercício da biblioteca para o dia na posição solta', () => {
    const [segunda] = store.dias();

    builder.onDrop(dropEvent(BIBLIOTECA_LIST, segunda.key, SUPINO, 3, 0));

    expect(store.dias()[0].itens.map(item => item.exercicio.id)).toEqual([SUPINO.id]);
  });

  it('reordena dentro do mesmo dia e move entre dias', () => {
    const [segunda, terca] = store.dias();
    store.insertFromLibrary(SUPINO, segunda.key, 0);
    store.insertFromLibrary({ ...SUPINO, id: 'outro' }, segunda.key, 1);

    builder.onDrop(dropEvent(segunda.key, segunda.key, null, 0, 1));
    expect(store.dias()[0].itens.map(item => item.exercicio.id)).toEqual(['outro', SUPINO.id]);

    builder.onDrop(dropEvent(segunda.key, terca.key, createItem(SUPINO), 1, 0));
    expect(store.dias()[1].itens.map(item => item.exercicio.id)).toEqual([SUPINO.id]);
  });

  it('ignora drops na biblioteca', () => {
    const [segunda] = store.dias();
    store.insertFromLibrary(SUPINO, segunda.key, 0);

    builder.onDrop(dropEvent(segunda.key, BIBLIOTECA_LIST, null));

    expect(store.dias()[0].itens).toHaveLength(1);
  });

  it('avisa em qual dia o exercício foi adicionado pelo botão', () => {
    builder.addExercicio(SUPINO);

    expect(toast.success).toHaveBeenCalledWith(`${SUPINO.nome} adicionado a Segunda.`);
  });

  it('renderiza a biblioteca com os exercícios do primeiro grupo', async () => {
    await vi.waitFor(() => {
      TestBed.tick();
      const nomes = [...document.querySelectorAll('app-exercicio-library article span')].map(h =>
        h.textContent?.trim(),
      );
      expect(nomes).toEqual([SUPINO.nome]);
    });
  });
});
