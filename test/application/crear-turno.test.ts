import assert from "node:assert/strict";
import test from "node:test";

import { CrearTurno } from "../../src/application/use-cases/crear-turno.ts";
import { ConflictoBoxError, ConflictoProfesionalError } from "../../src/domain/disponibilidad.ts";
import { crearTurno, DuracionInvalidaError, IntervaloInvalidoError, type Prestacion } from "../../src/domain/turnos.ts";
import { RepositorioHistorialesEnMemoria } from "../../src/infrastructure/in-memory/repositorio-historiales-en-memoria.ts";
import { RepositorioTurnosEnMemoria } from "../../src/infrastructure/in-memory/repositorio-turnos-en-memoria.ts";
import { boxDemo, pacienteDemo, prestacionDemo, profesionalDemo } from "../fixtures/datos-demo.ts";

const crearCaso = () => {
  const turnos = new RepositorioTurnosEnMemoria();
  const historiales = new RepositorioHistorialesEnMemoria();
  return { turnos, historiales, caso: new CrearTurno({ turnos, historiales }) };
};

const solicitudValida = {
  id: "turno-demo-alta-001",
  paciente: pacienteDemo,
  profesional: profesionalDemo,
  box: boxDemo,
  prestacion: prestacionDemo,
  inicio: new Date("2030-01-10T09:00:00.000Z"),
  ocurridoEn: new Date("2030-01-01T08:00:00.000Z"),
};

test("persiste un turno válido y un único historial creado", () => {
  const { caso, turnos, historiales } = crearCaso();

  const creado = caso.ejecutar(solicitudValida);

  assert.equal(creado.id, solicitudValida.id);
  assert.equal(creado.fin.toISOString(), "2030-01-10T09:30:00.000Z");
  assert.deepEqual(turnos.todos(), [creado]);
  assert.deepEqual(historiales.todos(), [{
    id: "historial-turno-demo-alta-001-creado",
    turnoId: solicitudValida.id,
    tipo: "creado",
    ocurridoEn: solicitudValida.ocurridoEn,
  }]);
});

test("rechaza un conflicto de profesional sin escribir turno ni historial", () => {
  const { caso, turnos, historiales } = crearCaso();
  const existente = crearTurno({
    id: "turno-demo-existente-profesional",
    pacienteId: "paciente-demo-002",
    profesionalId: profesionalDemo.id,
    boxId: "box-demo-otro",
    prestacionId: prestacionDemo.id,
    inicio: new Date("2030-01-10T09:00:00.000Z"),
    fin: new Date("2030-01-10T09:30:00.000Z"),
  });
  turnos.guardar(existente);

  assert.throws(() => caso.ejecutar(solicitudValida), ConflictoProfesionalError);
  assert.deepEqual(turnos.todos(), [existente]);
  assert.deepEqual(historiales.todos(), []);
});

test("rechaza un conflicto de box sin escribir turno ni historial", () => {
  const { caso, turnos, historiales } = crearCaso();
  const existente = crearTurno({
    id: "turno-demo-existente-box",
    pacienteId: "paciente-demo-003",
    profesionalId: "profesional-demo-otro",
    boxId: boxDemo.id,
    prestacionId: prestacionDemo.id,
    inicio: new Date("2030-01-10T09:00:00.000Z"),
    fin: new Date("2030-01-10T09:30:00.000Z"),
  });
  turnos.guardar(existente);

  assert.throws(() => caso.ejecutar(solicitudValida), ConflictoBoxError);
  assert.deepEqual(turnos.todos(), [existente]);
  assert.deepEqual(historiales.todos(), []);
});

test("acepta una reserva contigua que comparte profesional y box", () => {
  const { caso, turnos, historiales } = crearCaso();
  turnos.guardar(crearTurno({
    id: "turno-demo-contiguo-anterior",
    pacienteId: "paciente-demo-004",
    profesionalId: profesionalDemo.id,
    boxId: boxDemo.id,
    prestacionId: prestacionDemo.id,
    inicio: new Date("2030-01-10T08:30:00.000Z"),
    fin: new Date("2030-01-10T09:00:00.000Z"),
  }));

  const creado = caso.ejecutar(solicitudValida);

  assert.equal(turnos.todos().length, 2);
  assert.equal(historiales.todos().length, 1);
  assert.equal(creado.id, solicitudValida.id);
});

test("rechaza un intervalo inválido sin dejar estado parcial", () => {
  const { caso, turnos, historiales } = crearCaso();
  const inicio = new Date("2030-01-10T09:00:00.000Z");

  assert.throws(
    () => caso.ejecutar({ ...solicitudValida, id: "turno-demo-intervalo-invalido", inicio, fin: inicio }),
    IntervaloInvalidoError,
  );
  assert.deepEqual(turnos.todos(), []);
  assert.deepEqual(historiales.todos(), []);
});

test("rechaza una prestación de duración inválida sin dejar estado parcial", () => {
  const { caso, turnos, historiales } = crearCaso();
  const prestacionInvalida: Prestacion = {
    id: "prestacion-demo-invalida",
    nombre: "Prestación Demo Inválida",
    duracionMinutos: -30,
  };

  assert.throws(
    () => caso.ejecutar({ ...solicitudValida, id: "turno-demo-duracion-invalida", prestacion: prestacionInvalida }),
    DuracionInvalidaError,
  );
  assert.deepEqual(turnos.todos(), []);
  assert.deepEqual(historiales.todos(), []);
});
