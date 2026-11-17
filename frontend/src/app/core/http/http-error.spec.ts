import { HttpErrorResponse } from '@angular/common/http';

import { DEFAULT_ERROR_MESSAGE, getErrorMessage } from './http-error';

function httpError(status: number, error: unknown = null): HttpErrorResponse {
  return new HttpErrorResponse({ status, error });
}

describe('getErrorMessage', () => {
  it('usa a mensagem enviada pela API', () => {
    const error = httpError(409, {
      error: { code: 'conflict', message: 'E-mail já cadastrado.', request_id: 'r1' },
    });

    expect(getErrorMessage(error)).toBe('E-mail já cadastrado.');
  });

  it('informa falha de conexão quando o status é 0', () => {
    expect(getErrorMessage(httpError(0))).toBe('Não foi possível conectar ao servidor.');
  });

  it('usa a mensagem padrão do status quando o corpo não segue o formato da API', () => {
    expect(getErrorMessage(httpError(404, { detail: 'x' }))).toBe(
      'O recurso solicitado não foi encontrado.',
    );
    expect(getErrorMessage(httpError(500, '<html>'))).toBe(
      'O servidor encontrou um erro ao processar a solicitação.',
    );
  });

  it('usa o fallback informado para status desconhecido ou erro que não é HTTP', () => {
    expect(getErrorMessage(httpError(418), 'Falhou.')).toBe('Falhou.');
    expect(getErrorMessage(new Error('boom'))).toBe(DEFAULT_ERROR_MESSAGE);
  });
});
