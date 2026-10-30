"""Contrato de bloqueos probado contra PostgreSQL real, sin SQLite ni mocks."""

from datetime import UTC, datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from threading import Event

import pytest
from sqlalchemy import func, insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.application.crear_bloqueo import CrearBloqueo, SolicitudCrearBloqueo
from app.application.crear_turno import CrearTurno, SolicitudCrearTurno
from app.domain.disponibilidad import (
    ConflictoBloqueoBoxError, ConflictoBloqueoProfesionalError, ConflictoTurnoExistenteError,
)
from app.infrastructure.modelos import BloqueoModelo, HistorialModelo, TurnoModelo
from app.infrastructure.unidad_de_trabajo import UnidadDeTrabajoSQLAlchemy


def hora(h: int, m: int = 0) -> datetime:
    return datetime(2030, 1, 10, h, m, tzinfo=UTC)


def fila(id_: str, *, profesional_id: str | None = "profesional-demo-001",
         box_id: str | None = None, inicio: datetime | None = None,
         fin: datetime | None = None) -> dict[str, object]:
    return dict(id=id_, profesional_id=profesional_id, box_id=box_id,
                inicio=inicio or hora(9), fin=fin or hora(10), motivo=None)


def insertar(fabrica: sessionmaker[Session], valores: dict[str, object]) -> None:
    with fabrica() as sesion:
        sesion.execute(insert(BloqueoModelo).values(**valores))
        sesion.commit()


def cantidad(fabrica: sessionmaker[Session]) -> int:
    with fabrica() as sesion:
        return sesion.scalar(select(func.count()).select_from(BloqueoModelo)) or 0


@pytest.mark.parametrize("recurso", [
    {"profesional_id": None, "box_id": None},
    {"profesional_id": "profesional-demo-001", "box_id": "box-demo-001"},
])
def test_tabla_rechaza_cero_o_dos_recursos(fabrica: sessionmaker[Session], recurso: dict[str, str | None]) -> None:
    with pytest.raises(IntegrityError, match="bloqueos_un_recurso"):
        insertar(fabrica, fila("bloqueo-demo-xor", **recurso))
    assert cantidad(fabrica) == 0


@pytest.mark.parametrize("fin", [hora(9), hora(8, 30)])
def test_tabla_rechaza_intervalo_no_positivo(fabrica: sessionmaker[Session], fin: datetime) -> None:
    with pytest.raises(IntegrityError, match="bloqueos_fin_posterior_al_inicio"):
        insertar(fabrica, fila("bloqueo-demo-intervalo", fin=fin))


@pytest.mark.parametrize("recurso", [
    {"profesional_id": "profesional-inexistente", "box_id": None},
    {"profesional_id": None, "box_id": "box-inexistente"},
])
def test_tabla_rechaza_recurso_inexistente(fabrica: sessionmaker[Session], recurso: dict[str, str | None]) -> None:
    with pytest.raises(IntegrityError):
        insertar(fabrica, fila("bloqueo-demo-fk", **recurso))


@pytest.mark.parametrize("intervalo", [(hora(9, 30), hora(10, 30)), (hora(10), hora(11))])
def test_tabla_permite_bloqueos_superpuestos_y_contiguos(
    fabrica: sessionmaker[Session], intervalo: tuple[datetime, datetime]
) -> None:
    insertar(fabrica, fila("bloqueo-demo-uno"))
    insertar(fabrica, fila("bloqueo-demo-dos", inicio=intervalo[0], fin=intervalo[1]))
    assert cantidad(fabrica) == 2


@pytest.mark.parametrize("recurso", [
    {"profesional_id": "profesional-demo-001", "box_id": None},
    {"profesional_id": None, "box_id": "box-demo-001"},
])
def test_caso_de_uso_guarda_bloqueo_de_un_recurso(
    fabrica: sessionmaker[Session], recurso: dict[str, str | None]
) -> None:
    creado = CrearBloqueo(lambda: UnidadDeTrabajoSQLAlchemy(fabrica)).ejecutar(
        SolicitudCrearBloqueo("bloqueo-demo-caso", **recurso, inicio=hora(9), fin=hora(10), motivo="Demo")
    )
    with fabrica() as sesion:
        fila_guardada = sesion.get(BloqueoModelo, creado.id)
        assert fila_guardada is not None
        assert (fila_guardada.profesional_id, fila_guardada.box_id, fila_guardada.motivo) == (
            recurso["profesional_id"], recurso["box_id"], "Demo")


