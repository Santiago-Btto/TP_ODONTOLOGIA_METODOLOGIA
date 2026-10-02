import {
  calcularFin,
  crearPrestacion,
  crearTurno,
  type Box,
  type Paciente,
  type Prestacion,
  type Profesional,
  type Turno,
} from "../../domain/turnos.ts";
import { verificarDisponibilidad } from "../../domain/disponibilidad.ts";
import type { RepositorioHistoriales, RepositorioTurnos } from "../puertos.ts";

export interface CrearTurnoInput {
  readonly id: string;
  readonly paciente: Paciente;
  readonly profesional: Profesional;
  readonly box: Box;
  readonly prestacion: Prestacion;
  readonly inicio: Date;
  readonly fin?: Date;
  readonly ocurridoEn: Date;
}

export interface DependenciasCrearTurno {
  readonly turnos: RepositorioTurnos;
  readonly historiales: RepositorioHistoriales;
}

export class CrearTurno {
  private readonly dependencias: DependenciasCrearTurno;

  public constructor(dependencias: DependenciasCrearTurno) {
    this.dependencias = dependencias;
  }

  public ejecutar(input: CrearTurnoInput): Turno {
    const prestacion = crearPrestacion(input.prestacion);
    const candidato = crearTurno({
      id: input.id,
      pacienteId: input.paciente.id,
      profesionalId: input.profesional.id,
      boxId: input.box.id,
      prestacionId: prestacion.id,
      inicio: input.inicio,
      fin: input.fin ?? calcularFin(input.inicio, prestacion),
    });
    const existentes = [
      ...this.dependencias.turnos.buscarActivosPorProfesional(candidato.profesionalId),
      ...this.dependencias.turnos.buscarActivosPorBox(candidato.boxId),
    ];

    verificarDisponibilidad(candidato, existentes);
    this.dependencias.turnos.guardar(candidato);
    this.dependencias.historiales.guardar({
      id: `historial-${candidato.id}-creado`,
      turnoId: candidato.id,
      tipo: "creado",
      ocurridoEn: input.ocurridoEn,
    });
    return candidato;
  }
}
