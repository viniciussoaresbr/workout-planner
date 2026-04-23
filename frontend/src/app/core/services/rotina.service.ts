import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';

import { environment } from '../../../environments/environment';
import { ApiSuccessResponse } from '../models/api.models';
import {
  BackendRotinaResponse,
  RotinaPayload,
  RotinaResponse,
} from '../models/rotina.models';

@Injectable({
  providedIn: 'root',
})
export class RotinaService {
  private readonly rotinasUrl = `${environment.apiUrl}/rotinas`;
  private readonly planilhaUrl = `${environment.apiUrl}/planilha/export`;

  constructor(private readonly http: HttpClient) {}

  criar(payload: RotinaPayload): Observable<RotinaResponse> {
    return this.http
      .post<
        ApiSuccessResponse<BackendRotinaResponse>
      >(this.rotinasUrl, this.toBackendPayload(payload))
      .pipe(map(response => this.mapRotinaResponse(response.data)));
  }

  listar(): Observable<RotinaResponse[]> {
    return this.http
      .get<ApiSuccessResponse<BackendRotinaResponse[]>>(this.rotinasUrl)
      .pipe(
        map(response =>
          response.data.map(item => this.mapRotinaResponse(item)),
        ),
      );
  }

  buscarPorId(id: string): Observable<RotinaResponse> {
    return this.http
      .get<
        ApiSuccessResponse<BackendRotinaResponse>
      >(`${this.rotinasUrl}/${id}`)
      .pipe(map(response => this.mapRotinaResponse(response.data)));
  }

  atualizar(id: string, payload: RotinaPayload): Observable<RotinaResponse> {
    return this.http
      .put<
        ApiSuccessResponse<BackendRotinaResponse>
      >(`${this.rotinasUrl}/${id}`, this.toBackendPayload(payload))
      .pipe(map(response => this.mapRotinaResponse(response.data)));
  }

  deletar(id: string): Observable<void> {
    return this.http.delete<void>(`${this.rotinasUrl}/${id}`);
  }

  gerarPlanilha(id: string): Observable<Blob> {
    return this.http.post(
      this.planilhaUrl,
      {
        rotina_id: id,
      },
      {
        responseType: 'blob',
      },
    );
  }

  private mapRotinaResponse(response: BackendRotinaResponse): RotinaResponse {
    return {
      id: response.id,
      nome: response.nome,
      dias: response.dias
        .slice()
        .sort((a, b) => a.ordem - b.ordem)
        .map(dia => ({
          id: dia.id,
          nome: dia.nome,
          exercicios: dia.itens
            .slice()
            .sort((a, b) => a.ordem - b.ordem)
            .map(item => ({
              id: item.exercicio.id,
              nome: item.exercicio.nome,
              musculo: item.exercicio.musculo,
              descricao: item.exercicio.descricao ?? null,
              series: Number.parseInt(item.series, 10) || 4,
              repeticoes: Number.parseInt(item.repeticoes, 10) || 12,
            })),
        })),
    };
  }

  private toBackendPayload(payload: RotinaPayload): unknown {
    return {
      nome: payload.nome,
      dias: payload.dias.map((dia, diaIndex) => ({
        nome: dia.nome,
        ordem: diaIndex + 1,
        itens: dia.exercicios.map((exercicio, exercicioIndex) => ({
          exercicio_id: exercicio.id,
          series: String(exercicio.series),
          repeticoes: String(exercicio.repeticoes),
          ordem: exercicioIndex + 1,
        })),
      })),
    };
  }
}
