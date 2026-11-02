import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from app.application.puertos import ColaRecordatorios, ColaRecordatoriosNoOp, UnidadDeTrabajo
from app.domain.disponibilidad import verificar_bloqueos_de_turno, verificar_disponibilidad
from app.domain.recordatorios import MotivoRecordatorio, TareaRecordatorio
from app.domain.turnos import (
    HistorialDeCambio,
    Prestacion,
    RecursoInexistenteError,
    TipoCambio,
    Turno,
    calcular_fin,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SolicitudCrearTurno:
    id: str
    paciente_id: str
    profesional_id: str
    box_id: str
    prestacion_id: str
    inicio: datetime
    fin: datetime | None = None
    actor_id: str | None = None


class CrearTurno:
    def __init__(
        self,
        unidad_de_trabajo: Callable[[], UnidadDeTrabajo],
        reloj: Callable[[], datetime],
        cola_recordatorios: ColaRecordatorios = ColaRecordatoriosNoOp(),
    ) -> None:
        self._unidad_de_trabajo = unidad_de_trabajo
        self._reloj = reloj
        self._cola_recordatorios = cola_recordatorios

    def ejecutar(self, solicitud: SolicitudCrearTurno) -> Turno:
        with self._unidad_de_trabajo() as uow:
            prestacion = self._verificar_recursos(uow, solicitud)
            fin_por_prestacion = calcular_fin(solicitud.inicio, prestacion)
            candidato = Turno(
                id=solicitud.id,
                paciente_id=solicitud.paciente_id,
                profesional_id=solicitud.profesional_id,
                box_id=solicitud.box_id,
                prestacion_id=prestacion.id,
                inicio=solicitud.inicio,
                fin=solicitud.fin if solicitud.fin is not None else fin_por_prestacion,
            )
            uow.recursos.bloquear(candidato.profesional_id, candidato.box_id)
            activos = uow.turnos.activos_que_se_solapan(
                candidato.profesional_id, candidato.box_id, candidato.inicio, candidato.fin
            )
            verificar_disponibilidad(candidato, activos)
            bloqueos = uow.bloqueos.que_se_solapan(
                candidato.profesional_id, candidato.box_id, candidato.inicio, candidato.fin
            )
            verificar_bloqueos_de_turno(candidato, bloqueos)

            uow.turnos.agregar(candidato)
            uow.historiales.agregar(
                HistorialDeCambio(candidato.id, TipoCambio.CREADO, self._reloj(), actor_id=solicitud.actor_id)
            )
            uow.commit()

        self._encolar_recordatorio_seguro(candidato.id)
        return candidato

    def _encolar_recordatorio_seguro(self, turno_id: str) -> None:
        try:
            self._cola_recordatorios.encolar(
                TareaRecordatorio(turno_id=turno_id, motivo=MotivoRecordatorio.CREADO)
            )
        except Exception:
            logger.warning(
                "No se pudo encolar el recordatorio de creación para el turno '%s' (RN-EX-02).",
                turno_id,
                exc_info=True,
            )

    @staticmethod
    def _verificar_recursos(uow: UnidadDeTrabajo, solicitud: SolicitudCrearTurno) -> Prestacion:
        if uow.recursos.paciente(solicitud.paciente_id) is None:
            raise RecursoInexistenteError("paciente", solicitud.paciente_id)
        if uow.recursos.profesional(solicitud.profesional_id) is None:
            raise RecursoInexistenteError("profesional", solicitud.profesional_id)
        if uow.recursos.box(solicitud.box_id) is None:
            raise RecursoInexistenteError("box", solicitud.box_id)
        prestacion = uow.recursos.prestacion(solicitud.prestacion_id)
        if prestacion is None:
            raise RecursoInexistenteError("prestación", solicitud.prestacion_id)
        return prestacion
