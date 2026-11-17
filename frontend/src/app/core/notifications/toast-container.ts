import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { NgIcon, provideIcons } from '@ng-icons/core';
import {
  heroCheckCircle,
  heroExclamationCircle,
  heroExclamationTriangle,
  heroInformationCircle,
  heroXMark,
} from '@ng-icons/heroicons/outline';

import { ToastService, ToastType } from './toast.service';

const STYLES: Readonly<Record<ToastType, { icon: string; classes: string }>> = {
  success: { icon: 'heroCheckCircle', classes: 'border-emerald-400/40 text-emerald-100' },
  error: { icon: 'heroExclamationCircle', classes: 'border-rose-400/40 text-rose-100' },
  warning: { icon: 'heroExclamationTriangle', classes: 'border-amber-400/40 text-amber-100' },
  info: { icon: 'heroInformationCircle', classes: 'border-cyan-400/40 text-cyan-100' },
};

@Component({
  selector: 'app-toast-container',
  imports: [NgIcon],
  providers: [
    provideIcons({
      heroCheckCircle,
      heroExclamationCircle,
      heroExclamationTriangle,
      heroInformationCircle,
      heroXMark,
    }),
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div
      class="pointer-events-none fixed top-4 right-4 z-50 flex w-[min(24rem,calc(100vw-2rem))] flex-col gap-3"
      aria-live="polite"
    >
      @for (toast of toastService.toasts(); track toast.id) {
        <div
          class="pointer-events-auto flex items-start gap-3 rounded-2xl border bg-slate-900/95 px-4 py-3 text-sm shadow-xl shadow-slate-950/40 backdrop-blur-sm"
          [class]="styles[toast.type].classes"
          [attr.role]="toast.type === 'error' ? 'alert' : 'status'"
        >
          <ng-icon class="mt-0.5 shrink-0 text-lg" [name]="styles[toast.type].icon" />
          <p class="flex-1 leading-5">{{ toast.message }}</p>
          <button
            type="button"
            class="shrink-0 rounded-md text-slate-400 transition hover:text-white"
            aria-label="Fechar notificação"
            (click)="toastService.dismiss(toast.id)"
          >
            <ng-icon name="heroXMark" />
          </button>
        </div>
      }
    </div>
  `,
})
export class ToastContainer {
  protected readonly toastService = inject(ToastService);
  protected readonly styles = STYLES;
}
