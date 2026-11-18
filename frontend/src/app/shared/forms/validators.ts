import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

/**
 * E-mail com domínio de pelo menos dois rótulos (ex.: `ana@exemplo.com`), como a API exige.
 * O `Validators.email` do Angular aceita `ana@exemplo`, que a API rejeitaria.
 * Espaços nas pontas são ignorados (o valor é aparado antes do envio).
 */
const EMAIL_PATTERN = /^[^\s@]+@[^\s@.]+(\.[^\s@.]+)+$/;

function text(control: AbstractControl): string {
  return typeof control.value === 'string' ? control.value : '';
}

export const AppValidators = {
  email(control: AbstractControl): ValidationErrors | null {
    const value = text(control).trim();
    return !value || EMAIL_PATTERN.test(value) ? null : { email: true };
  },

  /** Obrigatório, sem aceitar só espaços. */
  requiredTrimmed(control: AbstractControl): ValidationErrors | null {
    return text(control).trim() ? null : { required: true };
  },

  /** `minLength` contando apenas o texto sem espaços nas pontas. */
  minLengthTrimmed(min: number): ValidatorFn {
    return control => {
      const length = text(control).trim().length;
      return length === 0 || length >= min
        ? null
        : { minlength: { requiredLength: min, actualLength: length } };
    };
  },

  /** A API remove espaços nas pontas; aceitá-los faria a senha salva diferir da digitada. */
  noEdgeWhitespace(control: AbstractControl): ValidationErrors | null {
    const value = text(control);
    return value === value.trim() ? null : { edgeWhitespace: true };
  },

  /** Exige ao menos uma letra e um número. */
  passwordStrength(control: AbstractControl): ValidationErrors | null {
    const value = text(control);
    if (!value) {
      return null;
    }
    return /\p{L}/u.test(value) && /\d/.test(value) ? null : { passwordStrength: true };
  },

  /** Valida que o controle tem o mesmo valor do controle irmão `otherName`. */
  matches(otherName: string): ValidatorFn {
    return control => {
      const other = control.parent?.get(otherName);
      if (!other || !control.value) {
        return null;
      }
      return control.value === other.value ? null : { mismatch: true };
    };
  },
};
