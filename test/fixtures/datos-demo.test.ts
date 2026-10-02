import assert from "node:assert/strict";
import test from "node:test";

import {
  boxDemo,
  pacienteDemo,
  prestacionDemo,
  profesionalDemo,
} from "./datos-demo.ts";

test("las fixtures identifican explícitamente a la paciente ficticia", () => {
  assert.match(pacienteDemo.nombreMostrado, /^Paciente Demo Ficticia /);
  assert.match(pacienteDemo.id, /^paciente-demo-/);
});

test("las fixtures de recursos y prestación son deterministas y ficticias", () => {
  assert.deepEqual(profesionalDemo, {
    id: "profesional-demo-001",
    nombreMostrado: "Profesional Demo Ficticio 001",
    activo: true,
  });
  assert.deepEqual(boxDemo, { id: "box-demo-001", nombre: "Box Demo 001", activo: true });
  assert.equal(prestacionDemo.duracionMinutos, 30);
});
