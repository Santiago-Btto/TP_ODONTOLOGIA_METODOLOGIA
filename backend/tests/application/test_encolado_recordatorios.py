"""Escenarios de encolado pos-commit y resiliencia ante caída de Redis (C-16, RN-EX-02)."""

from datetime import UTC, datetime
from types import TracebackType
from typing import Self

import pytest

from app.application.cambiar_estado_turno import (
    CancelarTurno,
    ConfirmarTurno,
    SolicitudCambioDeEstado,
)
from app.application.crear_turno import CrearTurno, SolicitudCrearTurno
from app.domain.recordatorios import MotivoRecordatorio, TareaRecordatorio
from app.domain.turnos import (
    EstadoTurno,
    RecursoInexistenteError,
    TransicionInvalidaError,
    Turno,
)
from tests.application.test_cambiar_estado_turno import TURNO, UoWEnMemoria as UoWCambioEstado
from tests.application.test_crear_turno import (
    AHORA,
    UnidadDeTrabajoEnMemoria as UoWCrearTurno,
    solicitud,
)


class ColaEspia:
    """Registra las tareas encoladas y el estado del commit al momento de encolar."""

    def __init__(self, uow_commits_fn: callable, fallar: bool = False) -> None:
        self._uow_commits_fn = uow_commits_fn
        self._fallar = fallar
        self.encoladas: list[TareaRecordatorio] = []
        self.commits_al_encolar: list[int] = []

    def encolar(self, tarea: TareaRecordatorio) -> None:
        self.commits_al_encolar.append(self._uow_commits_fn())
        if self._fallar:
            raise ConnectionError("Redis no disponible (simulado)")
        self.encoladas.append(tarea)

    def desencolar(self) -> TareaRecordatorio | None:
        return self.encoladas.pop(0) if self.encoladas else None


class UoWConFalloEnCommit(UoWCrearTurno):
    def commit(self) -> None:
        raise RuntimeError("Fallo de commit en base de datos")


# Escenario: Encolar recordatorio al crear un turno válido (después del commit)
def test_crear_turno_encola_recordatorio_creado_despues_del_commit() -> None:
    uow = UoWCrearTurno()
    cola = ColaEspia(lambda: uow.commits)
    caso = CrearTurno(lambda: uow, reloj=lambda: AHORA, cola_recordatorios=cola)

    creado = caso.ejecutar(solicitud())

    assert cola.encoladas == [
        TareaRecordatorio(turno_id=creado.id, motivo=MotivoRecordatorio.CREADO)
    ]
    assert cola.commits_al_encolar == [1]


# Escenario: Encolar recordatorio al confirmar un turno programado (después del commit)
def test_confirmar_turno_encola_recordatorio_confirmado_despues_del_commit() -> None:
    uow = UoWCambioEstado([TURNO])
    cola = ColaEspia(lambda: uow.commits)
    caso = ConfirmarTurno(lambda: uow, reloj=lambda: AHORA, cola_recordatorios=cola)

    confirmado = caso.ejecutar(SolicitudCambioDeEstado(TURNO.id))

    assert confirmado.estado is EstadoTurno.CONFIRMADO
    assert cola.encoladas == [
        TareaRecordatorio(turno_id=TURNO.id, motivo=MotivoRecordatorio.CONFIRMADO)
    ]
    assert cola.commits_al_encolar == [1]


def test_cancelar_turno_no_encola_ningun_recordatorio() -> None:
    uow = UoWCambioEstado([TURNO])
    cola = ColaEspia(lambda: uow.commits)
    caso = CancelarTurno(lambda: uow, reloj=lambda: AHORA)

    cancelado = caso.ejecutar(SolicitudCambioDeEstado(TURNO.id))

    assert cancelado.estado is EstadoTurno.CANCELADO
    assert cola.encoladas == []


# Escenario: No encolar recordatorio si la creación o confirmación falla
def test_crear_turno_fallido_por_validacion_o_commit_no_encola_recordatorio() -> None:
    uow = UoWCrearTurno()
    cola = ColaEspia(lambda: uow.commits)
    caso = CrearTurno(lambda: uow, reloj=lambda: AHORA, cola_recordatorios=cola)

    with pytest.raises(RecursoInexistenteError):
        caso.ejecutar(solicitud(paciente_id="paciente-inexistente"))

    assert cola.encoladas == []

    uow_fallo = UoWConFalloEnCommit()
    cola_fallo = ColaEspia(lambda: uow_fallo.commits)
    caso_fallo = CrearTurno(lambda: uow_fallo, reloj=lambda: AHORA, cola_recordatorios=cola_fallo)

    with pytest.raises(RuntimeError):
        caso_fallo.ejecutar(solicitud())

    assert cola_fallo.encoladas == []


def test_confirmar_turno_fallido_no_encola_recordatorio() -> None:
    uow = UoWCambioEstado([TURNO.cancelar()])
    cola = ColaEspia(lambda: uow.commits)
    caso = ConfirmarTurno(lambda: uow, reloj=lambda: AHORA, cola_recordatorios=cola)

    with pytest.raises(TransicionInvalidaError):
        caso.ejecutar(SolicitudCambioDeEstado(TURNO.id))

    assert cola.encoladas == []


# Escenario: Crear turno y confirmar turno con Redis caído (RN-EX-02)
def test_crear_y_confirmar_turno_con_redis_caido_preserva_el_commit_sin_error() -> None:
    uow_crear = UoWCrearTurno()
    cola_caida_1 = ColaEspia(lambda: uow_crear.commits, fallar=True)
    caso_crear = CrearTurno(lambda: uow_crear, reloj=lambda: AHORA, cola_recordatorios=cola_caida_1)

    creado = caso_crear.ejecutar(solicitud())

    assert uow_crear.turnos.confirmados == [creado]
    assert uow_crear.commits == 1
    assert cola_caida_1.commits_al_encolar == [1]

    uow_confirmar = UoWCambioEstado([creado])
    cola_caida_2 = ColaEspia(lambda: uow_confirmar.commits, fallar=True)
    caso_confirmar = ConfirmarTurno(
        lambda: uow_confirmar, reloj=lambda: AHORA, cola_recordatorios=cola_caida_2
    )

    confirmado = caso_confirmar.ejecutar(SolicitudCambioDeEstado(creado.id))

    assert confirmado.estado is EstadoTurno.CONFIRMADO
    assert uow_confirmar.commits == 1
    assert cola_caida_2.commits_al_encolar == [1]
