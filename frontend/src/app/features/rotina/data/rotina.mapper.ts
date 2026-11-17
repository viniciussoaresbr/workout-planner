import { ExercicioDto, RotinaDto, RotinaPayload } from './rotina-api.models';
import {
  DEFAULT_REPETICOES,
  DEFAULT_SERIES,
  DIAS_DA_SEMANA,
  DiaTreino,
  Exercicio,
  ItemTreino,
  Rotina,
  RotinaDraft,
  RotinaResumo,
} from './rotina.models';

export function newUid(): string {
  return crypto.randomUUID();
}

export function toExercicio(dto: ExercicioDto): Exercicio {
  return { id: dto.id, nome: dto.nome, musculo: dto.musculo, descricao: dto.descricao };
}

/** Cria uma nova ocorrência do exercício na rotina (sempre com `uid` próprio). */
export function createItem(
  exercicio: Exercicio,
  series: number | null = DEFAULT_SERIES,
  repeticoes: number | null = DEFAULT_REPETICOES,
): ItemTreino {
  return { uid: newUid(), exercicio, series, repeticoes };
}

export function createDefaultDays(): DiaTreino[] {
  return DIAS_DA_SEMANA.map((nome, index) => ({ key: `dia-${index + 1}`, nome, itens: [] }));
}

function parseCount(value: string, fallback: number): number {
  const parsed = Number.parseInt(value, 10);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : fallback;
}

export function fromRotinaDto(dto: RotinaDto): Rotina {
  return {
    id: dto.id,
    nome: dto.nome,
    dias: [...dto.dias]
      .sort((a, b) => a.ordem - b.ordem)
      .map(dia => ({
        key: dia.id,
        nome: dia.nome,
        itens: [...dia.itens]
          .sort((a, b) => a.ordem - b.ordem)
          .map(item =>
            createItem(
              toExercicio(item.exercicio),
              parseCount(item.series, DEFAULT_SERIES),
              parseCount(item.repeticoes, DEFAULT_REPETICOES),
            ),
          ),
      })),
  };
}

/** Converte o rascunho em payload da API. Deve ser chamado apenas com o rascunho válido. */
export function toRotinaPayload(draft: RotinaDraft): RotinaPayload {
  return {
    nome: draft.nome.trim(),
    dias: draft.dias.map((dia, diaIndex) => ({
      nome: dia.nome,
      ordem: diaIndex + 1,
      itens: dia.itens.map((item, itemIndex) => ({
        exercicio_id: item.exercicio.id,
        series: String(item.series ?? DEFAULT_SERIES),
        repeticoes: String(item.repeticoes ?? DEFAULT_REPETICOES),
        ordem: itemIndex + 1,
      })),
    })),
  };
}

export function toResumo(rotina: Rotina): RotinaResumo {
  const itens = rotina.dias.flatMap(dia => dia.itens);
  return {
    id: rotina.id,
    nome: rotina.nome,
    totalExercicios: itens.length,
    diasComTreino: rotina.dias.filter(dia => dia.itens.length > 0).length,
    grupos: [...new Set(itens.map(item => item.exercicio.musculo))],
  };
}
