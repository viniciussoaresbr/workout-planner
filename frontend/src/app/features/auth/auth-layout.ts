import { ChangeDetectionStrategy, Component } from '@angular/core';

import { Brand } from '../../shared/ui/brand';

/** Moldura das telas de login e cadastro: apresentação à esquerda, formulário à direita. */
@Component({
  selector: 'app-auth-layout',
  imports: [Brand],
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: { class: 'block' },
  template: `
    <main id="conteudo" class="grid min-h-dvh lg:grid-cols-[1.1fr_1fr]">
      <aside
        class="relative hidden flex-col justify-between overflow-hidden border-r border-white/[0.06] p-12 lg:flex xl:p-16"
      >
        <div
          class="pointer-events-none absolute -bottom-40 -left-40 size-[36rem] rounded-full bg-brand-500/10 blur-3xl"
          aria-hidden="true"
        ></div>

        <app-brand />

        <div class="relative max-w-lg">
          <h1 class="text-5xl leading-[1.05] font-semibold tracking-tight text-white xl:text-6xl">
            Sua semana de treino, montada em minutos.
          </h1>
          <p class="mt-6 max-w-md text-lg leading-8 text-slate-400">
            Escolha os exercícios, distribua pelos dias e ajuste séries e repetições sem planilha
            nenhuma — até a hora de exportar uma.
          </p>

          <ol class="mt-10 space-y-4">
            @for (passo of passos; track passo; let i = $index) {
              <li class="flex items-center gap-4 text-slate-300">
                <span
                  class="flex size-8 shrink-0 items-center justify-center rounded-lg border border-line text-sm font-medium text-brand-300 tabular-nums"
                >
                  {{ i + 1 }}
                </span>
                {{ passo }}
              </li>
            }
          </ol>
        </div>

        <p class="relative text-sm text-slate-500">
          Exportação para Excel (.xlsx) e PDF · suas rotinas ficam salvas na sua conta
        </p>
      </aside>

      <div class="flex flex-col justify-center px-6 py-12 sm:px-12">
        <div class="mx-auto w-full max-w-sm">
          <app-brand class="mb-12 lg:hidden" />
          <ng-content />
        </div>
      </div>
    </main>
  `,
})
export class AuthLayout {
  protected readonly passos = [
    'Filtre exercícios por grupo muscular',
    'Arraste para os dias da semana',
    'Exporte a rotina em planilha ou PDF',
  ];
}
