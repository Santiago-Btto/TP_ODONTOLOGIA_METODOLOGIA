"""Escenarios del spec `creacion-de-turnos` sobre el caso de uso, con una unidad de trabajo en memoria."""

from datetime import UTC, datetime
from types import TracebackType
from typing import Self

import pytest

from app.application.crear_turno import CrearTurno, SolicitudCrearTurno
from app.domain.bloqueos import BloqueoDeDisponibilidad
from app.domain.disponibilidad import (
    ConflictoBloqueoBoxError, ConflictoBloqueoProfesionalError,
    ConflictoBoxError, ConflictoProfesionalError, se_solapan,
)
from app.domain.turnos import (
    Box,
    DuracionInvalidaError,
    HistorialDeCambio,
    IntervaloInvalidoError,
    Paciente,
    Prestacion,
    Profesional,
    RecursoInexistenteError,
    TipoCambio,
    Turno,
)
from tests.datos_demo import BOX, BOX_2, PACIENTE, PRESTACION, PROFESIONAL, PROFESIONAL_2

AHORA = datetime(2030, 1, 1, 8, 0, tzinfo=UTC)


def hora(hh: int, mm: int) -> datetime:
    return datetime(2030, 1, 10, hh, mm, tzinfo=UTC)


class RecursosEnMemoria:
    def __init__(self, prestaciones: list[Prestacion]) -> None:
        self.pacientes = {PACIENTE.id: PACIENTE}
        self.profesionales = {p.id: p for p in (PROFESIONAL, PROFESIONAL_2)}
        self.boxes = {b.id: b for b in (BOX, BOX_2)}
        self.prestaciones = {p.id: p for p in prestaciones}
        self.bloqueos_adquiridos: list[tuple[str | None, str | None]] = []

    def paciente(self, id_: str) -> Paciente | None:
        return self.pacientes.get(id_)

    def profesional(self, id_: str) -> Profesional | None:
        return self.profesionales.get(id_)

    def box(self, id_: str) -> Box | None:
        return self.boxes.get(id_)

    def prestacion(self, id_: str) -> Prestacion | None:
        return self.prestaciones.get(id_)

    def bloquear(self, profesional_id: str | None, box_id: str | None) -> None:
        self.bloqueos_adquiridos.append((profesional_id, box_id))


class TurnosEnMemoria:
    def __init__(self) -> None:
        self.confirmados: list[Turno] = []
        self.pendientes: list[Turno] = []

    def activos_que_se_solapan(self, profesional_id: str, box_id: str, inicio: datetime, fin: datetime) -> list[Turno]:
        candidato = Turno("_", "_", profesional_id, box_id, "_", inicio, fin)
        return [
            t for t in self.confirmados
            if (t.profesional_id == profesional_id or t.box_id == box_id) and se_solapan(t, candidato)
        ]

    def agregar(self, turno: Turno) -> None:
        self.pendientes.append(turno)


class HistorialesEnMemoria:
    def __init__(self) -> None:
        self.confirmados: list[HistorialDeCambio] = []
        self.pendientes: list[HistorialDeCambio] = []

    def agregar(self, historial: HistorialDeCambio) -> None:
        self.pendientes.append(historial)


class BloqueosEnMemoria:
    def __init__(self) -> None:
        self.confirmados: list[BloqueoDeDisponibilidad] = []

    def que_se_solapan(self, profesional_id: str, box_id: str,
                       inicio: datetime, fin: datetime) -> list[BloqueoDeDisponibilidad]:
        return [b for b in self.confirmados if b.inicio < fin and inicio < b.fin and
                (b.profesional_id == profesional_id or b.box_id == box_id)]


class UnidadDeTrabajoEnMemoria:
    def __init__(self, prestaciones: list[Prestacion] | None = None) -> None:
        self.recursos = RecursosEnMemoria(prestaciones or [PRESTACION])
        self.turnos = TurnosEnMemoria()
        self.historiales = HistorialesEnMemoria()
        self.bloqueos = BloqueosEnMemoria()
        self.commits = 0

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        tipo: type[BaseException] | None,
        error: BaseException | None,
        traza: TracebackType | None,
    ) -> None:
        self.turnos.pendientes.clear()
        self.historiales.pendientes.clear()

    def commit(self) -> None:
        self.turnos.confirmados += self.turnos.pendientes
        self.historiales.confirmados += self.historiales.pendientes
        self.turnos.pendientes.clear()
        self.historiales.pendientes.clear()
        self.commits += 1


def preparar(prestaciones: list[Prestacion] | None = None) -> tuple[CrearTurno, UnidadDeTrabajoEnMemoria]:
    uow = UnidadDeTrabajoEnMemoria(prestaciones)
    return CrearTurno(lambda: uow, reloj=lambda: AHORA), uow


def solicitud(**cambios: object) -> SolicitudCrearTurno:
    base: dict[str, object] = {
        "id": "turno-demo-alta-001",
        "paciente_id": PACIENTE.id,
        "profesional_id": PROFESIONAL.id,
        "box_id": BOX.id,
        "prestacion_id": PRESTACION.id,
        "inicio": hora(9, 0),
    }
    base.update(cambios)
    return SolicitudCrearTurno(**base)  # type: ignore[arg-type]


def existente(id_: str, profesional_id: str, box_id: str, inicio: datetime, fin: datetime) -> Turno:
    return Turno(id_, "paciente-demo-002", profesional_id, box_id, PRESTACION.id, inicio, fin)


