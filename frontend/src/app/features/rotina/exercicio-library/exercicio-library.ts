import { CdkDrag, CdkDropList } from '@angular/cdk/drag-drop';
import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  linkedSignal,
  output,
  signal,
} from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { heroPlus } from '@ng-icons/heroicons/outline';
import { catchError, debounceTime, distinctUntilChanged, finalize, of, switchMap } from 'rxjs';

import { Exercicio } from '../data/rotina.models';
import { ExerciciosApi } from '../data/rotinas.api';
import { BIBLIOTECA_LIST, RotinaDrop } from '../drag-drop';

const SEARCH_DEBOUNCE_MS = 250;

@Component({
  selector: 'app-exercicio-library',
  imports: [CdkDropList, CdkDrag, NgIcon],
  providers: [provideIcons({ heroPlus })],
  templateUrl: './exercicio-library.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ExercicioLibrary {
  private readonly api = inject(ExerciciosApi);

  readonly added = output<Exercicio>();
  readonly dropped = output<RotinaDrop>();

  protected readonly listId = BIBLIOTECA_LIST;
  protected readonly loading = signal(false);

  protected readonly musculos = toSignal(this.api.listarMusculos().pipe(catchError(() => of([]))), {
    initialValue: [] as string[],
  });
  /** Começa no primeiro grupo disponível; depois segue a escolha do usuário. */
  protected readonly musculo = linkedSignal(() => this.musculos()[0] ?? '');
  protected readonly busca = signal('');

  private readonly query = computed(() => ({ musculo: this.musculo(), nome: this.busca() }));

  protected readonly exercicios = toSignal(
    toObservable(this.query).pipe(
      debounceTime(SEARCH_DEBOUNCE_MS),
      distinctUntilChanged((a, b) => a.musculo === b.musculo && a.nome.trim() === b.nome.trim()),
      switchMap(query => {
        if (!query.musculo) {
          return of([]);
        }
        this.loading.set(true);
        return this.api.listar(query).pipe(
          catchError(() => of([])),
          finalize(() => this.loading.set(false)),
        );
      }),
    ),
    { initialValue: [] as Exercicio[] },
  );

  /** A biblioteca só fornece itens; nada pode ser solto nela. */
  protected readonly noEnter = (): boolean => false;

  protected selectMusculo(musculo: string): void {
    this.musculo.set(musculo);
    this.busca.set('');
  }
}
