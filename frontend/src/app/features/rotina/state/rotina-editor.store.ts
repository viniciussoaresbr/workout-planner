import { DestroyRef, Injectable, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Observable, finalize } from 'rxjs';

import { ToastService } from '../../../core/notifications/toast.service';
import { ConfirmService } from '../../../shared/utils/confirm.service';
import { FileDownloader } from '../../../shared/utils/download-file';
import { createDefaultDays, createItem, toResumo } from '../data/rotina.mapper';
import {
  DiaTreino,
  Exercicio,
  ItemTreino,
  ROTINA_LIMITS,
  Rotina,
  RotinaDraft,
  RotinaResumo,
} from '../data/rotina.models';
import { RotinasApi } from '../data/rotinas.api';

export type ItemPatch = Partial<Pick<ItemTreino, 'series' | 'repeticoes'>>;

/** Representação estável do conteúdo do rascunho (ignora `uid` e chaves de tela). */
export function draftSignature(draft: RotinaDraft): string {
  return JSON.stringify([
    draft.nome.trim(),
    draft.dias.map(dia => [
      dia.nome,
      dia.itens.map(item => [item.exercicio.id, item.series, item.repeticoes]),
    ]),
  ]);
}

export function isValidCount(value: number | null): value is number {
  return (
    value !== null &&
    Number.isInteger(value) &&
    value >= ROTINA_LIMITS.valorMin &&
    value <= ROTINA_LIMITS.valorMax
  );
}

export function validateNome(nome: string): string | null {
  const length = nome.trim().length;
  if (length === 0) {
    return 'Dê um nome à rotina.';
  }
  if (length < ROTINA_LIMITS.nomeMin) {
    return `O nome da rotina precisa ter pelo menos ${ROTINA_LIMITS.nomeMin} caracteres.`;
  }
  if (length > ROTINA_LIMITS.nomeMax) {
    return `O nome da rotina pode ter no máximo ${ROTINA_LIMITS.nomeMax} caracteres.`;
  }
  return null;
}

const EMPTY_SIGNATURE = draftSignature({ nome: '', dias: createDefaultDays() });

/**
 * Estado e regras do editor de rotinas. Fornecido no componente da página,
 * então cada visita à tela começa com um estado limpo.
 */
@Injectable()
export class RotinaEditorStore {
  private readonly api = inject(RotinasApi);
  private readonly toast = inject(ToastService);
  private readonly confirm = inject(ConfirmService);
  private readonly downloader = inject(FileDownloader);
  private readonly destroyRef = inject(DestroyRef);

  // ---- Estado ----
  readonly nome = signal('');
  readonly dias = signal<DiaTreino[]>(createDefaultDays());
  readonly selectedId = signal<string | null>(null);
  readonly rotinas = signal<Rotina[]>([]);
  readonly loadingList = signal(false);
  readonly loadingId = signal<string | null>(null);
  readonly saving = signal(false);
  readonly deleting = signal(false);
  readonly exporting = signal(false);
  private readonly savedSignature = signal(EMPTY_SIGNATURE);

  // ---- Derivados ----
  readonly draft = computed<RotinaDraft>(() => ({ nome: this.nome(), dias: this.dias() }));
  readonly hasUnsavedChanges = computed(
    () => draftSignature(this.draft()) !== this.savedSignature(),
  );
  readonly nomeError = computed(() => validateNome(this.nome()));
  readonly validationError = computed(() => {
    const itensInvalidos = this.dias().some(dia =>
      dia.itens.some(item => !isValidCount(item.series) || !isValidCount(item.repeticoes)),
    );
    return (
      this.nomeError() ??
      (itensInvalidos
        ? `Preencha séries e repetições com valores entre ${ROTINA_LIMITS.valorMin} e ${ROTINA_LIMITS.valorMax}.`
        : null)
    );
  });
  readonly busy = computed(() => this.loadingId() !== null || this.saving() || this.deleting());
  /** Cards das rotinas salvas; a selecionada reflete a edição em andamento. */
  readonly resumos = computed<RotinaResumo[]>(() =>
    this.rotinas().map(rotina =>
      toResumo(
        rotina.id === this.selectedId()
          ? { ...rotina, nome: this.nome().trim() || rotina.nome, dias: this.dias() }
          : rotina,
      ),
    ),
  );

