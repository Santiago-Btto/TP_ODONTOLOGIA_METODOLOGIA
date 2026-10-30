from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


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


class ErrorSalida(BaseModel):
    codigo: str
    detalle: str
