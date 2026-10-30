from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from app.application.puertos import UnidadDeTrabajo
from app.domain.disponibilidad import verificar_bloqueos_de_turno, verificar_disponibilidad
from app.domain.turnos import (
    HistorialDeCambio,
    Prestacion,
    RecursoInexistenteError,
    TipoCambio,
    Turno,
    calcular_fin,
)


@dataclass(frozen=True)
class SolicitudCrearTurno:
    id: str
    paciente_id: str
    profesional_id: str
    box_id: str
    prestacion_id: str
    inicio: datetime
    fin: datetime | None = None


class CrearTurno:
    def __init__(self, unidad_de_trabajo: Callable[[], UnidadDeTrabajo], reloj: Callable[[], datetime]) -> None:
        self._unidad_de_trabajo = unidad_de_trabajo
        self._reloj = reloj

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
            uow.historiales.agregar(HistorialDeCambio(candidato.id, TipoCambio.CREADO, self._reloj()))
            uow.commit()
            return candidato

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
