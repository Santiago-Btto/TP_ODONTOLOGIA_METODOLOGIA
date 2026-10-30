"""Escenarios de lectura SQLAlchemy para `consulta-de-agenda` contra PostgreSQL real."""

from datetime import UTC, datetime

from sqlalchemy import insert
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.modelos import TurnoModelo
from app.infrastructure.unidad_de_trabajo import LectorAgendaSQLAlchemy


def hora(hh: int, mm: int, dia: int = 10) -> datetime:
    return datetime(2030, 1, dia, hh, mm, tzinfo=UTC)


def fila(
    id_: str,
    inicio: datetime,
    fin: datetime,
    profesional: str = "profesional-demo-001",
    box: str = "box-demo-001",
) -> dict[str, object]:
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


def insertar_directo(fabrica: sessionmaker[Session], *valores: dict[str, object]) -> None:
    with fabrica() as sesion:
        for item in valores:
            sesion.execute(insert(TurnoModelo).values(**item))
        sesion.commit()


# Escenario: Turnos contenidos en una agenda diaria
def test_lector_devuelve_turnos_contenidos_en_agenda_diaria(fabrica: sessionmaker[Session]) -> None:
    insertar_directo(
        fabrica,
        fila("turno-demo-1", hora(9, 0), hora(9, 30)),
        fila("turno-demo-2", hora(11, 0), hora(11, 30)),
    )
    lector = LectorAgendaSQLAlchemy(fabrica)

    turnos = lector.en_rango(hora(8, 0), hora(12, 0))

    assert [t.id for t in turnos] == ["turno-demo-1", "turno-demo-2"]


# Escenario: Turno que empieza antes del rango
def test_lector_devuelve_turno_que_empieza_antes_del_rango(fabrica: sessionmaker[Session]) -> None:
    insertar_directo(fabrica, fila("turno-demo-antes", hora(8, 30), hora(9, 15)))
    lector = LectorAgendaSQLAlchemy(fabrica)

    turnos = lector.en_rango(hora(9, 0), hora(10, 0))

    assert [t.id for t in turnos] == ["turno-demo-antes"]


# Escenario: Turno que termina después del rango
def test_lector_devuelve_turno_que_termina_despues_del_rango(fabrica: sessionmaker[Session]) -> None:
    insertar_directo(fabrica, fila("turno-demo-despues", hora(9, 45), hora(10, 15)))
    lector = LectorAgendaSQLAlchemy(fabrica)

    turnos = lector.en_rango(hora(9, 0), hora(10, 0))

    assert [t.id for t in turnos] == ["turno-demo-despues"]


# Escenario: Turno que cubre el rango completo
def test_lector_devuelve_una_sola_vez_el_turno_que_cubre_el_rango_completo(
    fabrica: sessionmaker[Session],
) -> None:
    insertar_directo(fabrica, fila("turno-demo-cubre", hora(8, 30), hora(10, 30)))
    lector = LectorAgendaSQLAlchemy(fabrica)

    turnos = lector.en_rango(hora(9, 0), hora(10, 0))

    assert [t.id for t in turnos] == ["turno-demo-cubre"]


# Escenario: Turno que termina justo al comenzar el rango
def test_lector_excluye_turno_que_termina_justo_al_comenzar_el_rango(
    fabrica: sessionmaker[Session],
) -> None:
    insertar_directo(fabrica, fila("turno-demo-borde-izq", hora(8, 30), hora(9, 0)))
    lector = LectorAgendaSQLAlchemy(fabrica)

    assert lector.en_rango(hora(9, 0), hora(10, 0)) == []


# Escenario: Turno que empieza justo al terminar el rango
def test_lector_excluye_turno_que_empieza_justo_al_terminar_el_rango(
    fabrica: sessionmaker[Session],
) -> None:
    insertar_directo(fabrica, fila("turno-demo-borde-der", hora(10, 0), hora(10, 30)))
    lector = LectorAgendaSQLAlchemy(fabrica)

    assert lector.en_rango(hora(9, 0), hora(10, 0)) == []


# Escenario: Rango sin coincidencias
def test_lector_devuelve_lista_vacia_cuando_el_rango_no_tiene_turnos(
    fabrica: sessionmaker[Session],
) -> None:
    insertar_directo(fabrica, fila("turno-demo-lejos", hora(14, 0), hora(14, 30)))
    lector = LectorAgendaSQLAlchemy(fabrica)

    assert lector.en_rango(hora(9, 0), hora(10, 0)) == []


