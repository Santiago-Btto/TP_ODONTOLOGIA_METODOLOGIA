import assert from "node:assert/strict";
import test from "node:test";

import { RepositorioTurnosEnMemoria } from "../../src/infrastructure/in-memory/repositorio-turnos-en-memoria.ts";
import { crearTurno } from "../../src/domain/turnos.ts";

const crearTurnoDemo = (id: string, profesionalId: string, boxId: string) => crearTurno({
  id,
  pacienteId: `paciente-demo-${id}`,
  profesionalId,
  boxId,
  prestacionId: "prestacion-demo-001",
  inicio: new Date("2030-01-10T09:00:00.000Z"),
  fin: new Date("2030-01-10T09:30:00.000Z"),
});

test("consulta sólo las reservas activas de un profesional o box", () => {
  const repositorio = new RepositorioTurnosEnMemoria();
  const compartido = crearTurnoDemo("turno-demo-001", "profesional-demo-001", "box-demo-001");
  repositorio.guardar(compartido);
  repositorio.guardar(crearTurnoDemo("turno-demo-002", "profesional-demo-002", "box-demo-002"));

  assert.deepEqual(repositorio.buscarActivosPorProfesional("profesional-demo-001"), [compartido]);
  assert.deepEqual(repositorio.buscarActivosPorBox("box-demo-001"), [compartido]);
});

test("mantiene recursos no compartidos fuera de las consultas", () => {
  const repositorio = new RepositorioTurnosEnMemoria();
  repositorio.guardar(crearTurnoDemo("turno-demo-003", "profesional-demo-003", "box-demo-003"));

  assert.deepEqual(repositorio.buscarActivosPorProfesional("profesional-demo-004"), []);
  assert.deepEqual(repositorio.buscarActivosPorBox("box-demo-004"), []);
});
