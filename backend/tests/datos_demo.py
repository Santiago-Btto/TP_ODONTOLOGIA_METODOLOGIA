"""Datos manifiestamente ficticios. Nunca usar datos reales de pacientes."""

from app.domain.turnos import Box, Paciente, Prestacion, Profesional

PACIENTE = Paciente(id="paciente-demo-001", nombre_mostrado="Paciente Demo Ficticia 001")
PROFESIONAL = Profesional(id="profesional-demo-001", nombre_mostrado="Profesional Demo Ficticio 001")
PROFESIONAL_2 = Profesional(id="profesional-demo-002", nombre_mostrado="Profesional Demo Ficticio 002")
BOX = Box(id="box-demo-001", nombre="Box Demo 001")
BOX_2 = Box(id="box-demo-002", nombre="Box Demo 002")
PRESTACION = Prestacion(id="prestacion-demo-001", nombre="Prestación Demo 30 minutos", duracion_minutos=30)
