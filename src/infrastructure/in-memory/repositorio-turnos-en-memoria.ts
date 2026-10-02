import type { RepositorioTurnos } from "../../application/puertos.ts";
import type { Turno } from "../../domain/turnos.ts";

export class RepositorioTurnosEnMemoria implements RepositorioTurnos {
  private readonly turnos: Turno[] = [];

  public buscarActivosPorProfesional(profesionalId: string): readonly Turno[] {
    return this.turnos.filter((turno) => turno.profesionalId === profesionalId);
  }

  public buscarActivosPorBox(boxId: string): readonly Turno[] {
    return this.turnos.filter((turno) => turno.boxId === boxId);
  }

  public guardar(turno: Turno): void {
    this.turnos.push(turno);
  }

  public todos(): readonly Turno[] {
    return [...this.turnos];
  }
}
