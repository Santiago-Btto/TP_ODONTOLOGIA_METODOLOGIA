"""Entidades y errores del dominio de turnos. Python puro: sin FastAPI ni SQLAlchemy."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum


class ErrorDeDominio(Exception):
    """Base de los errores de negocio; `codigo` es estable y lo usa la API."""

    codigo = "error_de_dominio"


class IntervaloInvalidoError(ErrorDeDominio):
    codigo = "intervalo_invalido"

    def __init__(self) -> None:
        super().__init__("El fin del turno debe ser posterior al inicio.")


class DuracionInvalidaError(ErrorDeDominio):
    codigo = "duracion_invalida"

    def __init__(self) -> None:
        super().__init__("La duración de la prestación debe ser positiva.")


class RecursoInexistenteError(ErrorDeDominio):
    codigo = "recurso_inexistente"

    def __init__(self, tipo: str, recurso_id: str) -> None:
        super().__init__(f"No existe {tipo} con id '{recurso_id}'.")
        self.tipo = tipo
        self.recurso_id = recurso_id


class EstadoTurno(StrEnum):
    PROGRAMADO = "programado"


class TipoCambio(StrEnum):
    CREADO = "creado"


@dataclass(frozen=True)
class Paciente:
    id: str
    nombre_mostrado: str


@dataclass(frozen=True)
class Profesional:
    id: str
    nombre_mostrado: str
    activo: bool = True


@dataclass(frozen=True)
class Box:
    id: str
    nombre: str
    activo: bool = True


@dataclass(frozen=True)
class Prestacion:
    id: str
    nombre: str
    duracion_minutos: int


@dataclass(frozen=True)
class Turno:
    id: str
    paciente_id: str
    profesional_id: str
    box_id: str
    prestacion_id: str
    inicio: datetime
    fin: datetime
    estado: EstadoTurno = EstadoTurno.PROGRAMADO

    def __post_init__(self) -> None:
        if self.fin <= self.inicio:
            raise IntervaloInvalidoError()


@dataclass(frozen=True)
class HistorialDeCambio:
    turno_id: str
    tipo: TipoCambio
    ocurrido_en: datetime


def calcular_fin(inicio: datetime, prestacion: Prestacion) -> datetime:
    if prestacion.duracion_minutos <= 0:
        raise DuracionInvalidaError()
    return inicio + timedelta(minutes=prestacion.duracion_minutos)
