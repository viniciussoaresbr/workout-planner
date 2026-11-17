/** Modelos de domínio usados pela tela (independentes do formato da API). */

export interface Exercicio {
  id: string;
  nome: string;
  musculo: string;
  descricao: string | null;
}

/** Exercício colocado em um dia da rotina. `uid` identifica a ocorrência (o mesmo exercício pode repetir). */
export interface ItemTreino {
  uid: string;
  exercicio: Exercicio;
  /** `null` enquanto o campo estiver vazio na edição. */
  series: number | null;
  repeticoes: number | null;
}

export interface DiaTreino {
  /** Chave estável usada na tela; não é persistida. */
  key: string;
  nome: string;
  itens: ItemTreino[];
}

export interface Rotina {
  id: string;
  nome: string;
  dias: DiaTreino[];
}

export interface RotinaDraft {
  nome: string;
  dias: DiaTreino[];
}

export interface RotinaResumo {
  id: string;
  nome: string;
  totalExercicios: number;
  grupos: string[];
}

export const ROTINA_LIMITS = {
  nomeMin: 3,
  nomeMax: 100,
  exerciciosPorDia: 10,
  valorMin: 1,
  valorMax: 999,
} as const;

export const DEFAULT_SERIES = 4;
export const DEFAULT_REPETICOES = 12;

export const DIAS_DA_SEMANA = [
  'Segunda',
  'Terça',
  'Quarta',
  'Quinta',
  'Sexta',
  'Sábado',
  'Domingo',
] as const;
