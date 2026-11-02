"""Ciclo de vida del turno (C-05) contra PostgreSQL real."""

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from datetime import UTC, datetime
from threading import Event

import pytest
from sqlalchemy import insert, select
from sqlalchemy.orm import Session, sessionmaker

from app.application.cambiar_estado_turno import CancelarTurno, ConfirmarTurno, SolicitudCambioDeEstado
from app.application.crear_bloqueo import CrearBloqueo, SolicitudCrearBloqueo
from app.application.crear_turno import CrearTurno, SolicitudCrearTurno
from app.domain.disponibilidad import ConflictoProfesionalError
from app.domain.turnos import EstadoTurno, TransicionInvalidaError
from app.infrastructure.modelos import HistorialModelo, TurnoModelo
from app.infrastructure.unidad_de_trabajo import UnidadDeTrabajoSQLAlchemy

AHORA = datetime(2030, 1, 1, 8, 0, tzinfo=UTC)


def hora(h: int, m: int = 0) -> datetime:
    return datetime(2030, 1, 10, h, m, tzinfo=UTC)


def crear(fabrica: sessionmaker[Session], id_: str = "turno-demo-001", **cambios: str) -> None:
    datos = dict(paciente_id="paciente-demo-001", profesional_id="profesional-demo-001",
                 box_id="box-demo-001", prestacion_id="prestacion-demo-001")
    datos.update(cambios)
    CrearTurno(lambda: UnidadDeTrabajoSQLAlchemy(fabrica), reloj=lambda: AHORA).ejecutar(
        SolicitudCrearTurno(id_, inicio=hora(9), **datos)  # type: ignore[arg-type]
    )


def cancelar(fabrica: sessionmaker[Session], id_: str = "turno-demo-001") -> None:
    CancelarTurno(lambda: UnidadDeTrabajoSQLAlchemy(fabrica), reloj=lambda: AHORA).ejecutar(
        SolicitudCambioDeEstado(id_))


def confirmar(fabrica: sessionmaker[Session], id_: str = "turno-demo-001") -> None:
    ConfirmarTurno(lambda: UnidadDeTrabajoSQLAlchemy(fabrica), reloj=lambda: AHORA).ejecutar(
        SolicitudCambioDeEstado(id_))


def estado_e_historial(fabrica: sessionmaker[Session], id_: str = "turno-demo-001") -> tuple[str, list[str]]:
    with fabrica() as sesion:
        fila = sesion.get(TurnoModelo, id_)
        assert fila is not None
        tipos = list(sesion.scalars(
            select(HistorialModelo.tipo).where(HistorialModelo.turno_id == id_).order_by(HistorialModelo.id)))
        return fila.estado, tipos


def test_confirmar_y_cancelar_persisten_estado_e_historial_en_orden(fabrica: sessionmaker[Session]) -> None:
    crear(fabrica)
    confirmar(fabrica)
    assert estado_e_historial(fabrica) == ("confirmado", ["creado", "confirmado"])

    cancelar(fabrica)
    assert estado_e_historial(fabrica) == ("cancelado", ["creado", "confirmado", "cancelado"])


# Escenario: Cancelar libera el intervalo para un nuevo turno
def test_cancelar_libera_el_intervalo_para_un_nuevo_turno(fabrica: sessionmaker[Session]) -> None:
    crear(fabrica)
    cancelar(fabrica)

    crear(fabrica, "turno-demo-002")

    assert estado_e_historial(fabrica, "turno-demo-002") == ("programado", ["creado"])


# Escenario: Cancelar libera el intervalo para un bloqueo
def test_cancelar_libera_el_intervalo_para_un_bloqueo(fabrica: sessionmaker[Session]) -> None:
    crear(fabrica)
    cancelar(fabrica)

    bloqueo = CrearBloqueo(lambda: UnidadDeTrabajoSQLAlchemy(fabrica)).ejecutar(
        SolicitudCrearBloqueo("bloqueo-demo-001", "profesional-demo-001", None, hora(9), hora(10)))

    assert bloqueo.id == "bloqueo-demo-001"


# Escenario: Confirmar conserva la reserva
def test_confirmar_conserva_la_reserva(fabrica: sessionmaker[Session]) -> None:
    crear(fabrica)
    confirmar(fabrica)

    with pytest.raises(ConflictoProfesionalError):
        crear(fabrica, "turno-demo-002", box_id="box-demo-002")


def test_la_base_acepta_escritura_directa_sobre_un_intervalo_cancelado(fabrica: sessionmaker[Session]) -> None:
    crear(fabrica)
    cancelar(fabrica)
    with fabrica() as sesion:
        sesion.execute(insert(TurnoModelo).values(
            id="turno-demo-directo", paciente_id="paciente-demo-002", profesional_id="profesional-demo-001",
            box_id="box-demo-001", prestacion_id="prestacion-demo-001",
            inicio=hora(9), fin=hora(9, 30), estado=EstadoTurno.PROGRAMADO.value))
        sesion.commit()
        assert sesion.get(TurnoModelo, "turno-demo-directo") is not None


def test_transicion_invalida_no_modifica_la_fila(fabrica: sessionmaker[Session]) -> None:
    crear(fabrica)
    cancelar(fabrica)

    with pytest.raises(TransicionInvalidaError):
        confirmar(fabrica)

    assert estado_e_historial(fabrica) == ("cancelado", ["creado", "cancelado"])


class UoWConCommitPausado(UnidadDeTrabajoSQLAlchemy):
    def __init__(self, fabrica: sessionmaker[Session], listo: Event, liberar: Event) -> None:
        super().__init__(fabrica)
        self._listo, self._liberar = listo, liberar

    def commit(self) -> None:
        self._listo.set()
        if not self._liberar.wait(8):
            raise TimeoutError("No se liberó el primer commit")
        super().commit()


# Escenario: Dos cancelaciones simultáneas
def test_dos_cancelaciones_concurrentes_registran_un_unico_evento(fabrica: sessionmaker[Session]) -> None:
    crear(fabrica)
    listo, liberar = Event(), Event()
    primera = CancelarTurno(lambda: UoWConCommitPausado(fabrica, listo, liberar), reloj=lambda: AHORA)

    with ThreadPoolExecutor(max_workers=2) as ejecutor:
        futura_primera = ejecutor.submit(primera.ejecutar, SolicitudCambioDeEstado("turno-demo-001"))
        try:
            assert listo.wait(8), "La primera cancelación no llegó al commit"
            futura_segunda = ejecutor.submit(cancelar, fabrica)
            with pytest.raises(FutureTimeoutError):
                futura_segunda.result(timeout=0.3)  # espera el FOR UPDATE de la primera
        finally:
            liberar.set()
        futura_primera.result(timeout=8)
        with pytest.raises(TransicionInvalidaError):
            futura_segunda.result(timeout=8)

    assert estado_e_historial(fabrica) == ("cancelado", ["creado", "cancelado"])
