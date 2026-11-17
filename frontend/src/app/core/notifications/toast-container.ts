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
  success: { icon: 'heroCheckCircle', classes: 'text-brand-300' },
  error: { icon: 'heroExclamationCircle', classes: 'text-rose-300' },
  warning: { icon: 'heroExclamationTriangle', classes: 'text-amber-300' },
  info: { icon: 'heroInformationCircle', classes: 'text-slate-300' },
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
  styles: `
    .toast {
      animation: toast-in 220ms cubic-bezier(0.2, 0, 0, 1);
    }
    @keyframes toast-in {
      from {
        opacity: 0;
        transform: translateY(8px);
      }
    }
  `,
  template: `
    <div
      class="pointer-events-none fixed right-4 bottom-4 z-50 flex w-[min(24rem,calc(100vw-2rem))] flex-col gap-2"
      aria-live="polite"
    >
      @for (toast of toastService.toasts(); track toast.id) {
        <div
          class="toast pointer-events-auto flex items-start gap-3 rounded-xl border border-line bg-surface-raised/95 px-4 py-3 text-sm text-slate-100 shadow-2xl shadow-black/40 backdrop-blur-sm"
          [attr.role]="toast.type === 'error' ? 'alert' : 'status'"
        >
          <ng-icon
            class="mt-px shrink-0 text-lg"
            [class]="styles[toast.type].classes"
            [name]="styles[toast.type].icon"
          />
          <p class="flex-1 leading-5">{{ toast.message }}</p>
          <button
            type="button"
            class="icon-btn -my-1 -mr-2 size-7 shrink-0"
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
