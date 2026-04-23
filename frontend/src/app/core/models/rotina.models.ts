import { Exercicio } from './exercicio.models';

export interface ExercicioRotina extends Exercicio {
  uid?: string;
  series: number;
  repeticoes: number;
}

export interface DiaTreino {
  id: string;
  nome: string;
  exercicios: ExercicioRotina[];
}

export interface RotinaPayload {
  id?: string;
  nome: string;
  dias: DiaTreino[];
}

export interface RotinaResponse extends RotinaPayload {
  id: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface BackendItemRotina {
  id: string;
  series: string;
  repeticoes: string;
  ordem: number;
  exercicio: {
    id: string;
    nome: string;
    musculo: string;
    descricao?: string | null;
  };
}

export interface BackendDiaRotina {
  id: string;
  nome: string;
  ordem: number;
  itens: BackendItemRotina[];
}

export interface BackendRotinaResponse {
  id: string;
  nome: string;
  dias: BackendDiaRotina[];
}
