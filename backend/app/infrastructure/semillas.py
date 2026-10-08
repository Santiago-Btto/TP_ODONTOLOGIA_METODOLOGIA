"""Carga datos manifiestamente ficticios para probar la API a mano: `python -m app.infrastructure.semillas`."""

from sqlalchemy.orm import Session

from app.infrastructure.db import crear_esquema, crear_fabrica_de_sesiones, crear_motor, url_de_base
from app.infrastructure.modelos import BoxModelo, PacienteModelo, PrestacionModelo, ProfesionalModelo


def cargar_semillas(sesion: Session) -> None:
    for fila in (
        PacienteModelo(id="paciente-demo-001", nombre_mostrado="Paciente Demo Ficticia 001"),
        PacienteModelo(id="paciente-demo-002", nombre_mostrado="Paciente Demo Ficticio 002"),
        ProfesionalModelo(id="profesional-demo-001", nombre_mostrado="Profesional Demo Ficticio 001"),
        ProfesionalModelo(id="profesional-demo-002", nombre_mostrado="Profesional Demo Ficticio 002"),
        BoxModelo(id="box-demo-001", nombre="Box Demo 001"),
        BoxModelo(id="box-demo-002", nombre="Box Demo 002"),
        PrestacionModelo(id="prestacion-demo-001", nombre="Prestación Demo 30 minutos", duracion_minutos=30),
    ):
        sesion.merge(fila)
    sesion.commit()


if __name__ == "__main__":
    motor = crear_motor(url_de_base())
    crear_esquema(motor)
    with crear_fabrica_de_sesiones(motor)() as sesion:
        cargar_semillas(sesion)
    print("Semillas ficticias cargadas.")
