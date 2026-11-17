import {
  ChangeDetectionStrategy,
  Component,
  ElementRef,
  effect,
  inject,
  viewChild,
} from '@angular/core';

import { ConfirmService } from './confirm.service';

/** Diálogo modal nativo (`<dialog>`): prende o foco, fecha com Esc e devolve a resposta. */
@Component({
  selector: 'app-confirm-dialog',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <dialog
      #dialog
      class="m-auto w-[min(26rem,calc(100vw-2rem))] rounded-2xl border border-line bg-surface p-0 text-slate-100 shadow-2xl shadow-black/50 backdrop:bg-canvas/70 backdrop:backdrop-blur-xs"
      aria-labelledby="confirm-title"
      aria-describedby="confirm-message"
      (cancel)="answer(false, $event)"
    >
      @if (confirm.request(); as request) {
        <div class="p-6">
          <h2 id="confirm-title" class="text-lg font-semibold tracking-tight text-white">
            {{ request.title }}
          </h2>
          <p id="confirm-message" class="mt-2 text-sm leading-6 text-slate-400">
            {{ request.message }}
          </p>
        </div>
        <div class="flex justify-end gap-2 border-t border-line/70 px-6 py-4">
          <button type="button" class="btn btn-ghost" (click)="answer(false)" autofocus>
            {{ request.cancelLabel }}
          </button>
          <button
            type="button"
            class="btn"
            [class.btn-primary]="request.tone === 'default'"
            [class.btn-danger-solid]="request.tone === 'danger'"
            (click)="answer(true)"
          >
            {{ request.confirmLabel }}
          </button>
        </div>
      }
    </dialog>
  `,
})
export class ConfirmDialog {
  protected readonly confirm = inject(ConfirmService);
  private readonly dialog = viewChild.required<ElementRef<HTMLDialogElement>>('dialog');

  constructor() {
    effect(() => {
      const dialog = this.dialog().nativeElement;
      if (this.confirm.request() && !dialog.open) {
        dialog.showModal?.();
      } else if (!this.confirm.request() && dialog.open) {
        dialog.close();
      }
    });
  }

  protected answer(confirmed: boolean, event?: Event): void {
    event?.preventDefault();
    this.confirm.request()?.resolve(confirmed);
  }
}
