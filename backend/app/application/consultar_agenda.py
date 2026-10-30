"""Caso de uso de consulta de agenda por intervalo temporal y filtros opcionales."""

from dataclasses import dataclass
from datetime import UTC, datetime

from app.application.puertos import LectorAgenda
from app.domain.turnos import IntervaloInvalidoError, Turno


def _normalizar_utc(instante: datetime) -> datetime:
    if instante.tzinfo is None or instante.utcoffset() is None:
        raise IntervaloInvalidoError()
    return instante.astimezone(UTC)


@dataclass(frozen=True)
class SolicitudConsultarAgenda:
    inicio: datetime
    fin: datetime
    profesional_id: str | None = None
    box_id: str | None = None


class ConsultarAgenda:
    def __init__(self, lector: LectorAgenda) -> None:
        self._lector = lector

    def ejecutar(self, solicitud: SolicitudConsultarAgenda) -> list[Turno]:
        inicio = _normalizar_utc(solicitud.inicio)
        fin = _normalizar_utc(solicitud.fin)
        if fin <= inicio:
            raise IntervaloInvalidoError()
        return self._lector.en_rango(
            inicio=inicio,
            fin=fin,
            profesional_id=solicitud.profesional_id,
            box_id=solicitud.box_id,
        )
