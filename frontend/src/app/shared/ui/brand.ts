import { ChangeDetectionStrategy, Component } from '@angular/core';

/** Marca do produto (ícone + nome). */
@Component({
  selector: 'app-brand',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: { class: 'inline-flex items-center gap-2.5' },
  template: `
    <svg class="size-7 shrink-0" viewBox="0 0 32 32" aria-hidden="true">
      <rect width="32" height="32" rx="8" class="fill-brand-950" />
      <g class="fill-brand-300">
        <rect x="5" y="11" width="4" height="10" rx="1.5" />
        <rect x="23" y="11" width="4" height="10" rx="1.5" />
        <rect x="9" y="13" width="3" height="6" rx="1" />
        <rect x="20" y="13" width="3" height="6" rx="1" />
        <rect x="12" y="15" width="8" height="2" rx="1" />
      </g>
    </svg>
    <span class="text-[0.95rem] font-semibold tracking-tight text-white">Workout Planner</span>
  `,
})
export class Brand {}