def assert_sin_cambios(uow: UnidadDeTrabajoEnMemoria, turnos_previos: list[Turno]) -> None:
    assert uow.turnos.confirmados == turnos_previos
    assert uow.historiales.confirmados == []
    assert uow.commits == 0


def bloqueo(*, profesional_id: str | None = PROFESIONAL.id, box_id: str | None = None,
            inicio: datetime | None = None, fin: datetime | None = None) -> BloqueoDeDisponibilidad:
    return BloqueoDeDisponibilidad("bloqueo-demo-001", profesional_id, box_id,
                                   inicio or hora(9, 0), fin or hora(10, 0))


# Escenario: Alta exitosa
def test_alta_exitosa_crea_el_turno_y_un_unico_historial_creado() -> None:
    caso, uow = preparar()

    creado = caso.ejecutar(solicitud())

    assert (creado.inicio, creado.fin) == (hora(9, 0), hora(9, 30))
    assert uow.turnos.confirmados == [creado]
    assert uow.historiales.confirmados == [HistorialDeCambio(creado.id, TipoCambio.CREADO, AHORA)]
    assert uow.commits == 1


# Escenario: Conflicto por profesional
def test_conflicto_por_profesional_no_escribe_turno_ni_historial() -> None:
    caso, uow = preparar()
    previos = [existente("turno-demo-prev", PROFESIONAL.id, BOX_2.id, hora(9, 0), hora(9, 30))]
    uow.turnos.confirmados = list(previos)

    with pytest.raises(ConflictoProfesionalError):
        caso.ejecutar(solicitud())

    assert_sin_cambios(uow, previos)


# Escenario: Conflicto por box
def test_conflicto_por_box_no_escribe_turno_ni_historial() -> None:
    caso, uow = preparar()
    previos = [existente("turno-demo-prev", PROFESIONAL_2.id, BOX.id, hora(9, 0), hora(9, 30))]
    uow.turnos.confirmados = list(previos)

    with pytest.raises(ConflictoBoxError):
        caso.ejecutar(solicitud())

    assert_sin_cambios(uow, previos)


# Escenario: Reserva contigua
def test_reserva_contigua_con_mismo_profesional_y_box_se_crea() -> None:
    caso, uow = preparar()
    uow.turnos.confirmados = [existente("turno-demo-prev", PROFESIONAL.id, BOX.id, hora(8, 30), hora(9, 0))]

    creado = caso.ejecutar(solicitud())

    assert len(uow.turnos.confirmados) == 2
    assert uow.historiales.confirmados == [HistorialDeCambio(creado.id, TipoCambio.CREADO, AHORA)]


# Escenario: Intervalo sin duración positiva
@pytest.mark.parametrize("fin", [hora(9, 0), hora(8, 45)])
def test_intervalo_sin_duracion_positiva_no_persiste_cambios(fin: datetime) -> None:
    caso, uow = preparar()

    with pytest.raises(IntervaloInvalidoError):
        caso.ejecutar(solicitud(fin=fin))

    assert_sin_cambios(uow, [])


# Escenario: Prestación con duración inválida
@pytest.mark.parametrize("duracion", [0, -30])
def test_prestacion_con_duracion_invalida_no_persiste_cambios(duracion: int) -> None:
    invalida = Prestacion(id="prestacion-demo-invalida", nombre="Prestación Demo Inválida", duracion_minutos=duracion)
    caso, uow = preparar([invalida])

    with pytest.raises(DuracionInvalidaError):
        caso.ejecutar(solicitud(prestacion_id=invalida.id))

    assert_sin_cambios(uow, [])


# Escenario: Profesional inexistente (y el resto de los recursos)
@pytest.mark.parametrize("campo", ["paciente_id", "profesional_id", "box_id", "prestacion_id"])
def test_recurso_inexistente_no_persiste_cambios(campo: str) -> None:
    caso, uow = preparar()

    with pytest.raises(RecursoInexistenteError):
        caso.ejecutar(solicitud(**{campo: "no-existe-demo"}))

    assert_sin_cambios(uow, [])


@pytest.mark.parametrize("recurso,esperado", [
    ({"profesional_id": PROFESIONAL.id, "box_id": None}, ConflictoBloqueoProfesionalError),
    ({"profesional_id": None, "box_id": BOX.id}, ConflictoBloqueoBoxError),
])
def test_alta_intersectante_con_bloqueo_no_crea_turno_ni_historial(
    recurso: dict[str, str | None], esperado: type[Exception]
) -> None:
    caso, uow = preparar()
    uow.bloqueos.confirmados.append(bloqueo(**recurso))
    with pytest.raises(esperado):
        caso.ejecutar(solicitud())
    assert_sin_cambios(uow, [])


@pytest.mark.parametrize("inicio,fin", [(hora(8, 0), hora(9, 0)), (hora(9, 30), hora(10, 0))])
def test_alta_contigua_a_bloqueo_conserva_historial_unico(inicio: datetime, fin: datetime) -> None:
    caso, uow = preparar()
    uow.bloqueos.confirmados.append(bloqueo(inicio=inicio, fin=fin))
    creado = caso.ejecutar(solicitud())
    assert uow.historiales.confirmados == [HistorialDeCambio(creado.id, TipoCambio.CREADO, AHORA)]
    assert uow.commits == 1


def test_alta_toma_bloqueos_de_profesional_y_box_antes_de_leer_disponibilidad() -> None:
    caso, uow = preparar()
    creado = caso.ejecutar(solicitud())
    assert uow.recursos.bloqueos_adquiridos == [(creado.profesional_id, creado.box_id)]
