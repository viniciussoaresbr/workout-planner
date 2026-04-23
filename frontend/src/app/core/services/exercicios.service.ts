import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';

import { environment } from '../../../environments/environment';
import { ApiSuccessResponse } from '../models/api.models';
import {
  BackendExercicio,
  ExerciciosListResponse,
  ExerciciosQueryParams,
} from '../models/exercicio.models';

@Injectable({
  providedIn: 'root',
})
export class ExerciciosService {
  private readonly exerciciosUrl = `${environment.apiUrl}/exercicios`;

  constructor(private readonly http: HttpClient) {}

  listar(params: ExerciciosQueryParams): Observable<ExerciciosListResponse> {
    let httpParams = new HttpParams();

    if (params.busca) {
      httpParams = httpParams.set('nome', params.busca);
    }

    if (params.musculo) {
      httpParams = httpParams.set('musculo', params.musculo);
    }

    if (params.page) {
      httpParams = httpParams.set('page', params.page);
    }

    return this.http
      .get<
        ApiSuccessResponse<{
          items: BackendExercicio[];
          total: number;
          page: number;
          page_size: number;
        }>
      >(this.exerciciosUrl, {
        params: httpParams,
      })
      .pipe(
        map(response => ({
          items: response.data.items.map(item => ({
            id: item.id,
            nome: item.nome,
            musculo: item.musculo,
            descricao: item.descricao ?? null,
            youtubeUrl: item.youtubeUrl ?? null,
          })),
          total: response.data.total,
          page: response.data.page,
          pageSize: response.data.page_size,
        })),
      );
  }

  listarMusculos(): Observable<string[]> {
    return this.http
      .get<ApiSuccessResponse<string[]>>(`${this.exerciciosUrl}/musculos`)
      .pipe(map(response => response.data));
  }
}