@pytest.mark.parametrize("recurso", [
    {"profesional_id": "profesional-demo-001", "box_id": "box-demo-002"},
    {"profesional_id": "profesional-demo-002", "box_id": "box-demo-001"},
])
def test_repositorio_busca_bloqueo_intersectante_por_cualquiera_de_los_recursos(
    fabrica: sessionmaker[Session], recurso: dict[str, str]
) -> None:
    insertar(fabrica, fila("bloqueo-demo-profesional"))
    insertar(fabrica, fila("bloqueo-demo-box", profesional_id=None, box_id="box-demo-001"))
    with UnidadDeTrabajoSQLAlchemy(fabrica) as uow:
        hallados = uow.bloqueos.que_se_solapan(**recurso, inicio=hora(9, 30), fin=hora(10, 30))
        contiguos = uow.bloqueos.que_se_solapan(**recurso, inicio=hora(10), fin=hora(11))
    assert len(hallados) == 1
    assert contiguos == []


@pytest.mark.parametrize("recurso", [
    {"profesional_id": "profesional-demo-001", "box_id": None},
    {"profesional_id": None, "box_id": "box-demo-001"},
])
def test_bloqueo_que_cruza_turno_existente_falla_sin_escritura(
    fabrica: sessionmaker[Session], recurso: dict[str, str | None]
) -> None:
    crear_turno = CrearTurno(lambda: UnidadDeTrabajoSQLAlchemy(fabrica), reloj=lambda: hora(8))
    crear_turno.ejecutar(SolicitudCrearTurno("turno-demo-previo", "paciente-demo-001", "profesional-demo-001",
                                           "box-demo-001", "prestacion-demo-001", hora(9, 30)))
    with pytest.raises(ConflictoTurnoExistenteError):
        CrearBloqueo(lambda: UnidadDeTrabajoSQLAlchemy(fabrica)).ejecutar(
            SolicitudCrearBloqueo("bloqueo-demo-tardio", **recurso, inicio=hora(9), fin=hora(10))
        )
    assert cantidad(fabrica) == 0
    with fabrica() as sesion:
        assert sesion.scalar(select(func.count()).select_from(TurnoModelo)) == 1
        assert sesion.scalar(select(func.count()).select_from(HistorialModelo)) == 1


@pytest.mark.parametrize("recurso,esperado", [
    ({"profesional_id": "profesional-demo-001", "box_id": None}, ConflictoBloqueoProfesionalError),
    ({"profesional_id": None, "box_id": "box-demo-001"}, ConflictoBloqueoBoxError),
])
def test_turno_que_cruza_bloqueo_falla_sin_historial(
    fabrica: sessionmaker[Session], recurso: dict[str, str | None], esperado: type[Exception]
) -> None:
    CrearBloqueo(lambda: UnidadDeTrabajoSQLAlchemy(fabrica)).ejecutar(
        SolicitudCrearBloqueo("bloqueo-demo-previo", **recurso, inicio=hora(9), fin=hora(10))
    )
    with pytest.raises(esperado):
        CrearTurno(lambda: UnidadDeTrabajoSQLAlchemy(fabrica), reloj=lambda: hora(8)).ejecutar(
            SolicitudCrearTurno("turno-demo-tardio", "paciente-demo-001", "profesional-demo-001",
                                "box-demo-001", "prestacion-demo-001", hora(9, 30))
        )
    with fabrica() as sesion:
        assert sesion.scalar(select(func.count()).select_from(TurnoModelo)) == 0
        assert sesion.scalar(select(func.count()).select_from(HistorialModelo)) == 0


class UoWConCommitPausado(UnidadDeTrabajoSQLAlchemy):
    def __init__(self, fabrica: sessionmaker[Session], listo: Event, liberar: Event) -> None:
        super().__init__(fabrica)
        self._listo = listo
        self._liberar = liberar

    def commit(self) -> None:
        self._listo.set()
        if not self._liberar.wait(8):
            raise TimeoutError("No se liberó el primer commit de la carrera")
        super().commit()


