/** Formato dos dados trafegados com a API (`/exercicios`, `/rotinas`). */

export interface ExercicioDto {
  id: string;
  nome: string;
  musculo: string;
  descricao: string | null;
  criado_em: string;
}

export interface ItemRotinaDto {
  id: string;
  series: string;
  repeticoes: string;
  ordem: number;
  exercicio: ExercicioDto;
}

export interface DiaRotinaDto {
  id: string;
  nome: string;
  ordem: number;
  itens: ItemRotinaDto[];
}

export interface RotinaDto {
  id: string;
  usuario_id: string;
  nome: string;
  criado_em: string;
  atualizado_em: string;
  dias: DiaRotinaDto[];
}

export interface RotinaPayload {
  nome: string;
  dias: {
    nome: string;
    ordem: number;
    itens: {
      exercicio_id: string;
      series: string;
      repeticoes: string;
      ordem: number;
    }[];
  }[];
}
