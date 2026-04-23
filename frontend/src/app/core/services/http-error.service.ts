import { HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class HttpErrorService {
  getMessage(
    error: HttpErrorResponse,
    fallbackMessage = 'Ocorreu um erro inesperado.',
  ): string {
    if (error.status === 0) {
      return 'Nao foi possivel conectar ao servidor.';
    }

    if (typeof error.error === 'string' && error.error.trim()) {
      return error.error;
    }

    if (this.hasDetail(error.error)) {
      return error.error.detail;
    }

    if (this.hasMessage(error.error)) {
      return error.error.message;
    }

    switch (error.status) {
      case 400:
        return 'A requisicao enviada e invalida.';
      case 401:
        return 'Sua sessao expirou. Faca login novamente.';
      case 403:
        return 'Voce nao tem permissao para executar esta acao.';
      case 404:
        return 'O recurso solicitado nao foi encontrado.';
      case 409:
        return 'O recurso ja existe ou entrou em conflito com outro registro.';
      case 422:
        return 'Existem dados invalidos no formulario enviado.';
      case 500:
        return 'O servidor encontrou um erro ao processar a solicitacao.';
      default:
        return fallbackMessage;
    }
  }

  private hasDetail(error: unknown): error is { detail: string } {
    return !!error && typeof error === 'object' && 'detail' in error &&
      typeof (error as { detail: unknown }).detail === 'string';
  }

  private hasMessage(error: unknown): error is { message: string } {
    return !!error && typeof error === 'object' && 'message' in error &&
      typeof (error as { message: unknown }).message === 'string';
  }
}
