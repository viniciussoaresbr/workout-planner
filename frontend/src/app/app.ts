import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

import { ToastContainer } from './core/notifications/toast-container';
import { ConfirmDialog } from './shared/utils/confirm-dialog';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, ToastContainer, ConfirmDialog],
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: { class: 'relative z-10 block min-h-dvh' },
  template: `
    <a class="skip-link" href="#conteudo">Pular para o conteúdo</a>
    <router-outlet />
    <app-toast-container />
    <app-confirm-dialog />
  `,
})
export class App {}