  /** Totais da semana em edição. */
  readonly semana = computed(() => {
    const dias = this.dias();
    return {
      exercicios: dias.reduce((total, dia) => total + dia.itens.length, 0),
      diasComTreino: dias.filter(dia => dia.itens.length > 0).length,
    };
  });
  readonly status = computed<'nova' | 'salva' | 'alterada'>(() => {
    if (this.hasUnsavedChanges()) {
      return 'alterada';
    }
    return this.selectedId() ? 'salva' : 'nova';
  });

  // ---- Edição ----

  canAccept(diaKey: string): boolean {
    const dia = this.dias().find(item => item.key === diaKey);
    return !!dia && dia.itens.length < ROTINA_LIMITS.exerciciosPorDia;
  }

  /** Adiciona ao primeiro dia com espaço. Retorna o dia escolhido, ou `null` se todos estiverem cheios. */
  addToFirstAvailableDay(exercicio: Exercicio): DiaTreino | null {
    const dia = this.dias().find(item => item.itens.length < ROTINA_LIMITS.exerciciosPorDia);
    if (!dia) {
      return null;
    }
    this.insertFromLibrary(exercicio, dia.key, dia.itens.length);
    return dia;
  }

  insertFromLibrary(exercicio: Exercicio, diaKey: string, index: number): boolean {
    if (!this.canAccept(diaKey)) {
      return false;
    }
    this.updateDia(diaKey, itens => insertAt(itens, index, createItem(exercicio)));
    return true;
  }

  moveItem(diaKey: string, fromIndex: number, toIndex: number): void {
    if (fromIndex === toIndex) {
      return;
    }
    this.updateDia(diaKey, itens => {
      const next = [...itens];
      const [moved] = next.splice(fromIndex, 1);
      return moved ? insertAt(next, toIndex, moved) : itens;
    });
  }

  transferItem(fromKey: string, toKey: string, fromIndex: number, toIndex: number): boolean {
    const item = this.dias().find(dia => dia.key === fromKey)?.itens[fromIndex];
    if (!item || !this.canAccept(toKey)) {
      return false;
    }
    this.dias.update(dias =>
      dias.map(dia => {
        if (dia.key === fromKey) {
          return { ...dia, itens: dia.itens.filter((_, index) => index !== fromIndex) };
        }
        if (dia.key === toKey) {
          return { ...dia, itens: insertAt(dia.itens, toIndex, item) };
        }
        return dia;
      }),
    );
    return true;
  }

  removeItem(diaKey: string, uid: string): void {
    this.updateDia(diaKey, itens => itens.filter(item => item.uid !== uid));
  }

  updateItem(diaKey: string, uid: string, patch: ItemPatch): void {
    this.updateDia(diaKey, itens =>
      itens.map(item => (item.uid === uid ? { ...item, ...patch } : item)),
    );
  }

  // ---- Persistência ----

  loadRotinas(): void {
    this.loadingList.set(true);
    this.run(
      this.api.listar(),
      () => this.loadingList.set(false),
      rotinas => this.rotinas.set(rotinas),
    );
  }

  async select(id: string): Promise<void> {
    if (id === this.selectedId() || this.busy() || !(await this.confirmDiscard())) {
      return;
    }
    this.loadingId.set(id);
    this.run(
      this.api.buscar(id),
      () => this.loadingId.set(null),
      rotina => {
        this.applyRotina(rotina);
        this.toast.success('Rotina carregada.');
      },
    );
  }

  save(): void {
    const error = this.validationError();
    if (error) {
      this.toast.warning(error);
      return;
    }
    if (this.saving()) {
      return;
    }

    const id = this.selectedId();
    const request = id ? this.api.atualizar(id, this.draft()) : this.api.criar(this.draft());
    this.saving.set(true);
    this.run(
      request,
      () => this.saving.set(false),
      rotina => {
        this.applyRotina(rotina);
        this.rotinas.update(rotinas =>
          id ? rotinas.map(item => (item.id === rotina.id ? rotina : item)) : [rotina, ...rotinas],
        );
        this.toast.success(id ? 'Rotina atualizada com sucesso.' : 'Rotina criada com sucesso.');
      },
    );
  }

