import { CdkDragDrop } from '@angular/cdk/drag-drop';
import { Component, EventEmitter, Input, Output } from '@angular/core';

import { DiaTreino, ExercicioRotina } from '../../../core/models/rotina.models';

@Component({
  selector: 'app-dia-treino',
  templateUrl: './dia-treino.component.html',
  styleUrls: ['./dia-treino.component.css'],
})
export class DiaTreinoComponent {
  @Input() dia!: DiaTreino;
  @Input() connectedDropLists: string[] = [];
  @Input() dropListId!: string;

  @Output() exerciseDropped = new EventEmitter<
    CdkDragDrop<ExercicioRotina[]>
  >();
  @Output() removeExercise = new EventEmitter<{
    diaId: string;
    uid?: string;
  }>();

  onDrop(event: CdkDragDrop<ExercicioRotina[]>): void {
    this.exerciseDropped.emit(event);
  }

  onRemove(uid?: string): void {
    this.removeExercise.emit({ diaId: this.dia.id, uid });
  }

  onKeyPress(event: KeyboardEvent): void {
    const isNumber = /[0-9]/.test(event.key);
    if (!isNumber) {
      event.preventDefault();
    }
  }

  onPaste(event: ClipboardEvent): void {
    const pasteData = event.clipboardData?.getData('text');
    if (pasteData && !/^\d+$/.test(pasteData)) {
      event.preventDefault();
    }
  }

  trackByExercicio(_: number, exercicio: ExercicioRotina): string {
    return exercicio.uid || exercicio.id;
  }
}
