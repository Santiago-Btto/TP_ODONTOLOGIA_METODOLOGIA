export type EstadoTurno = "programado";

export interface Paciente {
  readonly id: string;
  readonly nombreMostrado: string;
}

export interface Profesional {
  readonly id: string;
  readonly nombreMostrado: string;
  readonly activo: boolean;
}

export interface Box {
  readonly id: string;
  readonly nombre: string;
  readonly activo: boolean;
}

export interface Prestacion {
  readonly id: string;
  readonly nombre: string;
  readonly duracionMinutos: number;
}

export interface Turno {
  readonly id: string;
  readonly pacienteId: string;
  readonly profesionalId: string;
  readonly boxId: string;
  readonly prestacionId: string;
  readonly inicio: Date;
  readonly fin: Date;
  readonly estado: EstadoTurno;
}

export interface HistorialDeCambio {
  readonly id: string;
  readonly turnoId: string;
  readonly tipo: "creado";
  readonly ocurridoEn: Date;
}

export interface CrearTurnoEnDominioInput {
  readonly id: string;
  readonly pacienteId: string;
  readonly profesionalId: string;
  readonly boxId: string;
  readonly prestacionId: string;
  readonly inicio: Date;
  readonly fin: Date;
}

export interface CrearPrestacionInput {
  readonly id: string;
  readonly nombre: string;
  readonly duracionMinutos: number;
}

export class IntervaloInvalidoError extends Error {
  public constructor() {
    super("El fin del turno debe ser posterior al inicio.");
    this.name = "IntervaloInvalidoError";
  }
}

export class DuracionInvalidaError extends Error {
  public constructor() {
    super("La duración de la prestación debe ser positiva.");
    this.name = "DuracionInvalidaError";
  }
}

export function crearPrestacion(input: CrearPrestacionInput): Prestacion {
  if (input.duracionMinutos <= 0) {
    throw new DuracionInvalidaError();
  }

  return { ...input };
}

export function crearTurno(input: CrearTurnoEnDominioInput): Turno {
  if (input.fin.getTime() <= input.inicio.getTime()) {
    throw new IntervaloInvalidoError();
  }

  return {
    ...input,
    inicio: new Date(input.inicio.getTime()),
    fin: new Date(input.fin.getTime()),
    estado: "programado",
  };
}

export function calcularFin(inicio: Date, prestacion: Prestacion): Date {
  return new Date(inicio.getTime() + prestacion.duracionMinutos * 60_000);
}
