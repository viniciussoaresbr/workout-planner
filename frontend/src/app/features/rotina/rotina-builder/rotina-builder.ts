import { CdkDropListGroup } from '@angular/cdk/drag-drop';
import { CdkMenu, CdkMenuItem, CdkMenuTrigger } from '@angular/cdk/menu';
import { ConnectedPosition } from '@angular/cdk/overlay';
import { ChangeDetectionStrategy, Component, OnInit, computed, inject } from '@angular/core';
import { Router } from '@angular/router';
import { NgIcon, provideIcons } from '@ng-icons/core';
import {
  heroArrowDownTray,
  heroArrowRightStartOnRectangle,
  heroChevronDown,
  heroDocumentText,
  heroTableCells,
  heroTrash,
} from '@ng-icons/heroicons/outline';

import { AuthService } from '../../../core/auth/auth.service';
import { ToastService } from '../../../core/notifications/toast.service';
import { Brand } from '../../../shared/ui/brand';
import { Exercicio, ROTINA_LIMITS } from '../data/rotina.models';
import { DiaTreinoCard, ItemChange } from '../dia-treino/dia-treino';
import { BIBLIOTECA_LIST, RotinaDrop } from '../drag-drop';
import { ExercicioLibrary } from '../exercicio-library/exercicio-library';
import { RotinasSalvas } from '../rotinas-salvas/rotinas-salvas';
import { RotinaEditorStore } from '../state/rotina-editor.store';

/** O botão fica perto da borda direita: o menu se alinha pela direita, abrindo para baixo. */
const EXPORT_MENU_POSITION: ConnectedPosition[] = [
  { originX: 'end', originY: 'bottom', overlayX: 'end', overlayY: 'top', offsetY: 6 },
  { originX: 'end', originY: 'top', overlayX: 'end', overlayY: 'bottom', offsetY: -6 },
];

const STATUS = {
  nova: { label: 'Nova rotina', dot: 'bg-slate-500' },
  salva: { label: 'Salva', dot: 'bg-brand-400' },
  alterada: { label: 'Alterações não salvas', dot: 'bg-amber-400' },
} as const;

@Component({
  selector: 'app-rotina-builder',
  imports: [
    CdkDropListGroup,
    CdkMenu,
    CdkMenuItem,
    CdkMenuTrigger,
    NgIcon,
    Brand,
    DiaTreinoCard,
    ExercicioLibrary,
    RotinasSalvas,
  ],
  providers: [
    RotinaEditorStore,
    provideIcons({
      heroArrowDownTray,
      heroArrowRightStartOnRectangle,
      heroChevronDown,
      heroDocumentText,
      heroTableCells,
      heroTrash,
    }),
  ],
  templateUrl: './rotina-builder.html',
  styleUrl: './rotina-builder.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RotinaBuilder implements OnInit {
  protected readonly store = inject(RotinaEditorStore);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly toast = inject(ToastService);

  protected readonly nomeMax = ROTINA_LIMITS.nomeMax;
  protected readonly exportMenuPosition = EXPORT_MENU_POSITION;
  protected readonly statusLabel = computed(() => STATUS[this.store.status()].label);
  protected readonly statusDot = computed(() => STATUS[this.store.status()].dot);

  ngOnInit(): void {
    this.store.loadRotinas();
  }

  protected addExercicio(exercicio: Exercicio): void {
    const dia = this.store.addToFirstAvailableDay(exercicio);
    if (dia) {
      this.toast.success(`${exercicio.nome} adicionado a ${dia.nome}.`);
    } else {
      this.toast.warning('Todos os dias já atingiram o limite de exercícios.');
    }
  }

  protected onDrop(event: RotinaDrop): void {
    const from = event.previousContainer.data;
    const to = event.container.data;

    if (to === BIBLIOTECA_LIST) {
      return;
    }
    if (from === BIBLIOTECA_LIST) {
      this.store.insertFromLibrary(event.item.data as Exercicio, to, event.currentIndex);
    } else if (from === to) {
      this.store.moveItem(to, event.previousIndex, event.currentIndex);
    } else {
      this.store.transferItem(from, to, event.previousIndex, event.currentIndex);
    }
  }

  protected onItemChange(diaKey: string, change: ItemChange): void {
    this.store.updateItem(diaKey, change.uid, { [change.campo]: change.valor });
  }

  protected onRemove(diaKey: string, uid: string): void {
    this.store.removeItem(diaKey, uid);
  }

  protected async logout(): Promise<void> {
    if (!(await this.store.confirmDiscard())) {
      return;
    }
    this.auth.logout();
    void this.router.navigate(['/login']);
  }
}
