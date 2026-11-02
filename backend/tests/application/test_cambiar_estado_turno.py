"""Escenarios de `ciclo-de-vida-del-turno` sobre los casos de uso, con una unidad de trabajo en memoria."""

from dataclasses import replace
from datetime import UTC, datetime
from types import TracebackType
from typing import Self

import pytest

from app.application.cambiar_estado_turno import (
    CancelarTurno,
    ConfirmarTurno,
    SolicitudCambioDeEstado,
)
from app.domain.turnos import (
    EstadoTurno,
    HistorialDeCambio,
    RecursoInexistenteError,
    TipoCambio,
    TransicionInvalidaError,
    Turno,
)
from tests.datos_demo import BOX, PACIENTE, PRESTACION, PROFESIONAL

AHORA = datetime(2030, 1, 1, 8, 0, tzinfo=UTC)
TURNO = Turno(
    "turno-demo-001", PACIENTE.id, PROFESIONAL.id, BOX.id, PRESTACION.id,
    datetime(2030, 1, 10, 9, 0, tzinfo=UTC), datetime(2030, 1, 10, 9, 30, tzinfo=UTC),
)


class TurnosEnMemoria:
    def __init__(self, turnos: list[Turno]) -> None:
        self.confirmados = {t.id: t for t in turnos}
        self.pendientes: dict[str, Turno] = {}
        self.bloqueados: list[str] = []

    def obtener_para_actualizar(self, turno_id: str) -> Turno | None:
        self.bloqueados.append(turno_id)
        return self.confirmados.get(turno_id)

    def actualizar(self, turno: Turno) -> None:
        self.pendientes[turno.id] = turno


class HistorialesEnMemoria:
    def __init__(self) -> None:
        self.confirmados: list[HistorialDeCambio] = []
        self.pendientes: list[HistorialDeCambio] = []

    def agregar(self, historial: HistorialDeCambio) -> None:
        self.pendientes.append(historial)


class UoWEnMemoria:
    def __init__(self, turnos: list[Turno]) -> None:
        self.turnos = TurnosEnMemoria(turnos)
        self.historiales = HistorialesEnMemoria()
        self.commits = 0

    def __enter__(self) -> Self:
        return self

    def __exit__(self, tipo: type[BaseException] | None, error: BaseException | None,
                 traza: TracebackType | None) -> None:
        self.turnos.pendientes.clear()
        self.historiales.pendientes.clear()

    def commit(self) -> None:
        self.turnos.confirmados.update(self.turnos.pendientes)
        self.historiales.confirmados += self.historiales.pendientes
        self.turnos.pendientes.clear()
        self.historiales.pendientes.clear()
        self.commits += 1


def preparar(estado: EstadoTurno = EstadoTurno.PROGRAMADO) -> UoWEnMemoria:
    return UoWEnMemoria([replace(TURNO, estado=estado)])


# Escenario: Confirmación exitosa
def test_confirmar_cambia_estado_y_registra_un_evento_confirmado() -> None:
    uow = preparar()

    resultado = ConfirmarTurno(lambda: uow, reloj=lambda: AHORA).ejecutar(SolicitudCambioDeEstado(TURNO.id))

    assert resultado == replace(TURNO, estado=EstadoTurno.CONFIRMADO)
    assert uow.turnos.confirmados[TURNO.id] == resultado
    assert uow.historiales.confirmados == [HistorialDeCambio(TURNO.id, TipoCambio.CONFIRMADO, AHORA)]
    assert uow.commits == 1


# Escenarios: Cancelación de un turno programado / confirmado
@pytest.mark.parametrize("estado", [EstadoTurno.PROGRAMADO, EstadoTurno.CONFIRMADO])
def test_cancelar_un_turno_activo_registra_un_evento_cancelado(estado: EstadoTurno) -> None:
    uow = preparar(estado)

    resultado = CancelarTurno(lambda: uow, reloj=lambda: AHORA).ejecutar(SolicitudCambioDeEstado(TURNO.id))

    assert resultado.estado is EstadoTurno.CANCELADO
    assert (resultado.inicio, resultado.fin) == (TURNO.inicio, TURNO.fin)
    assert uow.historiales.confirmados == [HistorialDeCambio(TURNO.id, TipoCambio.CANCELADO, AHORA)]
    assert uow.commits == 1


# Escenarios: Confirmar un turno cancelado / Cancelar dos veces / Confirmar dos veces
@pytest.mark.parametrize("caso,estado", [
    (ConfirmarTurno, EstadoTurno.CANCELADO),
    (ConfirmarTurno, EstadoTurno.CONFIRMADO),
    (CancelarTurno, EstadoTurno.CANCELADO),
])
def test_transicion_invalida_no_cambia_estado_ni_escribe_historial(
    caso: type[ConfirmarTurno] | type[CancelarTurno], estado: EstadoTurno
) -> None:
    uow = preparar(estado)

    with pytest.raises(TransicionInvalidaError):
        caso(lambda: uow, reloj=lambda: AHORA).ejecutar(SolicitudCambioDeEstado(TURNO.id))

    assert uow.turnos.confirmados[TURNO.id].estado is estado
    assert uow.historiales.confirmados == []
    assert uow.commits == 0


# Escenario: Turno inexistente
@pytest.mark.parametrize("caso", [ConfirmarTurno, CancelarTurno])
def test_turno_inexistente_informa_recurso_inexistente_sin_escribir(
    caso: type[ConfirmarTurno] | type[CancelarTurno]
) -> None:
    uow = preparar()

    with pytest.raises(RecursoInexistenteError) as error:
        caso(lambda: uow, reloj=lambda: AHORA).ejecutar(SolicitudCambioDeEstado("turno-demo-inexistente"))

    assert error.value.tipo == "turno"
    assert uow.historiales.confirmados == []
    assert uow.commits == 0


@pytest.mark.parametrize("caso", [ConfirmarTurno, CancelarTurno])
def test_lee_el_turno_con_bloqueo_de_fila(caso: type[ConfirmarTurno] | type[CancelarTurno]) -> None:
    uow = preparar()

    caso(lambda: uow, reloj=lambda: AHORA).ejecutar(SolicitudCambioDeEstado(TURNO.id))

    assert uow.turnos.bloqueados == [TURNO.id]
