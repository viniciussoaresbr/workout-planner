import { ChangeDetectionStrategy, Component, computed, effect, input, signal } from '@angular/core';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { heroEye, heroEyeSlash } from '@ng-icons/heroicons/outline';

/**
 * Botão "mostrar/ocultar senha" posicionado dentro do campo. Uso:
 *
 *     <div class="relative">
 *       <input #senha type="password" class="field pr-11" ... />
 *       <app-password-toggle [input]="senha" />
 *     </div>
 */
@Component({
  selector: 'app-password-toggle',
  imports: [NgIcon],
  providers: [provideIcons({ heroEye, heroEyeSlash })],
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: { class: 'absolute inset-y-0 right-0 flex items-center pr-1.5' },
  template: `
    <button
      type="button"
      class="flex size-8 items-center justify-center rounded-md text-slate-400 transition hover:bg-white/5 hover:text-slate-100 focus-visible:text-slate-100 focus-visible:outline-2 focus-visible:outline-brand-400"
      [attr.aria-label]="actionLabel()"
      [attr.aria-pressed]="visible()"
      [attr.aria-controls]="input().id || null"
      [attr.title]="actionLabel()"
      (click)="visible.update(v => !v)"
    >
      <ng-icon [name]="visible() ? 'heroEyeSlash' : 'heroEye'" size="18" aria-hidden="true" />
    </button>
  `,
})
export class PasswordToggle {
  readonly input = input.required<HTMLInputElement>();
  /** O que o campo contém, usado no nome acessível ("Mostrar <label>"). */
  readonly label = input('senha');
  protected readonly visible = signal(false);
  protected readonly actionLabel = computed(
    () => `${this.visible() ? 'Ocultar' : 'Mostrar'} ${this.label()}`,
  );

  constructor() {
    effect(() => {
      this.input().type = this.visible() ? 'text' : 'password';
    });
  }
}