  async remove(): Promise<void> {
    const id = this.selectedId();
    if (!id) {
      this.toast.warning('Selecione uma rotina salva antes de excluir.');
      return;
    }
    if (this.deleting()) {
      return;
    }
    const nome = this.rotinas().find(rotina => rotina.id === id)?.nome ?? this.nome();
    const confirmed = await this.confirm.ask({
      title: 'Excluir rotina?',
      message: `"${nome}" será removida permanentemente. Esta ação não pode ser desfeita.`,
      confirmLabel: 'Excluir rotina',
      tone: 'danger',
    });
    // A seleção pode ter mudado enquanto o diálogo estava aberto.
    if (!confirmed || this.selectedId() !== id) {
      return;
    }

    this.deleting.set(true);
    this.run(
      this.api.excluir(id),
      () => this.deleting.set(false),
      () => {
        this.rotinas.update(rotinas => rotinas.filter(rotina => rotina.id !== id));
        this.clear();
        this.toast.success('Rotina excluída com sucesso.');
      },
    );
  }

  exportSpreadsheet(): void {
    const id = this.selectedId();
    if (!id) {
      this.toast.warning('Salve a rotina antes de exportar a planilha.');
      return;
    }
    if (this.hasUnsavedChanges()) {
      this.toast.warning('Salve as alterações antes de exportar a planilha.');
      return;
    }
    if (this.exporting()) {
      return;
    }

    this.exporting.set(true);
    this.run(
      this.api.exportarPlanilha(id),
      () => this.exporting.set(false),
      ({ blob, filename }) => {
        this.downloader.download(blob, filename ?? 'rotina.xlsx');
        this.toast.success('Planilha exportada com sucesso.');
      },
    );
  }

  /** Começa uma rotina nova, pedindo confirmação se houver alterações não salvas. */
  async reset(): Promise<void> {
    if (await this.confirmDiscard()) {
      this.clear();
    }
  }

  /** Resolve `true` se não há alterações pendentes ou se o usuário aceitou descartá-las. */
  confirmDiscard(): Promise<boolean> {
    if (!this.hasUnsavedChanges()) {
      return Promise.resolve(true);
    }
    return this.confirm.ask({
      title: 'Descartar alterações?',
      message: 'Esta rotina tem alterações que ainda não foram salvas.',
      confirmLabel: 'Descartar',
      tone: 'danger',
    });
  }

  // ---- Internos ----

  private clear(): void {
    this.selectedId.set(null);
    this.nome.set('');
    this.dias.set(createDefaultDays());
    this.savedSignature.set(EMPTY_SIGNATURE);
  }

  private applyRotina(rotina: Rotina): void {
    this.selectedId.set(rotina.id);
    this.nome.set(rotina.nome);
    this.dias.set(rotina.dias);
    this.savedSignature.set(draftSignature(rotina));
  }

  private updateDia(diaKey: string, change: (itens: ItemTreino[]) => ItemTreino[]): void {
    this.dias.update(dias =>
      dias.map(dia => (dia.key === diaKey ? { ...dia, itens: change(dia.itens) } : dia)),
    );
  }

  /**
   * Executa uma requisição atrelada ao ciclo de vida da tela. Erros já são exibidos pelo
   * interceptor global, então aqui só garantimos que o estado de carregamento seja limpo.
   */
  private run<T>(request: Observable<T>, done: () => void, next: (value: T) => void): void {
    request
      .pipe(finalize(done), takeUntilDestroyed(this.destroyRef))
      .subscribe({ next, error: () => undefined });
  }
}

function insertAt<T>(items: readonly T[], index: number, item: T): T[] {
  const position = Math.max(0, Math.min(index, items.length));
  return [...items.slice(0, position), item, ...items.slice(position)];
}
