"""Caso de uso de registro de un bloqueo de disponibilidad."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from app.application.puertos import UnidadDeTrabajo
from app.domain.bloqueos import BloqueoDeDisponibilidad
from app.domain.disponibilidad import verificar_turnos_para_bloqueo
from app.domain.turnos import RecursoInexistenteError


@dataclass(frozen=True)
class SolicitudCrearBloqueo:
    id: str
    profesional_id: str | None
    box_id: str | None
    inicio: datetime
    fin: datetime
    motivo: str | None = None


class CrearBloqueo:
    def __init__(self, unidad_de_trabajo: Callable[[], UnidadDeTrabajo]) -> None:
        self._unidad_de_trabajo = unidad_de_trabajo

    def ejecutar(self, solicitud: SolicitudCrearBloqueo) -> BloqueoDeDisponibilidad:
        bloqueo = BloqueoDeDisponibilidad(
            id=solicitud.id,
            profesional_id=solicitud.profesional_id,
            box_id=solicitud.box_id,
            inicio=solicitud.inicio,
            fin=solicitud.fin,
            motivo=solicitud.motivo,
        )
        with self._unidad_de_trabajo() as uow:
            if bloqueo.profesional_id is not None:
                if uow.recursos.profesional(bloqueo.profesional_id) is None:
                    raise RecursoInexistenteError("profesional", bloqueo.profesional_id)
            elif bloqueo.box_id is not None and uow.recursos.box(bloqueo.box_id) is None:
                raise RecursoInexistenteError("box", bloqueo.box_id)

            uow.recursos.bloquear(bloqueo.profesional_id, bloqueo.box_id)
            activos = uow.turnos.activos_del_recurso_que_se_solapan(
                bloqueo.profesional_id, bloqueo.box_id, bloqueo.inicio, bloqueo.fin
            )
            verificar_turnos_para_bloqueo(bloqueo, activos)
            uow.bloqueos.agregar(bloqueo)
            uow.commit()
            return bloqueo
