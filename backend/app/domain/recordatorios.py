"""Entidades y valores de dominio para recordatorios simulados de turnos (C-16).

Python puro: sin dependencias de FastAPI, SQLAlchemy ni Redis.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.domain.turnos import ErrorDeDominio


class TurnoRecordatorioInvalidoError(ErrorDeDominio):
    codigo = "turno_recordatorio_invalido"

    def __init__(self) -> None:
        super().__init__("El identificador del turno del recordatorio no puede estar vacío.")


class MotivoRecordatorio(StrEnum):
    CREADO = "creado"
    CONFIRMADO = "confirmado"


@dataclass(frozen=True)
class TareaRecordatorio:
    """Tarea encolada tras confirmar la creación o confirmación de un turno."""

    turno_id: str
    motivo: MotivoRecordatorio

    def __post_init__(self) -> None:
        if not self.turno_id or not self.turno_id.strip():
            raise TurnoRecordatorioInvalidoError()


@dataclass(frozen=True)
class RecordatorioEnviado:
    """Registro de un recordatorio simulado procesado por el worker."""

    turno_id: str
    motivo: MotivoRecordatorio
    destinatario: str
    enviado_en: datetime
    id: int | None = None
