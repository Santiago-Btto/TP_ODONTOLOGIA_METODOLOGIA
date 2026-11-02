"""Casos de uso de procesamiento y consulta de recordatorios simulados (C-16)."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from app.application.puertos import (
    ColaRecordatorios,
    NotificadorRecordatorios,
    UnidadDeTrabajo,
)
from app.domain.recordatorios import RecordatorioEnviado
from app.domain.turnos import Paciente, RecursoInexistenteError


@dataclass(frozen=True)
class ResultadoProcesamientoRecordatorio:
    procesada: bool
    enviado: bool
    recordatorio: RecordatorioEnviado | None = None


class ProcesarSiguienteRecordatorio:
    """Desencola una tarea de recordatorio, verifica estado e idempotencia y registra el envío simulado."""

    def __init__(
        self,
        unidad_de_trabajo: Callable[[], UnidadDeTrabajo],
        cola_recordatorios: ColaRecordatorios,
        notificador: NotificadorRecordatorios,
        reloj: Callable[[], datetime],
    ) -> None:
        self._unidad_de_trabajo = unidad_de_trabajo
        self._cola_recordatorios = cola_recordatorios
        self._notificador = notificador
        self._reloj = reloj

    def ejecutar(self) -> ResultadoProcesamientoRecordatorio:
        tarea = self._cola_recordatorios.desencolar()
        if tarea is None:
            return ResultadoProcesamientoRecordatorio(procesada=False, enviado=False, recordatorio=None)

        with self._unidad_de_trabajo() as uow:
            turno = uow.turnos.obtener(tarea.turno_id)
            if turno is None or not turno.activo:
                return ResultadoProcesamientoRecordatorio(procesada=True, enviado=False, recordatorio=None)

            existente = uow.recordatorios.obtener(tarea.turno_id, tarea.motivo)
            if existente is not None:
                return ResultadoProcesamientoRecordatorio(
                    procesada=True, enviado=False, recordatorio=existente
                )

            paciente = uow.recursos.paciente(turno.paciente_id) or Paciente(
                id=turno.paciente_id, nombre_mostrado=turno.paciente_id
            )
            envio = self._notificador.enviar_recordatorio(
                turno=turno,
                paciente=paciente,
                motivo=tarea.motivo,
                enviado_en=self._reloj(),
            )
            persistido = uow.recordatorios.agregar(envio)
            uow.commit()
            return ResultadoProcesamientoRecordatorio(
                procesada=True, enviado=True, recordatorio=persistido
            )


class ConsultarRecordatoriosTurno:
    """Devuelve los recordatorios simulados registrados para un turno existente."""

    def __init__(self, unidad_de_trabajo: Callable[[], UnidadDeTrabajo]) -> None:
        self._unidad_de_trabajo = unidad_de_trabajo

    def ejecutar(self, turno_id: str) -> list[RecordatorioEnviado]:
        with self._unidad_de_trabajo() as uow:
            turno = uow.turnos.obtener(turno_id)
            if turno is None:
                raise RecursoInexistenteError("turno", turno_id)
            return uow.recordatorios.listar_por_turno(turno_id)
