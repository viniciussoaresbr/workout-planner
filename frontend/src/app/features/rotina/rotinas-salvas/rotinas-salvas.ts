import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { heroClipboardDocumentList } from '@ng-icons/heroicons/outline';

import { RotinaResumo } from '../data/rotina.models';

@Component({
  selector: 'app-rotinas-salvas',
  imports: [NgIcon],
  providers: [provideIcons({ heroClipboardDocumentList })],
  templateUrl: './rotinas-salvas.html',
  styleUrl: './rotinas-salvas.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RotinasSalvas {
  readonly rotinas = input.required<RotinaResumo[]>();
  readonly selectedId = input<string | null>(null);
  readonly loadingId = input<string | null>(null);
  readonly loading = input(false);
  readonly disabled = input(false);

  readonly selected = output<string>();
}
