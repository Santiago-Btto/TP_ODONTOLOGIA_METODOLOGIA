"""Reprogramación atómica (C-04) contra PostgreSQL real."""

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from datetime import UTC, datetime
from threading import Event

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.application.crear_bloqueo import CrearBloqueo, SolicitudCrearBloqueo
from app.application.crear_turno import CrearTurno, SolicitudCrearTurno
from app.application.reprogramar_turno import ReprogramarTurno, SolicitudReprogramarTurno
from app.domain.disponibilidad import ConflictoBloqueoBoxError, ConflictoProfesionalError
from app.domain.turnos import HistorialDeCambio
from app.infrastructure.modelos import HistorialModelo, TurnoModelo
from app.infrastructure.unidad_de_trabajo import HistorialesSQLAlchemy, UnidadDeTrabajoSQLAlchemy
from tests.infrastructure.test_bloqueos import UoWConAvisoDeLock, UoWConCommitPausado

AHORA = datetime(2030, 1, 1, 8, 0, tzinfo=UTC)


def hora(h: int, m: int = 0) -> datetime:
    return datetime(2030, 1, 10, h, m, tzinfo=UTC)


def crear(fabrica: sessionmaker[Session], id_: str, inicio: datetime, *, profesional: str = "profesional-demo-001",
          box: str = "box-demo-001", uow: object = None) -> None:
    fabrica_uow = uow or (lambda: UnidadDeTrabajoSQLAlchemy(fabrica))
    CrearTurno(fabrica_uow, reloj=lambda: AHORA).ejecutar(  # type: ignore[arg-type]
        SolicitudCrearTurno(id_, "paciente-demo-001", profesional, box, "prestacion-demo-001", inicio))


def reprogramar(fabrica: sessionmaker[Session], uow: object = None, **cambios: object) -> None:
    fabrica_uow = uow or (lambda: UnidadDeTrabajoSQLAlchemy(fabrica))
    ReprogramarTurno(fabrica_uow, reloj=lambda: AHORA).ejecutar(  # type: ignore[arg-type]
        SolicitudReprogramarTurno("turno-demo-001", **cambios))  # type: ignore[arg-type]


def fila(fabrica: sessionmaker[Session], id_: str = "turno-demo-001") -> tuple[str, str, datetime, datetime]:
    with fabrica() as sesion:
        turno = sesion.get(TurnoModelo, id_)
        assert turno is not None
        return turno.profesional_id, turno.box_id, turno.inicio, turno.fin


def historial(fabrica: sessionmaker[Session]) -> list[HistorialModelo]:
    with fabrica() as sesion:
        return list(sesion.scalars(select(HistorialModelo).order_by(HistorialModelo.id)))


# Escenario: Cambio de horario válido (persistencia de antes/después)
def test_reprogramar_persiste_intervalo_recursos_y_resumen_en_el_historial(fabrica: sessionmaker[Session]) -> None:
    crear(fabrica, "turno-demo-001", hora(9))

    reprogramar(fabrica, inicio=hora(11), box_id="box-demo-002")

    assert fila(fabrica) == ("profesional-demo-001", "box-demo-002", hora(11), hora(11, 30))
    eventos = historial(fabrica)
    assert [e.tipo for e in eventos] == ["creado", "reprogramado"]
    assert (eventos[0].antes, eventos[0].despues) == (None, None)
    assert eventos[1].antes == {"profesional_id": "profesional-demo-001", "box_id": "box-demo-001",
                                "inicio": "2030-01-10T09:00:00+00:00", "fin": "2030-01-10T09:30:00+00:00"}
    assert eventos[1].despues == {"profesional_id": "profesional-demo-001", "box_id": "box-demo-002",
                                  "inicio": "2030-01-10T11:00:00+00:00", "fin": "2030-01-10T11:30:00+00:00"}


# Escenario: El intervalo anterior queda libre
def test_el_intervalo_anterior_queda_libre(fabrica: sessionmaker[Session]) -> None:
    crear(fabrica, "turno-demo-001", hora(9))
    reprogramar(fabrica, inicio=hora(11))

    crear(fabrica, "turno-demo-002", hora(9))

    assert fila(fabrica, "turno-demo-002")[2] == hora(9)


# Escenario: Correr un turno dentro de su propio intervalo (también para la exclusión GiST)
def test_la_base_acepta_que_el_turno_solape_su_version_anterior(fabrica: sessionmaker[Session]) -> None:
    crear(fabrica, "turno-demo-001", hora(9))

    reprogramar(fabrica, inicio=hora(9, 15))

    assert fila(fabrica)[2:] == (hora(9, 15), hora(9, 45))


