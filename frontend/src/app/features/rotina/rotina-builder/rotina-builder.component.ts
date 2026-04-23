import {
  CdkDragDrop,
  copyArrayItem,
  moveItemInArray,
  transferArrayItem,
} from '@angular/cdk/drag-drop';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import {
  Subject,
  combineLatest,
  debounceTime,
  distinctUntilChanged,
  startWith,
  switchMap,
  takeUntil,
  tap,
} from 'rxjs';

import { Exercicio } from '../../../core/models/exercicio.models';
import {
  DiaTreino,
  ExercicioRotina,
  RotinaPayload,
  RotinaResponse,
} from '../../../core/models/rotina.models';
import { AuthService } from '../../../core/services/auth.service';
import { ExerciciosService } from '../../../core/services/exercicios.service';
import { RotinaService } from '../../../core/services/rotina.service';

@Component({
  selector: 'app-rotina-builder',
  templateUrl: './rotina-builder.component.html',
  styleUrls: ['./rotina-builder.component.css'],
})
export class RotinaBuilderComponent implements OnInit, OnDestroy {
  private readonly defaultDayNames = [
    'Segunda',
    'Terça',
    'Quarta',
    'Quinta',
    'Sexta',
    'Sábado',
    'Domingo',
  ];

  readonly rotinaForm = this.formBuilder.nonNullable.group({
    nome: [
      '',
      [Validators.required, Validators.minLength(3), Validators.max(100)],
    ],
  });

  readonly buscaControl = this.formBuilder.nonNullable.control('');
  readonly musculoControl = this.formBuilder.nonNullable.control('');

  dias: DiaTreino[] = this.createDefaultDays();
  exerciciosDisponiveis: ExercicioRotina[] = [];
  musculosDisponiveis: string[] = [];
  rotinasSalvas: RotinaResponse[] = [];
  selectedRoutineId: string | null = null;
  isLoadingExercises = false;
  isSaving = false;
  isExporting = false;

  private nextDayIndex = 0;
  private readonly destroy$ = new Subject<void>();

  constructor(
    private readonly formBuilder: FormBuilder,
    private readonly exerciciosService: ExerciciosService,
    private readonly rotinaService: RotinaService,
    private readonly authService: AuthService,
    private readonly router: Router,
    private readonly toastr: ToastrService,
  ) {}

  ngOnInit(): void {
    this.loadMusculos();
    combineLatest([
      this.buscaControl.valueChanges.pipe(
        startWith(this.buscaControl.value),
        debounceTime(300),
        distinctUntilChanged(),
      ),
      this.musculoControl.valueChanges.pipe(
        startWith(this.musculoControl.value),
        distinctUntilChanged(),
      ),
    ])
      .pipe(
        tap(() => {
          this.isLoadingExercises = true;
        }),
        switchMap(([busca, musculo]) =>
          this.exerciciosService.listar({ busca, musculo, page: 1 }),
        ),
        takeUntil(this.destroy$),
      )
      .subscribe({
        next: response => {
          this.exerciciosDisponiveis = response.items.map(item =>
            this.toRoutineExercise(item),
          );
          this.isLoadingExercises = false;
        },
        error: (_error: HttpErrorResponse) => {
          this.isLoadingExercises = false;
        },
      });

    this.loadRoutines();
  }

