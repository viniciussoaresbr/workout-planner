export interface Exercicio {
  id: string;
  nome: string;
  musculo: string;
  youtubeUrl?: string | null;
  descricao?: string | null;
  equipamento?: string | null;
}

export interface BackendExercicio {
  id: string;
  nome: string;
  musculo: string;
  descricao?: string | null;
  youtubeUrl?: string | null;
}

export interface ExerciciosListResponse {
  items: Exercicio[];
  total: number;
  page: number;
  pageSize: number;
}

export interface ExerciciosQueryParams {
  busca?: string;
  musculo?: string;
  page?: number;
}
