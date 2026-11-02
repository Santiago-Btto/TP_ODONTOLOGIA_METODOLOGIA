"""Casos de uso de confirmación y cancelación de turnos (C-05, C-16)."""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from app.application.puertos import ColaRecordatorios, ColaRecordatoriosNoOp, UnidadDeTrabajo
from app.domain.recordatorios import MotivoRecordatorio, TareaRecordatorio
from app.domain.turnos import HistorialDeCambio, RecursoInexistenteError, TipoCambio, Turno

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SolicitudCambioDeEstado:
    turno_id: str
    actor_id: str | None = None


class _CambiarEstadoTurno:
    """Bloquea la fila del turno, aplica la transición del dominio y guarda turno + historial juntos."""

    _tipo: TipoCambio

    def __init__(self, unidad_de_trabajo: Callable[[], UnidadDeTrabajo], reloj: Callable[[], datetime]) -> None:
        self._unidad_de_trabajo = unidad_de_trabajo
        self._reloj = reloj

    def ejecutar(self, solicitud: SolicitudCambioDeEstado) -> Turno:
        with self._unidad_de_trabajo() as uow:
            actual = uow.turnos.obtener_para_actualizar(solicitud.turno_id)
            if actual is None:
                raise RecursoInexistenteError("turno", solicitud.turno_id)
            nuevo = self._transicionar(actual)
            uow.turnos.actualizar(nuevo)
            uow.historiales.agregar(
                HistorialDeCambio(nuevo.id, self._tipo, self._reloj(), actor_id=solicitud.actor_id)
            )
            uow.commit()
            return nuevo

    def _transicionar(self, turno: Turno) -> Turno:
        raise NotImplementedError


class ConfirmarTurno(_CambiarEstadoTurno):
    _tipo = TipoCambio.CONFIRMADO

    def __init__(
        self,
        unidad_de_trabajo: Callable[[], UnidadDeTrabajo],
        reloj: Callable[[], datetime],
        cola_recordatorios: ColaRecordatorios = ColaRecordatoriosNoOp(),
    ) -> None:
        super().__init__(unidad_de_trabajo, reloj)
        self._cola_recordatorios = cola_recordatorios

    def ejecutar(self, solicitud: SolicitudCambioDeEstado) -> Turno:
        confirmado = super().ejecutar(solicitud)
        try:
            self._cola_recordatorios.encolar(
                TareaRecordatorio(turno_id=confirmado.id, motivo=MotivoRecordatorio.CONFIRMADO)
            )
        except Exception:
            logger.warning(
                "No se pudo encolar el recordatorio de confirmación para el turno '%s' (RN-EX-02).",
                confirmado.id,
                exc_info=True,
            )
        return confirmado

    def _transicionar(self, turno: Turno) -> Turno:
        return turno.confirmar()


class CancelarTurno(_CambiarEstadoTurno):
    _tipo = TipoCambio.CANCELADO

    def _transicionar(self, turno: Turno) -> Turno:
        return turno.cancelar()
