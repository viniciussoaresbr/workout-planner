import { DOCUMENT, Injectable, inject } from '@angular/core';

/** Dispara downloads de arquivos gerados em memória. */
@Injectable({ providedIn: 'root' })
export class FileDownloader {
  private readonly document = inject(DOCUMENT);

  download(blob: Blob, filename: string): void {
    const url = URL.createObjectURL(blob);
    const anchor = this.document.createElement('a');
    anchor.href = url;
    anchor.download = filename;
    anchor.rel = 'noopener';
    this.document.body.append(anchor);
    anchor.click();
    anchor.remove();
    // Revogar no mesmo tick pode cancelar o download em alguns navegadores.
    setTimeout(() => URL.revokeObjectURL(url), 1_000);
  }
}
