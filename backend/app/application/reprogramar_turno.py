"""Caso de uso de reprogramación atómica de un turno (C-04)."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from app.application.puertos import UnidadDeTrabajo
from app.domain.disponibilidad import verificar_bloqueos_de_turno, verificar_disponibilidad
from app.domain.turnos import HistorialDeCambio, RecursoInexistenteError, ResumenTurno, TipoCambio, Turno


@dataclass(frozen=True)
class SolicitudReprogramarTurno:
    turno_id: str
    inicio: datetime | None = None
    fin: datetime | None = None
    profesional_id: str | None = None
    box_id: str | None = None


class ReprogramarTurno:
    """Orden de bloqueos: fila del turno → profesional → box de destino; luego lectura de conflictos.

    Ante cualquier error, la unidad de trabajo descarta todo: el intervalo anterior sólo se libera
    al confirmar un cambio válido (RN-TU-02).
    """

    def __init__(self, unidad_de_trabajo: Callable[[], UnidadDeTrabajo], reloj: Callable[[], datetime]) -> None:
        self._unidad_de_trabajo = unidad_de_trabajo
        self._reloj = reloj

    def ejecutar(self, solicitud: SolicitudReprogramarTurno) -> Turno:
        with self._unidad_de_trabajo() as uow:
            actual = uow.turnos.obtener_para_actualizar(solicitud.turno_id)
            if actual is None:
                raise RecursoInexistenteError("turno", solicitud.turno_id)
            if solicitud.profesional_id is not None and uow.recursos.profesional(solicitud.profesional_id) is None:
                raise RecursoInexistenteError("profesional", solicitud.profesional_id)
            if solicitud.box_id is not None and uow.recursos.box(solicitud.box_id) is None:
                raise RecursoInexistenteError("box", solicitud.box_id)

            candidato = actual.reprogramar(
                inicio=solicitud.inicio,
                fin=solicitud.fin,
                profesional_id=solicitud.profesional_id,
                box_id=solicitud.box_id,
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

            uow.turnos.actualizar(candidato)
            uow.historiales.agregar(HistorialDeCambio(
                candidato.id, TipoCambio.REPROGRAMADO, self._reloj(),
                antes=ResumenTurno.de(actual), despues=ResumenTurno.de(candidato),
            ))
            uow.commit()
            return candidato
