import {
  crearPrestacion,
  type Box,
  type Paciente,
  type Profesional,
} from "../../src/domain/turnos.ts";

export const pacienteDemo: Paciente = {
  id: "paciente-demo-001",
  nombreMostrado: "Paciente Demo Ficticia 001",
};

export const profesionalDemo: Profesional = {
  id: "profesional-demo-001",
  nombreMostrado: "Profesional Demo Ficticio 001",
  activo: true,
};

export const boxDemo: Box = {
  id: "box-demo-001",
  nombre: "Box Demo 001",
  activo: true,
};

export const prestacionDemo = crearPrestacion({
  id: "prestacion-demo-001",
  nombre: "Prestación Demo 30 minutos",
  duracionMinutos: 30,
});
