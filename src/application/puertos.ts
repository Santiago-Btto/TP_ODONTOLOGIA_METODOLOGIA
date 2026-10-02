import type { HistorialDeCambio, Turno } from "../domain/turnos.ts";

export interface RepositorioTurnos {
  buscarActivosPorProfesional(profesionalId: string): readonly Turno[];
  buscarActivosPorBox(boxId: string): readonly Turno[];
  guardar(turno: Turno): void;
  todos(): readonly Turno[];
}

export interface RepositorioHistoriales {
  guardar(historial: HistorialDeCambio): void;
  todos(): readonly HistorialDeCambio[];
}