class RecursosConAviso:
    def __init__(self, original: object, intenta_bloquear: Event) -> None:
        self._original = original
        self._intenta_bloquear = intenta_bloquear

    def __getattr__(self, nombre: str):
        return getattr(self._original, nombre)

    def bloquear(self, profesional_id: str | None, box_id: str | None) -> None:
        self._intenta_bloquear.set()
        self._original.bloquear(profesional_id, box_id)  # type: ignore[attr-defined]


class UoWConAvisoDeLock(UnidadDeTrabajoSQLAlchemy):
    def __init__(self, fabrica: sessionmaker[Session], intenta_bloquear: Event) -> None:
        super().__init__(fabrica)
        self._intenta_bloquear = intenta_bloquear

    def __enter__(self):
        super().__enter__()
        self.recursos = RecursosConAviso(self.recursos, self._intenta_bloquear)  # type: ignore[assignment]
        return self


@pytest.mark.parametrize("primer_tipo,recurso", [
    ("turno", "profesional"), ("bloqueo", "profesional"),
    ("turno", "box"), ("bloqueo", "box"),
])
def test_carrera_turno_y_bloqueo_serializa_recurso_y_confirma_solo_uno(
    fabrica: sessionmaker[Session], primer_tipo: str, recurso: str
) -> None:
    """La segunda solicitud espera el lock y relee tras el commit de la primera."""
    listo, liberar, intento = Event(), Event(), Event()
    ids = ({"profesional_id": "profesional-demo-001", "box_id": None} if recurso == "profesional"
           else {"profesional_id": None, "box_id": "box-demo-001"})

    def crear_turno(primero: bool) -> object:
        fabrica_uow = (lambda: UoWConCommitPausado(fabrica, listo, liberar)) if primero else (
            lambda: UoWConAvisoDeLock(fabrica, intento))
        return CrearTurno(fabrica_uow, reloj=lambda: hora(8)).ejecutar(
            SolicitudCrearTurno("turno-demo-carrera", "paciente-demo-001", "profesional-demo-001",
                                "box-demo-001", "prestacion-demo-001", hora(9, 30))
        )

    def crear_bloqueo(primero: bool) -> object:
        fabrica_uow = (lambda: UoWConCommitPausado(fabrica, listo, liberar)) if primero else (
            lambda: UoWConAvisoDeLock(fabrica, intento))
        return CrearBloqueo(fabrica_uow).ejecutar(
            SolicitudCrearBloqueo("bloqueo-demo-carrera", **ids, inicio=hora(9), fin=hora(10))
        )

    primera = crear_turno if primer_tipo == "turno" else crear_bloqueo
    segunda = crear_bloqueo if primer_tipo == "turno" else crear_turno
    esperado = ConflictoTurnoExistenteError if primer_tipo == "turno" else (
        ConflictoBloqueoProfesionalError if recurso == "profesional" else ConflictoBloqueoBoxError)

    with ThreadPoolExecutor(max_workers=2) as ejecutor:
        futura_primera = ejecutor.submit(primera, True)
        try:
            assert listo.wait(8), "La primera operación no alcanzó su commit"
            futura_segunda = ejecutor.submit(segunda, False)
            assert intento.wait(8), "La segunda operación no intentó bloquear el recurso"
            with pytest.raises(FutureTimeoutError):
                futura_segunda.result(timeout=0.15)
        finally:
            liberar.set()
        futura_primera.result(timeout=8)
        with pytest.raises(esperado):
            futura_segunda.result(timeout=8)

    with fabrica() as sesion:
        turnos = sesion.scalar(select(func.count()).select_from(TurnoModelo)) or 0
        bloqueos = sesion.scalar(select(func.count()).select_from(BloqueoModelo)) or 0
        historiales = sesion.scalar(select(func.count()).select_from(HistorialModelo)) or 0
    assert (turnos, bloqueos, historiales) == ((1, 0, 1) if primer_tipo == "turno" else (0, 1, 0))
