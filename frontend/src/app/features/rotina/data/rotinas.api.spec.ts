import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { firstValueFrom } from 'rxjs';

import { TEST_API_URL } from '../../../../testing/jwt';
import { API_URL } from '../../../core/api/api.models';
import { ArquivoExportado, FormatoExportacao, RotinasApi } from './rotinas.api';

describe('RotinasApi.exportar', () => {
  let api: RotinasApi;
  let backend: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: API_URL, useValue: TEST_API_URL },
      ],
    });
    api = TestBed.inject(RotinasApi);
    backend = TestBed.inject(HttpTestingController);
  });

  afterEach(() => backend.verify());

  it.each<[FormatoExportacao, string, string]>([
    ['xlsx', 'planilha/export', 'rotina-treino-a.xlsx'],
    ['pdf', 'pdf/export', 'rotina-treino-a.pdf'],
  ])('exporta em %s pelo endpoint %s', async (formato, path, filename) => {
    const resultado: Promise<ArquivoExportado> = firstValueFrom(api.exportar('rotina-1', formato));

    const req = backend.expectOne(`${TEST_API_URL}/${path}`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({ rotina_id: 'rotina-1' });
    expect(req.request.responseType).toBe('blob');
    req.flush(new Blob(['conteudo']), {
      headers: { 'Content-Disposition': `attachment; filename="${filename}"` },
    });

    await expect(resultado).resolves.toEqual({ blob: expect.any(Blob), filename });
  });
});
