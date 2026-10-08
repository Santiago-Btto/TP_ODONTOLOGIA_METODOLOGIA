"""Escenarios de `Impedir solapamientos en la persistencia` contra PostgreSQL real."""

from datetime import UTC, datetime

import pytest
from sqlalchemy import func, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.application.crear_turno import CrearTurno, SolicitudCrearTurno
from app.domain.disponibilidad import ConflictoBoxError, ConflictoProfesionalError
from app.domain.turnos import Turno
from app.infrastructure.modelos import HistorialModelo, TurnoModelo
from app.infrastructure.unidad_de_trabajo import UnidadDeTrabajoSQLAlchemy

AHORA = datetime(2030, 1, 1, 8, 0, tzinfo=UTC)


def hora(hh: int, mm: int) -> datetime:
    return datetime(2030, 1, 10, hh, mm, tzinfo=UTC)


def fila(id_: str, inicio: datetime, fin: datetime, profesional: str = "profesional-demo-001",
         box: str = "box-demo-001") -> dict[str, object]:
    return {
        "id": id_,
        "paciente_id": "paciente-demo-001",
        "profesional_id": profesional,
        "box_id": box,
        "prestacion_id": "prestacion-demo-001",
        "inicio": inicio,
        "fin": fin,
        "estado": "programado",
    }


def cantidad(fabrica: sessionmaker[Session], modelo: type[TurnoModelo] | type[HistorialModelo]) -> int:
    with fabrica() as sesion:
        return sesion.scalar(select(func.count()).select_from(modelo)) or 0


def insertar_directo(fabrica: sessionmaker[Session], valores: dict[str, object]) -> None:
    with fabrica() as sesion:
        sesion.execute(insert(TurnoModelo).values(**valores))
        sesion.commit()


# Escenario: Escritura solapada que elude la aplicación
def test_la_base_rechaza_un_solapamiento_de_profesional_insertado_directamente(fabrica: sessionmaker[Session]) -> None:
    insertar_directo(fabrica, fila("turno-demo-a", hora(9, 0), hora(9, 30), box="box-demo-001"))

    with pytest.raises(IntegrityError, match="turnos_sin_solapamiento_profesional"):
        insertar_directo(fabrica, fila("turno-demo-b", hora(9, 15), hora(9, 45), box="box-demo-002"))

    assert cantidad(fabrica, TurnoModelo) == 1


def test_la_base_rechaza_un_solapamiento_de_box_insertado_directamente(fabrica: sessionmaker[Session]) -> None:
    insertar_directo(fabrica, fila("turno-demo-a", hora(9, 0), hora(9, 30), profesional="profesional-demo-001"))

    with pytest.raises(IntegrityError, match="turnos_sin_solapamiento_box"):
        insertar_directo(fabrica, fila("turno-demo-b", hora(9, 15), hora(9, 45), profesional="profesional-demo-002"))

    assert cantidad(fabrica, TurnoModelo) == 1


# Escenario: Escritura contigua directa
def test_la_base_acepta_un_turno_contiguo_insertado_directamente(fabrica: sessionmaker[Session]) -> None:
    insertar_directo(fabrica, fila("turno-demo-a", hora(9, 0), hora(9, 30)))
    insertar_directo(fabrica, fila("turno-demo-b", hora(9, 30), hora(10, 0)))

    assert cantidad(fabrica, TurnoModelo) == 2


def test_la_base_rechaza_un_intervalo_con_fin_no_posterior(fabrica: sessionmaker[Session]) -> None:
    with pytest.raises(IntegrityError, match="turnos_fin_posterior_al_inicio"):
        insertar_directo(fabrica, fila("turno-demo-a", hora(9, 0), hora(9, 0)))


def test_alta_por_caso_de_uso_persiste_turno_e_historial_en_postgresql(fabrica: sessionmaker[Session]) -> None:
    caso = CrearTurno(lambda: UnidadDeTrabajoSQLAlchemy(fabrica), reloj=lambda: AHORA)

    caso.ejecutar(SolicitudCrearTurno("turno-demo-a", "paciente-demo-001", "profesional-demo-001",
                                      "box-demo-001", "prestacion-demo-001", hora(9, 0)))
    caso.ejecutar(SolicitudCrearTurno("turno-demo-b", "paciente-demo-002", "profesional-demo-001",
                                      "box-demo-001", "prestacion-demo-001", hora(9, 30)))
    with pytest.raises(ConflictoBoxError):
        caso.ejecutar(SolicitudCrearTurno("turno-demo-c", "paciente-demo-002", "profesional-demo-002",
                                          "box-demo-001", "prestacion-demo-001", hora(9, 45)))

    assert cantidad(fabrica, TurnoModelo) == 2
    assert cantidad(fabrica, HistorialModelo) == 2


@pytest.mark.parametrize(
    ("profesional", "box", "error"),
    [
        ("profesional-demo-001", "box-demo-002", ConflictoProfesionalError),
        ("profesional-demo-002", "box-demo-001", ConflictoBoxError),
    ],
)
def test_carrera_entre_dos_altas_se_traduce_a_conflicto_sin_estado_parcial(
    fabrica: sessionmaker[Session], profesional: str, box: str, error: type[Exception]
) -> None:
    """Simula dos requests: ambas validan sin ver a la otra y la segunda llega tarde al commit."""
    with UnidadDeTrabajoSQLAlchemy(fabrica) as tardia:
        assert tardia.turnos.activos_que_se_solapan(profesional, box, hora(9, 0), hora(9, 30)) == []

        insertar_directo(fabrica, fila("turno-demo-primera", hora(9, 0), hora(9, 30)))

        with pytest.raises(error):
            tardia.turnos.agregar(Turno("turno-demo-tardia", "paciente-demo-002", profesional, box,
                                        "prestacion-demo-001", hora(9, 0), hora(9, 30)))
            tardia.commit()

    assert cantidad(fabrica, TurnoModelo) == 1
    assert cantidad(fabrica, HistorialModelo) == 0
