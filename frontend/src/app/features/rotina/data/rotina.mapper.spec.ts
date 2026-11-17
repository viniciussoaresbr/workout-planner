import { AGACHAMENTO, SUPINO, rotinaDto } from '../../../../testing/rotina-fixtures';
import {
  createDefaultDays,
  createItem,
  fromRotinaDto,
  toResumo,
  toRotinaPayload,
} from './rotina.mapper';
import { filenameFromContentDisposition } from './rotinas.api';

describe('rotina.mapper', () => {
  it('converte a resposta da API ordenando dias e itens', () => {
    const rotina = fromRotinaDto(rotinaDto());

    expect(rotina.dias.map(dia => dia.nome)).toEqual(['Segunda', 'Quarta']);
    expect(rotina.dias[0].key).toBe('dia-segunda');
    expect(rotina.dias[0].itens.map(item => item.exercicio.nome)).toEqual([
      SUPINO.nome,
      AGACHAMENTO.nome,
    ]);
    expect(rotina.dias[0].itens[0]).toMatchObject({ series: 4, repeticoes: 10 });
  });

  it('usa o início numérico de faixas como "8-12"', () => {
    const [, agachamento] = fromRotinaDto(rotinaDto()).dias[0].itens;

    expect(agachamento.repeticoes).toBe(8);
  });

  it('gera um uid diferente para cada ocorrência do mesmo exercício', () => {
    const a = createItem(SUPINO);
    const b = createItem(SUPINO);

    expect(a.uid).not.toBe(b.uid);
    expect(a).toMatchObject({ exercicio: SUPINO, series: 4, repeticoes: 12 });
  });

  it('monta o payload com ordem sequencial e valores em texto', () => {
    const dias = createDefaultDays();
    dias[0].itens = [createItem(SUPINO, 5, 5), createItem(AGACHAMENTO, 3, 15)];

    const payload = toRotinaPayload({ nome: '  Treino A  ', dias });

    expect(payload.nome).toBe('Treino A');
    expect(payload.dias).toHaveLength(7);
    expect(payload.dias[0]).toEqual({
      nome: 'Segunda',
      ordem: 1,
      itens: [
        { exercicio_id: SUPINO.id, series: '5', repeticoes: '5', ordem: 1 },
        { exercicio_id: AGACHAMENTO.id, series: '3', repeticoes: '15', ordem: 2 },
      ],
    });
    expect(payload.dias[6]).toEqual({ nome: 'Domingo', ordem: 7, itens: [] });
  });

  it('resume a rotina para os cards', () => {
    const resumo = toResumo(fromRotinaDto(rotinaDto()));

    expect(resumo).toEqual({
      id: 'rotina-1',
      nome: 'Treino A',
      totalExercicios: 2,
      grupos: ['Peito', 'Pernas'],
    });
  });

  it.each([
    ['attachment; filename="rotina-treino-a.xlsx"', 'rotina-treino-a.xlsx'],
    ["attachment; filename*=UTF-8''rotina%20p%C3%A9.xlsx", 'rotina pé.xlsx'],
    [null, null],
    ['inline', null],
  ])('extrai o nome do arquivo de %s', (header, expected) => {
    expect(filenameFromContentDisposition(header)).toBe(expected);
  });
});
