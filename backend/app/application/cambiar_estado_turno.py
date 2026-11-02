"""Casos de uso de confirmación y cancelación de turnos (C-05)."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from app.application.puertos import UnidadDeTrabajo
from app.domain.turnos import HistorialDeCambio, RecursoInexistenteError, TipoCambio, Turno


@dataclass(frozen=True)
class SolicitudCambioDeEstado:
    turno_id: str


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
            uow.historiales.agregar(HistorialDeCambio(nuevo.id, self._tipo, self._reloj()))
            uow.commit()
            return nuevo

    def _transicionar(self, turno: Turno) -> Turno:
        raise NotImplementedError


class ConfirmarTurno(_CambiarEstadoTurno):
    _tipo = TipoCambio.CONFIRMADO

    def _transicionar(self, turno: Turno) -> Turno:
        return turno.confirmar()


class CancelarTurno(_CambiarEstadoTurno):
    _tipo = TipoCambio.CANCELADO

    def _transicionar(self, turno: Turno) -> Turno:
        return turno.cancelar()
