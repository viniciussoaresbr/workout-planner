import { CdkDropListGroup } from '@angular/cdk/drag-drop';
import { ChangeDetectionStrategy, Component, OnInit, inject } from '@angular/core';
import { Router } from '@angular/router';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { heroArrowPath } from '@ng-icons/heroicons/outline';

import { AuthService } from '../../../core/auth/auth.service';
import { ToastService } from '../../../core/notifications/toast.service';
import { ConfirmService } from '../../../shared/utils/confirm.service';
import { Exercicio, ROTINA_LIMITS } from '../data/rotina.models';
import { DiaTreinoCard, ItemChange } from '../dia-treino/dia-treino';
import { BIBLIOTECA_LIST, RotinaDrop } from '../drag-drop';
import { ExercicioLibrary } from '../exercicio-library/exercicio-library';
import { RotinasSalvas } from '../rotinas-salvas/rotinas-salvas';
import { RotinaEditorStore } from '../state/rotina-editor.store';

@Component({
  selector: 'app-rotina-builder',
  imports: [CdkDropListGroup, NgIcon, DiaTreinoCard, ExercicioLibrary, RotinasSalvas],
  providers: [RotinaEditorStore, provideIcons({ heroArrowPath })],
  templateUrl: './rotina-builder.html',
  styleUrl: './rotina-builder.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RotinaBuilder implements OnInit {
  protected readonly store = inject(RotinaEditorStore);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly toast = inject(ToastService);
  private readonly confirm = inject(ConfirmService);

  protected readonly nomeMax = ROTINA_LIMITS.nomeMax;

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

  protected logout(): void {
    const leave =
      !this.store.hasUnsavedChanges() ||
      this.confirm.ask('Há alterações não salvas nesta rotina. Deseja sair mesmo assim?');
    if (!leave) {
      return;
    }
    this.auth.logout();
    void this.router.navigate(['/login']);
  }
}
