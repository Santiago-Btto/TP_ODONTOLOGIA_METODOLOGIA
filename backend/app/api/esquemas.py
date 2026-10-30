from typing import Self

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator


class TurnoEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    paciente_id: str = Field(min_length=1, max_length=64)
    profesional_id: str = Field(min_length=1, max_length=64)
    box_id: str = Field(min_length=1, max_length=64)
    prestacion_id: str = Field(min_length=1, max_length=64)
    inicio: AwareDatetime
    fin: AwareDatetime | None = None


class TurnoSalida(BaseModel):
    id: str
    paciente_id: str
    profesional_id: str
    box_id: str
    prestacion_id: str
    inicio: AwareDatetime
    fin: AwareDatetime
    estado: str


class TurnoAgendaSalida(BaseModel):
    id: str
    profesional_id: str
    box_id: str
    inicio: AwareDatetime
    fin: AwareDatetime


class BloqueoEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profesional_id: str | None = Field(default=None, min_length=1, max_length=64)
    box_id: str | None = Field(default=None, min_length=1, max_length=64)
    inicio: AwareDatetime
    fin: AwareDatetime
    motivo: str | None = None

    @model_validator(mode="after")
    def validar_recurso_e_intervalo(self) -> Self:
        if (self.profesional_id is None) == (self.box_id is None):
            raise ValueError("Indicar exactamente un profesional o un box.")
        if self.fin <= self.inicio:
            raise ValueError("El fin debe ser posterior al inicio.")
        return self


class BloqueoSalida(BaseModel):
    id: str
    profesional_id: str | None
    box_id: str | None
    inicio: AwareDatetime
    fin: AwareDatetime
    motivo: str | None


class ErrorSalida(BaseModel):
    codigo: str
    detalle: str