# Escenario: Identificador sin turnos coincidentes
def test_lector_devuelve_lista_vacia_para_identificador_de_texto_sin_coincidencias(
    fabrica: sessionmaker[Session],
) -> None:
    insertar_directo(fabrica, fila("turno-demo-1", hora(9, 0), hora(9, 30)))
    lector = LectorAgendaSQLAlchemy(fabrica)

    assert lector.en_rango(hora(8, 0), hora(10, 0), profesional_id="profesional-inexistente-demo") == []
    assert lector.en_rango(hora(8, 0), hora(10, 0), box_id="box-inexistente-demo") == []


# Escenario: Agenda semanal de un profesional
def test_lector_filtra_agenda_semanal_por_profesional(fabrica: sessionmaker[Session]) -> None:
    insertar_directo(
        fabrica,
        fila("turno-demo-p1-lun", hora(9, 0, dia=7), hora(9, 30, dia=7), profesional="profesional-demo-001"),
        fila("turno-demo-p2-mie", hora(10, 0, dia=9), hora(10, 30, dia=9), profesional="profesional-demo-002"),
        fila("turno-demo-p1-vie", hora(11, 0, dia=11), hora(11, 30, dia=11), profesional="profesional-demo-001"),
    )
    lector = LectorAgendaSQLAlchemy(fabrica)

    turnos = lector.en_rango(hora(0, 0, dia=7), hora(0, 0, dia=14), profesional_id="profesional-demo-001")

    assert [t.id for t in turnos] == ["turno-demo-p1-lun", "turno-demo-p1-vie"]


# Escenario: Agenda semanal de un box
def test_lector_filtra_agenda_semanal_por_box(fabrica: sessionmaker[Session]) -> None:
    insertar_directo(
        fabrica,
        fila("turno-demo-b1-lun", hora(9, 0, dia=7), hora(9, 30, dia=7), box="box-demo-001"),
        fila("turno-demo-b2-mie", hora(10, 0, dia=9), hora(10, 30, dia=9), box="box-demo-002"),
        fila("turno-demo-b1-vie", hora(11, 0, dia=11), hora(11, 30, dia=11), box="box-demo-001"),
    )
    lector = LectorAgendaSQLAlchemy(fabrica)

    turnos = lector.en_rango(hora(0, 0, dia=7), hora(0, 0, dia=14), box_id="box-demo-001")

    assert [t.id for t in turnos] == ["turno-demo-b1-lun", "turno-demo-b1-vie"]


# Escenario: Filtros combinados
def test_lector_filtra_con_conjuncion_and_por_profesional_y_box(fabrica: sessionmaker[Session]) -> None:
    insertar_directo(
        fabrica,
        fila("turno-demo-p1-b1", hora(9, 0), hora(9, 30), profesional="profesional-demo-001", box="box-demo-001"),
        fila("turno-demo-p1-b2", hora(10, 0), hora(10, 30), profesional="profesional-demo-001", box="box-demo-002"),
        fila("turno-demo-p2-b1", hora(11, 0), hora(11, 30), profesional="profesional-demo-002", box="box-demo-001"),
    )
    lector = LectorAgendaSQLAlchemy(fabrica)

    turnos = lector.en_rango(
        hora(8, 0),
        hora(12, 0),
        profesional_id="profesional-demo-001",
        box_id="box-demo-001",
    )

    assert [t.id for t in turnos] == ["turno-demo-p1-b1"]


# Escenario: Resultado ordenado y recursos incluidos
def test_lector_devuelve_resultados_ordenados_por_inicio_ascendente_con_sus_recursos(
    fabrica: sessionmaker[Session],
) -> None:
    insertar_directo(
        fabrica,
        fila("turno-demo-tarde", hora(11, 0), hora(11, 30), profesional="profesional-demo-002", box="box-demo-002"),
        fila("turno-demo-temprano", hora(8, 30), hora(9, 0), profesional="profesional-demo-001", box="box-demo-001"),
        fila("turno-demo-medio", hora(9, 30), hora(10, 0), profesional="profesional-demo-001", box="box-demo-002"),
    )
    lector = LectorAgendaSQLAlchemy(fabrica)

    turnos = lector.en_rango(hora(8, 0), hora(12, 0))

    assert [t.id for t in turnos] == ["turno-demo-temprano", "turno-demo-medio", "turno-demo-tarde"]
    assert [(t.profesional_id, t.box_id) for t in turnos] == [
        ("profesional-demo-001", "box-demo-001"),
        ("profesional-demo-001", "box-demo-002"),
        ("profesional-demo-002", "box-demo-002"),
    ]
