import { HttpClient, HttpParams, HttpResponse } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, map } from 'rxjs';

import { API_URL, ApiResponse, Page } from '../../../core/api/api.models';
import { ExercicioDto, RotinaDto } from './rotina-api.models';
import { fromRotinaDto, toExercicio, toRotinaPayload } from './rotina.mapper';
import { Exercicio, Rotina, RotinaDraft } from './rotina.models';

export interface ExerciciosQuery {
  nome?: string;
  musculo?: string;
}

export interface ArquivoPlanilha {
  blob: Blob;
  filename: string | null;
}

/** O catálogo é pequeno: uma página grande evita esconder exercícios da biblioteca. */
const EXERCICIOS_PAGE_SIZE = 100;

@Injectable({ providedIn: 'root' })
export class ExerciciosApi {
  private readonly http = inject(HttpClient);
  private readonly url = `${inject(API_URL)}/exercicios`;

  listar(query: ExerciciosQuery = {}): Observable<Exercicio[]> {
    let params = new HttpParams().set('page_size', EXERCICIOS_PAGE_SIZE);
    if (query.nome?.trim()) {
      params = params.set('nome', query.nome.trim());
    }
    if (query.musculo) {
      params = params.set('musculo', query.musculo);
    }
    return this.http
      .get<ApiResponse<Page<ExercicioDto>>>(this.url, { params })
      .pipe(map(response => response.data.items.map(toExercicio)));
  }

  listarMusculos(): Observable<string[]> {
    return this.http
      .get<ApiResponse<string[]>>(`${this.url}/musculos`)
      .pipe(map(response => response.data));
  }
}

@Injectable({ providedIn: 'root' })
export class RotinasApi {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = inject(API_URL);
  private readonly url = `${this.apiUrl}/rotinas`;

  listar(): Observable<Rotina[]> {
    return this.http
      .get<ApiResponse<RotinaDto[]>>(this.url)
      .pipe(map(response => response.data.map(fromRotinaDto)));
  }

  buscar(id: string): Observable<Rotina> {
    return this.http
      .get<ApiResponse<RotinaDto>>(`${this.url}/${id}`)
      .pipe(map(response => fromRotinaDto(response.data)));
  }

  criar(draft: RotinaDraft): Observable<Rotina> {
    return this.http
      .post<ApiResponse<RotinaDto>>(this.url, toRotinaPayload(draft))
      .pipe(map(response => fromRotinaDto(response.data)));
  }

  atualizar(id: string, draft: RotinaDraft): Observable<Rotina> {
    return this.http
      .put<ApiResponse<RotinaDto>>(`${this.url}/${id}`, toRotinaPayload(draft))
      .pipe(map(response => fromRotinaDto(response.data)));
  }

  excluir(id: string): Observable<void> {
    return this.http.delete<void>(`${this.url}/${id}`);
  }

  exportarPlanilha(rotinaId: string): Observable<ArquivoPlanilha> {
    return this.http
      .post(
        `${this.apiUrl}/planilha/export`,
        { rotina_id: rotinaId },
        { observe: 'response', responseType: 'blob' },
      )
      .pipe(
        map((response: HttpResponse<Blob>) => ({
          blob: response.body ?? new Blob(),
          filename: filenameFromContentDisposition(response.headers.get('Content-Disposition')),
        })),
      );
  }
}

export function filenameFromContentDisposition(header: string | null): string | null {
  const match = header?.match(/filename\*?=(?:UTF-8'')?"?([^";]+)"?/i);
  return match ? decodeURIComponent(match[1]) : null;
}
