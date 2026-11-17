import { TestBed } from '@angular/core/testing';
import { Subject, of, throwError } from 'rxjs';

import { AGACHAMENTO, SUPINO, rotinaDto } from '../../../../testing/rotina-fixtures';
import { ToastService } from '../../../core/notifications/toast.service';
import { ConfirmService } from '../../../shared/utils/confirm.service';
import { FileDownloader } from '../../../shared/utils/download-file';
import { fromRotinaDto } from '../data/rotina.mapper';
import { ROTINA_LIMITS, Rotina } from '../data/rotina.models';
import { RotinasApi } from '../data/rotinas.api';
import { RotinaEditorStore } from './rotina-editor.store';

type ApiMock = { [K in keyof RotinasApi]: ReturnType<typeof vi.fn> };

describe('RotinaEditorStore', () => {
  let store: RotinaEditorStore;
  let api: ApiMock;
  let toast: { success: ReturnType<typeof vi.fn>; warning: ReturnType<typeof vi.fn> };
  let confirm: { ask: ReturnType<typeof vi.fn> };
  let downloader: { download: ReturnType<typeof vi.fn> };
  const salva: Rotina = fromRotinaDto(rotinaDto());

  beforeEach(() => {
    api = {
      listar: vi.fn(() => of([salva])),
      buscar: vi.fn(() => of(fromRotinaDto(rotinaDto()))),
      criar: vi.fn(() => of(fromRotinaDto(rotinaDto({ id: 'nova', nome: 'Nova' })))),
      atualizar: vi.fn(() => of(fromRotinaDto(rotinaDto({ nome: 'Treino A2' })))),
      excluir: vi.fn(() => of(undefined)),
      exportarPlanilha: vi.fn(() => of({ blob: new Blob(['x']), filename: 'rotina-a.xlsx' })),
    };
    toast = { success: vi.fn(), warning: vi.fn() };
    confirm = { ask: vi.fn(() => true) };
    downloader = { download: vi.fn() };

    TestBed.configureTestingModule({
      providers: [
        RotinaEditorStore,
        { provide: RotinasApi, useValue: api },
        { provide: ToastService, useValue: toast },
        { provide: ConfirmService, useValue: confirm },
        { provide: FileDownloader, useValue: downloader },
      ],
    });
    store = TestBed.inject(RotinaEditorStore);
  });

  const segunda = () => store.dias()[0];

  describe('edição', () => {
    it('começa com os 7 dias da semana vazios e sem alterações', () => {
      expect(store.dias().map(dia => dia.nome)).toEqual([
        'Segunda',
        'Terça',
        'Quarta',
        'Quinta',
        'Sexta',
        'Sábado',
        'Domingo',
      ]);
      expect(store.hasUnsavedChanges()).toBe(false);
    });

    it('cria ocorrências independentes ao adicionar o mesmo exercício duas vezes', () => {
      store.insertFromLibrary(SUPINO, segunda().key, 0);
      store.insertFromLibrary(SUPINO, segunda().key, 1);
      const [a, b] = segunda().itens;

      store.updateItem(segunda().key, a.uid, { series: 6 });
      store.removeItem(segunda().key, b.uid);

      expect(a.uid).not.toBe(b.uid);
      expect(segunda().itens).toHaveLength(1);
      expect(segunda().itens[0]).toMatchObject({ uid: a.uid, series: 6 });
    });

    it('adiciona ao primeiro dia com espaço e respeita o limite por dia', () => {
      for (let i = 0; i < ROTINA_LIMITS.exerciciosPorDia; i++) {
        expect(store.addToFirstAvailableDay(SUPINO)?.nome).toBe('Segunda');
      }

      expect(store.addToFirstAvailableDay(SUPINO)?.nome).toBe('Terça');
      expect(store.canAccept(segunda().key)).toBe(false);
      expect(store.insertFromLibrary(AGACHAMENTO, segunda().key, 0)).toBe(false);
    });

    it('retorna null quando todos os dias estão cheios', () => {
      const total = ROTINA_LIMITS.exerciciosPorDia * 7;
      for (let i = 0; i < total; i++) {
        store.addToFirstAvailableDay(SUPINO);
      }

      expect(store.addToFirstAvailableDay(SUPINO)).toBeNull();
    });

    it('reordena dentro do dia e transfere entre dias', () => {
      const [seg, ter] = store.dias();
      store.insertFromLibrary(SUPINO, seg.key, 0);
      store.insertFromLibrary(AGACHAMENTO, seg.key, 1);

      store.moveItem(seg.key, 0, 1);
      expect(segunda().itens.map(item => item.exercicio.id)).toEqual([AGACHAMENTO.id, SUPINO.id]);

      expect(store.transferItem(seg.key, ter.key, 1, 0)).toBe(true);
      expect(segunda().itens.map(item => item.exercicio.id)).toEqual([AGACHAMENTO.id]);
      expect(store.dias()[1].itens.map(item => item.exercicio.id)).toEqual([SUPINO.id]);
    });

    it('não transfere para um dia cheio', () => {
      const [seg, ter] = store.dias();
      for (let i = 0; i < ROTINA_LIMITS.exerciciosPorDia; i++) {
        store.insertFromLibrary(SUPINO, ter.key, i);
      }
      store.insertFromLibrary(AGACHAMENTO, seg.key, 0);

      expect(store.transferItem(seg.key, ter.key, 0, 0)).toBe(false);
      expect(segunda().itens).toHaveLength(1);
    });

    it('valida nome e valores de séries/repetições', () => {
      expect(store.validationError()).toBe('Dê um nome à rotina.');

      store.nome.set('AB');
      expect(store.validationError()).toContain('pelo menos 3');

      store.nome.set('Treino A');
      store.insertFromLibrary(SUPINO, segunda().key, 0);
      expect(store.validationError()).toBeNull();

      store.updateItem(segunda().key, segunda().itens[0].uid, { repeticoes: null });
      expect(store.validationError()).toContain('séries e repetições');
    });
  });

  describe('persistência', () => {
    it('carrega as rotinas e exibe os resumos', () => {
      store.loadRotinas();

      expect(store.resumos()).toEqual([
        { id: 'rotina-1', nome: 'Treino A', totalExercicios: 2, grupos: ['Peito', 'Pernas'] },
      ]);
      expect(store.loadingList()).toBe(false);
    });

    it('não salva rascunho inválido', () => {
      store.save();

      expect(api.criar).not.toHaveBeenCalled();
      expect(toast.warning).toHaveBeenCalledWith('Dê um nome à rotina.');
    });

    it('cria uma rotina nova, seleciona e marca como salva', () => {
      store.nome.set('Nova');
      store.insertFromLibrary(SUPINO, segunda().key, 0);

      store.save();

      expect(api.criar).toHaveBeenCalledWith(expect.objectContaining({ nome: 'Nova' }));
      expect(store.selectedId()).toBe('nova');
      expect(store.rotinas().map(rotina => rotina.id)).toEqual(['nova']);
      expect(store.hasUnsavedChanges()).toBe(false);
      expect(store.saving()).toBe(false);
    });

    it('atualiza a rotina selecionada no lugar', () => {
      store.loadRotinas();
      store.select('rotina-1');
      store.nome.set('Treino A2');

      store.save();

      expect(api.atualizar).toHaveBeenCalledWith('rotina-1', expect.anything());
      expect(store.rotinas().map(rotina => rotina.nome)).toEqual(['Treino A2']);
    });

    it('libera o estado de carregamento quando a API falha', () => {
      api.criar.mockReturnValue(throwError(() => new Error('falhou')));
      store.nome.set('Nova');

      store.save();

      expect(store.saving()).toBe(false);
      expect(store.selectedId()).toBeNull();
    });

    it('ignora cliques repetidos enquanto salva', () => {
      const pending = new Subject<Rotina>();
      api.criar.mockReturnValue(pending);
      store.nome.set('Nova');

      store.save();
      store.save();

      expect(api.criar).toHaveBeenCalledTimes(1);
    });

    it('pede confirmação antes de trocar de rotina com alterações não salvas', () => {
      store.nome.set('Rascunho');
      confirm.ask.mockReturnValue(false);

      store.select('rotina-1');

      expect(api.buscar).not.toHaveBeenCalled();
      expect(store.nome()).toBe('Rascunho');
    });

    it('carrega a rotina escolhida sem marcar alterações', () => {
      store.select('rotina-1');

      expect(store.selectedId()).toBe('rotina-1');
      expect(store.nome()).toBe('Treino A');
      expect(store.hasUnsavedChanges()).toBe(false);
      expect(confirm.ask).not.toHaveBeenCalled();
    });

    it('exclui somente após confirmação', () => {
      store.loadRotinas();
      store.select('rotina-1');

      confirm.ask.mockReturnValueOnce(false);
      store.remove();
      expect(api.excluir).not.toHaveBeenCalled();

      store.remove();
      expect(confirm.ask).toHaveBeenLastCalledWith(expect.stringContaining('"Treino A"'));
      expect(api.excluir).toHaveBeenCalledWith('rotina-1');
      expect(store.rotinas()).toEqual([]);
      expect(store.selectedId()).toBeNull();
      expect(store.nome()).toBe('');
    });

    it('exporta apenas rotinas salvas e sem alterações pendentes', () => {
      store.exportSpreadsheet();
      expect(toast.warning).toHaveBeenLastCalledWith(
        'Salve a rotina antes de exportar a planilha.',
      );

      store.select('rotina-1');
      store.nome.set('Mudou');
      store.exportSpreadsheet();
      expect(toast.warning).toHaveBeenLastCalledWith(
        'Salve as alterações antes de exportar a planilha.',
      );
      expect(api.exportarPlanilha).not.toHaveBeenCalled();

      store.nome.set('Treino A');
      store.exportSpreadsheet();
      expect(api.exportarPlanilha).toHaveBeenCalledWith('rotina-1');
      expect(downloader.download).toHaveBeenCalledWith(expect.any(Blob), 'rotina-a.xlsx');
    });

    it('reset volta ao estado inicial após confirmar o descarte', () => {
      store.nome.set('Rascunho');
      store.insertFromLibrary(SUPINO, segunda().key, 0);

      store.reset();

      expect(confirm.ask).toHaveBeenCalled();
      expect(store.nome()).toBe('');
      expect(store.dias().every(dia => dia.itens.length === 0)).toBe(true);
      expect(store.hasUnsavedChanges()).toBe(false);
    });
  });
});
