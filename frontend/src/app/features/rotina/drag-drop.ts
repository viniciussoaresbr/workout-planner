import { CdkDragDrop } from '@angular/cdk/drag-drop';

import { Exercicio, ItemTreino } from './data/rotina.models';

/** `cdkDropListData` da biblioteca; os dias usam a própria `key`. */
export const BIBLIOTECA_LIST = 'biblioteca';

/** Evento de drop entre biblioteca e dias: os dados da lista são o identificador do contêiner. */
export type RotinaDrop = CdkDragDrop<string, string, Exercicio | ItemTreino>;
