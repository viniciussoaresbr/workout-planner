import { DragDropModule } from '@angular/cdk/drag-drop';
import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { DiaTreinoComponent } from './dia-treino/dia-treino.component';
import { RotinaBuilderComponent } from './rotina-builder/rotina-builder.component';
import { RotinaRoutingModule } from './rotina-routing.module';
import { NgIconsModule } from '@ng-icons/core';
import { HeroTrash, HeroPlus } from '@ng-icons/heroicons/outline';

@NgModule({
  declarations: [RotinaBuilderComponent, DiaTreinoComponent],
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    DragDropModule,
    RotinaRoutingModule,
    NgIconsModule.withIcons({ HeroTrash, HeroPlus }),
  ],
  exports: [RotinaBuilderComponent, DiaTreinoComponent],
})
export class RotinaModule {}
