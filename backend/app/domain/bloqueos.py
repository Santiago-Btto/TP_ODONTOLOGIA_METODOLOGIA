"""Bloqueos de disponibilidad: reglas de entrada sin dependencias de infraestructura."""

from dataclasses import dataclass
from datetime import datetime

from app.domain.turnos import ErrorDeDominio, IntervaloInvalidoError


class RecursoDeBloqueoInvalidoError(ErrorDeDominio):
    codigo = "recurso_bloqueo_invalido"

    def __init__(self) -> None:
        super().__init__("Un bloqueo debe indicar exactamente un profesional o un box.")


class FechaSinZonaError(ErrorDeDominio, ValueError):
    codigo = "fecha_sin_zona"

    def __init__(self) -> None:
        super().__init__("El inicio y fin del bloqueo deben incluir zona horaria.")


class IntervaloBloqueoInvalidoError(IntervaloInvalidoError):
    def __init__(self) -> None:
        ErrorDeDominio.__init__(self, "El fin del bloqueo debe ser posterior al inicio.")


@dataclass(frozen=True)
class BloqueoDeDisponibilidad:
    id: str
    profesional_id: str | None
    box_id: str | None
    inicio: datetime
    fin: datetime
    motivo: str | None = None

    def __post_init__(self) -> None:
        if ((self.profesional_id is None) == (self.box_id is None)
                or self.profesional_id == "" or self.box_id == ""):
            raise RecursoDeBloqueoInvalidoError()
        if any(fecha.tzinfo is None or fecha.utcoffset() is None for fecha in (self.inicio, self.fin)):
            raise FechaSinZonaError()
        if self.fin <= self.inicio:
            raise IntervaloBloqueoInvalidoError()