  private loadMusculos(): void {
    this.exerciciosService.listarMusculos().subscribe({
      next: musculos => {
        this.musculosDisponiveis = musculos;
        if (musculos.length > 0 && !this.musculoControl.value) {
          this.musculoControl.setValue(musculos[0]);
        }
      },
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  get connectedDropLists(): string[] {
    return [
      'biblioteca-exercicios',
      ...this.dias.map(dia => this.dropListId(dia.id)),
    ];
  }

  dropListId(diaId: string): string {
    return `drop-${diaId}`;
  }

  onDrop(event: CdkDragDrop<ExercicioRotina[]>): void {
    if (event.previousContainer === event.container) {
      moveItemInArray(
        event.container.data,
        event.previousIndex,
        event.currentIndex,
      );
      return;
    }

    if (event.previousContainer.id === 'biblioteca-exercicios') {
      copyArrayItem(
        event.previousContainer.data,
        event.container.data,
        event.previousIndex,
        event.currentIndex,
      );
      return;
    }

    transferArrayItem(
      event.previousContainer.data,
      event.container.data,
      event.previousIndex,
      event.currentIndex,
    );
  }

  addExerciseToNextAvailableDay(exercicio: Exercicio): void {
    const MAX_EXERCISES_PER_DAY = 10;

    // Busca o primeiro dia que ainda tem espaço disponível (menos de 10 exercícios)
    const targetDayIndex = this.dias.findIndex(
      dia => dia.exercicios.length < MAX_EXERCISES_PER_DAY,
    );

    if (targetDayIndex === -1) {
      this.toastr.warning('Todos os dias já atingiram o limite de exercícios.');
      return;
    }

    // Atualiza o nextDayIndex para o dia encontrado
    this.nextDayIndex = targetDayIndex;
    const targetDay = this.dias[this.nextDayIndex];

    targetDay.exercicios.push(this.toRoutineExercise(exercicio));

    this.toastr.success(`Exercício adicionado ao dia: ${targetDay.nome}.`);
  }

  removeExercise(payload: { diaId: string; uid?: string }): void {
    const dia = this.dias.find(item => item.id === payload.diaId);

    if (!dia) {
      return;
    }

    dia.exercicios = dia.exercicios.filter(
      exercicio => exercicio.uid !== payload.uid,
    );
    this.toastr.success('Exercicio removido do dia.');
  }

  salvarRotina(): void {
    if (this.rotinaForm.invalid || this.isSaving) {
      this.rotinaForm.markAllAsTouched();
      return;
    }

    const payload = this.buildPayload();
    this.isSaving = true;

    const request$ = this.selectedRoutineId
      ? this.rotinaService.atualizar(this.selectedRoutineId, payload)
      : this.rotinaService.criar(payload);

    request$.subscribe({
      next: response => {
        this.selectedRoutineId = response.id;
        this.toastr.success('Rotina salva com sucesso.');
        this.loadRoutines();
      },
      error: (_error: HttpErrorResponse) => {
        this.isSaving = false;
      },
      complete: () => {
        this.isSaving = false;
      },
    });
  }

  carregarRotina(idAsString: string): void {
    const id = idAsString.trim();

    if (!id) {
      this.selectedRoutineId = null;
      return;
    }

    this.rotinaService.buscarPorId(id).subscribe({
      next: rotina => {
        this.selectedRoutineId = rotina.id;
        this.rotinaForm.patchValue({
          nome: rotina.nome,
        });
        this.dias = rotina.dias.map(dia => ({
          ...dia,
          exercicios: dia.exercicios.map(exercicio => ({
            ...exercicio,
            uid: crypto.randomUUID(),
            series: exercicio.series ?? 4,
            repeticoes: exercicio.repeticoes ?? 12,
          })),
        }));
        this.nextDayIndex = this.dias.filter(
          dia => dia.exercicios.length > 0,
        ).length;
        this.toastr.success('Rotina carregada.');
      },
      error: (_error: HttpErrorResponse) => {},
    });
  }

  excluirRotina(): void {
    if (!this.selectedRoutineId) {
      this.toastr.error('Selecione uma rotina salva antes de excluir.');
      return;
    }

    this.rotinaService.deletar(this.selectedRoutineId).subscribe({
      next: () => {
        this.toastr.success('Rotina excluida com sucesso.');
        this.selectedRoutineId = null;
        this.resetBuilder();
        this.loadRoutines();
      },
      error: (_error: HttpErrorResponse) => {},
    });
  }

  exportarPlanilha(): void {
    if (!this.selectedRoutineId || this.isExporting) {
      this.toastr.error('Salve a rotina antes de exportar a planilha.');
      return;
    }

    this.isExporting = true;

    this.rotinaService.gerarPlanilha(this.selectedRoutineId).subscribe({
      next: blob => {
        const objectUrl = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = objectUrl;
        anchor.download = `${this.rotinaForm.getRawValue().nome || 'rotina'}.xlsx`;
        anchor.click();
        URL.revokeObjectURL(objectUrl);
        this.toastr.success('Planilha exportada com sucesso.');
      },
      error: (_error: HttpErrorResponse) => {
        this.isExporting = false;
      },
      complete: () => {
        this.isExporting = false;
      },
    });
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  trackByDia(_: number, dia: DiaTreino): string {
    return dia.id;
  }

  private buildPayload(): RotinaPayload {
    const formValue = this.rotinaForm.getRawValue();

    return {
      nome: formValue.nome,
      dias: this.dias,
    };
  }

  private loadRoutines(): void {
    this.rotinaService
      .listar()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: rotinas => {
          this.rotinasSalvas = rotinas;
          this.isSaving = false;
        },
        error: (_error: HttpErrorResponse) => {},
      });
  }

  private resetBuilder(): void {
    this.rotinaForm.reset({
      nome: '',
    });
    this.dias = this.createDefaultDays();
    this.nextDayIndex = 0;
  }

  private toRoutineExercise(exercicio: Exercicio): ExercicioRotina {
    return {
      ...exercicio,
      uid: crypto.randomUUID(),
      series: 4,
      repeticoes: 12,
    };
  }

  private createDefaultDays(): DiaTreino[] {
    return this.defaultDayNames.map((nome, index) => ({
      id: `dia-${index + 1}`,
      nome,
      exercicios: [],
    }));
  }
}
