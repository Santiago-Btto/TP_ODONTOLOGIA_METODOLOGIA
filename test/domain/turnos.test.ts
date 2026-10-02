import assert from "node:assert/strict";
import test from "node:test";

import {
  DuracionInvalidaError,
  IntervaloInvalidoError,
  crearPrestacion,
  crearTurno,
} from "../../src/domain/turnos.ts";

const inicio = new Date("2030-01-10T09:00:00.000Z");
const fin = new Date("2030-01-10T09:30:00.000Z");

test("crea un turno con un intervalo estrictamente positivo", () => {
  const turno = crearTurno({
    id: "turno-demo-001",
    pacienteId: "paciente-demo-001",
    profesionalId: "profesional-demo-001",
    boxId: "box-demo-001",
    prestacionId: "prestacion-demo-001",
    inicio,
    fin,
  });

  assert.equal(turno.inicio.getTime(), inicio.getTime());
  assert.equal(turno.fin.getTime(), fin.getTime());
});

test("rechaza un intervalo cuyo fin coincide con el inicio", () => {
  assert.throws(
    () => crearTurno({
      id: "turno-demo-002",
      pacienteId: "paciente-demo-001",
      profesionalId: "profesional-demo-001",
      boxId: "box-demo-001",
      prestacionId: "prestacion-demo-001",
      inicio,
      fin: inicio,
    }),
    IntervaloInvalidoError,
  );
});

test("rechaza un intervalo cuyo fin es anterior al inicio", () => {
  assert.throws(
    () => crearTurno({
      id: "turno-demo-003",
      pacienteId: "paciente-demo-001",
      profesionalId: "profesional-demo-001",
      boxId: "box-demo-001",
      prestacionId: "prestacion-demo-001",
      inicio: fin,
      fin: inicio,
    }),
    IntervaloInvalidoError,
  );
});

test("rechaza una prestación de duración cero", () => {
  assert.throws(
    () => crearPrestacion({
      id: "prestacion-demo-cero",
      nombre: "Prestación Demo Cero",
      duracionMinutos: 0,
    }),
    DuracionInvalidaError,
  );
});

test("rechaza una prestación de duración negativa", () => {
  assert.throws(
    () => crearPrestacion({
      id: "prestacion-demo-negativa",
      nombre: "Prestación Demo Negativa",
      duracionMinutos: -15,
    }),
    DuracionInvalidaError,
  );
});
