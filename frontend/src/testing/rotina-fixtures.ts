import { RotinaDto } from '../app/features/rotina/data/rotina-api.models';
import { Exercicio } from '../app/features/rotina/data/rotina.models';

export const SUPINO: Exercicio = {
  id: 'ex-supino',
  nome: 'Supino reto com barra',
  musculo: 'Peito',
  descricao: null,
};

export const AGACHAMENTO: Exercicio = {
  id: 'ex-agachamento',
  nome: 'Agachamento livre',
  musculo: 'Pernas',
  descricao: 'Base',
};

export function rotinaDto(overrides: Partial<RotinaDto> = {}): RotinaDto {
  return {
    id: 'rotina-1',
    usuario_id: 'user-1',
    nome: 'Treino A',
    criado_em: '2026-11-17T10:00:00Z',
    atualizado_em: '2026-11-17T10:00:00Z',
    dias: [
      {
        id: 'dia-quarta',
        nome: 'Quarta',
        ordem: 2,
        itens: [],
      },
      {
        id: 'dia-segunda',
        nome: 'Segunda',
        ordem: 1,
        itens: [
          {
            id: 'item-2',
            series: '3',
            repeticoes: '8-12',
            ordem: 2,
            exercicio: { ...AGACHAMENTO, criado_em: '' },
          },
          {
            id: 'item-1',
            series: '4',
            repeticoes: '10',
            ordem: 1,
            exercicio: { ...SUPINO, criado_em: '' },
          },
        ],
      },
    ],
    ...overrides,
  };
}
