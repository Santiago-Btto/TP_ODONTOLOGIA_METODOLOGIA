import assert from "node:assert/strict";
import test from "node:test";

import { intervalosSeSolapan } from "../../src/domain/disponibilidad.ts";

const intervalo = (inicio: string, fin: string) => ({ inicio: new Date(inicio), fin: new Date(fin) });

test("detecta un solapamiento parcial", () => {
  assert.equal(
    intervalosSeSolapan(
      intervalo("2030-01-10T09:00:00.000Z", "2030-01-10T09:30:00.000Z"),
      intervalo("2030-01-10T09:15:00.000Z", "2030-01-10T09:45:00.000Z"),
    ),
    true,
  );
});

test("detecta un intervalo candidato contenido por uno existente", () => {
  assert.equal(
    intervalosSeSolapan(
      intervalo("2030-01-10T09:10:00.000Z", "2030-01-10T09:20:00.000Z"),
      intervalo("2030-01-10T09:00:00.000Z", "2030-01-10T09:30:00.000Z"),
    ),
    true,
  );
});

test("admite intervalos contiguos en un borde", () => {
  assert.equal(
    intervalosSeSolapan(
      intervalo("2030-01-10T09:30:00.000Z", "2030-01-10T10:00:00.000Z"),
      intervalo("2030-01-10T09:00:00.000Z", "2030-01-10T09:30:00.000Z"),
    ),
    false,
  );
});