# Escenario: Rechazo sin cambios
def test_rechazo_por_conflicto_conserva_turno_e_historial(fabrica: sessionmaker[Session]) -> None:
    crear(fabrica, "turno-demo-001", hora(9))
    crear(fabrica, "turno-demo-otro", hora(11), box="box-demo-002")

    with pytest.raises(ConflictoProfesionalError):
        reprogramar(fabrica, inicio=hora(11))

    assert fila(fabrica) == ("profesional-demo-001", "box-demo-001", hora(9), hora(9, 30))
    assert [e.tipo for e in historial(fabrica)] == ["creado", "creado"]


def test_rechazo_por_bloqueo_del_nuevo_box(fabrica: sessionmaker[Session]) -> None:
    crear(fabrica, "turno-demo-001", hora(9))
    CrearBloqueo(lambda: UnidadDeTrabajoSQLAlchemy(fabrica)).ejecutar(
        SolicitudCrearBloqueo("bloqueo-demo-001", None, "box-demo-002", hora(9), hora(10)))

    with pytest.raises(ConflictoBloqueoBoxError):
        reprogramar(fabrica, box_id="box-demo-002")

    assert fila(fabrica)[1] == "box-demo-001"


class HistorialesQueFallan(HistorialesSQLAlchemy):
    def agregar(self, historial: HistorialDeCambio) -> None:
        raise RuntimeError("Fallo simulado al registrar historial")


class UoWConHistorialFallido(UnidadDeTrabajoSQLAlchemy):
    def __enter__(self):  # type: ignore[no-untyped-def]
        super().__enter__()
        self.historiales = HistorialesQueFallan(self._sesion)
        return self


# Escenario: Fallo al registrar el historial
def test_fallo_al_registrar_historial_revierte_la_actualizacion_ya_enviada(fabrica: sessionmaker[Session]) -> None:
    crear(fabrica, "turno-demo-001", hora(9))

    with pytest.raises(RuntimeError):
        reprogramar(fabrica, uow=lambda: UoWConHistorialFallido(fabrica), inicio=hora(11))

    assert fila(fabrica) == ("profesional-demo-001", "box-demo-001", hora(9), hora(9, 30))
    assert [e.tipo for e in historial(fabrica)] == ["creado"]


# Escenarios: Reprogramación confirma antes que un alta / Alta confirma antes que una reprogramación
@pytest.mark.parametrize("primera", ["reprogramacion", "alta"])
def test_carrera_entre_reprogramacion_y_alta_confirma_solo_una(
    fabrica: sessionmaker[Session], primera: str
) -> None:
    crear(fabrica, "turno-demo-001", hora(9))
    listo, liberar, intento = Event(), Event(), Event()

    def operar(cual: str, es_primera: bool) -> None:
        uow = (lambda: UoWConCommitPausado(fabrica, listo, liberar)) if es_primera else (
            lambda: UoWConAvisoDeLock(fabrica, intento))
        if cual == "reprogramacion":
            reprogramar(fabrica, uow=uow, inicio=hora(11))
        else:
            crear(fabrica, "turno-demo-alta", hora(11), box="box-demo-002", uow=uow)

    segunda = "alta" if primera == "reprogramacion" else "reprogramacion"
    with ThreadPoolExecutor(max_workers=2) as ejecutor:
        futura_primera = ejecutor.submit(operar, primera, True)
        try:
            assert listo.wait(8), "La primera operación no alcanzó su commit"
            futura_segunda = ejecutor.submit(operar, segunda, False)
            assert intento.wait(8), "La segunda operación no intentó bloquear el recurso"
            with pytest.raises(FutureTimeoutError):
                futura_segunda.result(timeout=0.15)
        finally:
            liberar.set()
        futura_primera.result(timeout=8)
        with pytest.raises(ConflictoProfesionalError):
            futura_segunda.result(timeout=8)

    with fabrica() as sesion:
        ids = set(sesion.scalars(select(TurnoModelo.id)))
    if primera == "reprogramacion":
        assert ids == {"turno-demo-001"}
        assert fila(fabrica)[2] == hora(11)
    else:
        assert ids == {"turno-demo-001", "turno-demo-alta"}
        assert fila(fabrica)[2] == hora(9)
