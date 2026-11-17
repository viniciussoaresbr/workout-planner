import { HttpErrorResponse } from '@angular/common/http';

import { ApiErrorBody } from '../api/api.models';

const STATUS_MESSAGES: Readonly<Record<number, string>> = {
  0: 'Não foi possível conectar ao servidor.',
  400: 'A requisição enviada é inválida.',
  401: 'Sua sessão expirou. Faça login novamente.',
  403: 'Você não tem permissão para executar esta ação.',
  404: 'O recurso solicitado não foi encontrado.',
  409: 'O recurso já existe ou entrou em conflito com outro registro.',
  422: 'Existem dados inválidos no formulário enviado.',
  500: 'O servidor encontrou um erro ao processar a solicitação.',
  503: 'O serviço está temporariamente indisponível.',
};

export const DEFAULT_ERROR_MESSAGE = 'Ocorreu um erro inesperado.';

function isApiErrorBody(body: unknown): body is ApiErrorBody {
  if (typeof body !== 'object' || body === null || !('error' in body)) {
    return false;
  }
  const { error } = body as { error: unknown };
  return (
    typeof error === 'object' &&
    error !== null &&
    typeof (error as { message?: unknown }).message === 'string'
  );
}

/** Extrai uma mensagem amigável de um erro HTTP, priorizando a mensagem enviada pela API. */
export function getErrorMessage(error: unknown, fallback = DEFAULT_ERROR_MESSAGE): string {
  if (!(error instanceof HttpErrorResponse)) {
    return fallback;
  }
  if (error.status === 0) {
    return STATUS_MESSAGES[0];
  }
  if (isApiErrorBody(error.error) && error.error.error.message.trim()) {
    return error.error.error.message;
  }
  return STATUS_MESSAGES[error.status] ?? fallback;
}
