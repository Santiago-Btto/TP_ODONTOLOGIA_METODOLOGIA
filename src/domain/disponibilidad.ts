export interface Intervalo {
  readonly inicio: Date;
  readonly fin: Date;
}

export class ConflictoProfesionalError extends Error {
  public constructor() {
    super("El profesional ya tiene un turno activo en ese intervalo.");
    this.name = "ConflictoProfesionalError";
  }
}

export class ConflictoBoxError extends Error {
  public constructor() {
    super("El box ya tiene un turno activo en ese intervalo.");
    this.name = "ConflictoBoxError";
  }
}

export function intervalosSeSolapan(candidato: Intervalo, existente: Intervalo): boolean {
  return candidato.inicio < existente.fin && existente.inicio < candidato.fin;
}

interface TurnoReservable extends Intervalo {
  readonly profesionalId: string;
  readonly boxId: string;
}

export function verificarDisponibilidad(
  candidato: TurnoReservable,
  turnosActivos: readonly TurnoReservable[],
): void {
  if (turnosActivos.some((turno) =>
    turno.profesionalId === candidato.profesionalId && intervalosSeSolapan(candidato, turno))) {
    throw new ConflictoProfesionalError();
  }
  if (turnosActivos.some((turno) =>
    turno.boxId === candidato.boxId && intervalosSeSolapan(candidato, turno))) {
    throw new ConflictoBoxError();
  }
}
