import assert from "node:assert/strict";
import test from "node:test";

import {
  ConflictoBoxError,
  ConflictoProfesionalError,
  verificarDisponibilidad,
} from "../../src/domain/disponibilidad.ts";
import { crearTurno, type Turno } from "../../src/domain/turnos.ts";

const turno = (id: string, profesionalId: string, boxId: string, inicio: string, fin: string): Turno =>
  crearTurno({
    id,
    pacienteId: `paciente-demo-${id}`,
    profesionalId,
    boxId,
    prestacionId: "prestacion-demo-001",
    inicio: new Date(inicio),
    fin: new Date(fin),
  });

const existente = turno(
  "existente",
  "profesional-demo-001",
  "box-demo-001",
  "2030-01-10T09:00:00.000Z",
  "2030-01-10T09:30:00.000Z",
);

test("informa conflicto tipado por profesional aunque el box sea distinto", () => {
  const candidato = turno(
    "candidato-profesional",
    "profesional-demo-001",
    "box-demo-002",
    "2030-01-10T09:15:00.000Z",
    "2030-01-10T09:45:00.000Z",
  );

  assert.throws(() => verificarDisponibilidad(candidato, [existente]), ConflictoProfesionalError);
});

test("informa conflicto tipado por box aunque el profesional sea distinto", () => {
  const candidato = turno(
    "candidato-box",
    "profesional-demo-002",
    "box-demo-001",
    "2030-01-10T09:15:00.000Z",
    "2030-01-10T09:45:00.000Z",
  );

  assert.throws(() => verificarDisponibilidad(candidato, [existente]), ConflictoBoxError);
});
