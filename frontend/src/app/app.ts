import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

import { ToastContainer } from './core/notifications/toast-container';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, ToastContainer],
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: { class: 'block min-h-screen bg-slate-950 text-slate-100' },
  template: `
    <router-outlet />
    <app-toast-container />
  `,
})
export class App {}
