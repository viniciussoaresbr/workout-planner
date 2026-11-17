import { CdkDrag, CdkDropList } from '@angular/cdk/drag-drop';
import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { heroTrash } from '@ng-icons/heroicons/outline';

import { DiaTreino, ItemTreino, ROTINA_LIMITS } from '../data/rotina.models';
import { RotinaDrop } from '../drag-drop';

export interface ItemChange {
  uid: string;
  campo: 'series' | 'repeticoes';
  valor: number | null;
}

const MAX_DIGITS = String(ROTINA_LIMITS.valorMax).length;

/** Mantém só dígitos e converte para número (`null` quando vazio). */
export function parseCountInput(raw: string): { text: string; value: number | null } {
  const text = raw.replace(/\D/g, '').slice(0, MAX_DIGITS);
  return { text, value: text ? Number(text) : null };
}

@Component({
  selector: 'app-dia-treino',
  imports: [CdkDropList, CdkDrag, NgIcon],
  providers: [provideIcons({ heroTrash })],
  templateUrl: './dia-treino.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DiaTreinoCard {
  readonly dia = input.required<DiaTreino>();
  readonly acceptsMore = input(true);

  readonly dropped = output<RotinaDrop>();
  readonly removed = output<string>();
  readonly changed = output<ItemChange>();

  protected readonly maxItens = ROTINA_LIMITS.exerciciosPorDia;
  protected readonly maxDigits = MAX_DIGITS;

  /** Bloqueia a entrada de exercícios vindos de outra lista quando o dia está cheio. */
  protected readonly canEnter = (): boolean => this.acceptsMore();

  protected onCountInput(item: ItemTreino, campo: ItemChange['campo'], event: Event): void {
    const field = event.target as HTMLInputElement;
    const { text, value } = parseCountInput(field.value);
    if (field.value !== text) {
      field.value = text;
    }
    this.changed.emit({ uid: item.uid, campo, valor: value });
  }

  protected isInvalid(value: number | null): boolean {
    return value === null || value < ROTINA_LIMITS.valorMin;
  }
}
