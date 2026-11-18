import { FormControl, FormGroup } from '@angular/forms';

import { validationMessage } from './field-error';
import { AppValidators } from './validators';

describe('AppValidators', () => {
  const run = (validator: (c: FormControl) => unknown, value: unknown) =>
    validator(new FormControl(value));

  it('email exige domínio com ponto e ignora espaços nas pontas', () => {
    for (const valido of ['ana@exemplo.com', ' ana.silva+treino@mail.exemplo.com.br ', '']) {
      expect(run(AppValidators.email, valido), valido).toBeNull();
    }
    for (const invalido of ['ana', 'ana@exemplo', 'ana@.com', 'a na@exemplo.com', 'ana@@x.com']) {
      expect(run(AppValidators.email, invalido), invalido).toEqual({ email: true });
    }
  });

  it('requiredTrimmed rejeita texto vazio ou só com espaços', () => {
    expect(run(AppValidators.requiredTrimmed, '   ')).toEqual({ required: true });
    expect(run(AppValidators.requiredTrimmed, '')).toEqual({ required: true });
    expect(run(AppValidators.requiredTrimmed, ' Ana ')).toBeNull();
  });

  it('minLengthTrimmed conta só o texto sem espaços nas pontas', () => {
    const validator = AppValidators.minLengthTrimmed(3);
    expect(run(validator, '  ab  ')).toEqual({ minlength: { requiredLength: 3, actualLength: 2 } });
    expect(run(validator, ' abc ')).toBeNull();
    expect(run(validator, '')).toBeNull(); // obrigatoriedade é outro validador
  });

  it('noEdgeWhitespace rejeita espaços no início ou no fim', () => {
    expect(run(AppValidators.noEdgeWhitespace, ' senha123')).toEqual({ edgeWhitespace: true });
    expect(run(AppValidators.noEdgeWhitespace, 'senha123 ')).toEqual({ edgeWhitespace: true });
    expect(run(AppValidators.noEdgeWhitespace, 'senha com espaço 1')).toBeNull();
  });

  it('passwordStrength exige letra e número', () => {
    expect(run(AppValidators.passwordStrength, 'somenteletras')).toEqual({
      passwordStrength: true,
    });
    expect(run(AppValidators.passwordStrength, '12345678')).toEqual({ passwordStrength: true });
    expect(run(AppValidators.passwordStrength, 'çãoé1234')).toBeNull();
    expect(run(AppValidators.passwordStrength, '')).toBeNull();
  });

  it('matches compara com o controle irmão', () => {
    const form = new FormGroup({
      password: new FormControl('senha123'),
      confirm: new FormControl('', AppValidators.matches('password')),
    });
    expect(form.controls.confirm.errors).toBeNull(); // vazio fica a cargo do `required`

    form.controls.confirm.setValue('outra');
    expect(form.controls.confirm.errors).toEqual({ mismatch: true });

    form.controls.confirm.setValue('senha123');
    expect(form.controls.confirm.errors).toBeNull();
  });

  it('cada erro tem uma mensagem própria', () => {
    expect(validationMessage({ edgeWhitespace: true })).toBe(
      'Não use espaços no início ou no fim.',
    );
    expect(validationMessage({ passwordStrength: true })).toBe(
      'Use pelo menos uma letra e um número.',
    );
    expect(validationMessage({ mismatch: true })).toBe('As senhas não coincidem.');
  });
});
