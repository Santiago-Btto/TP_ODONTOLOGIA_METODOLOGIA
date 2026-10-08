"""Regla anti-solapamiento con intervalos semiabiertos [inicio, fin)."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from app.domain.turnos import ErrorDeDominio


class ConflictoProfesionalError(ErrorDeDominio):
    codigo = "conflicto_profesional"

    def __init__(self) -> None:
        super().__init__("El profesional ya tiene un turno activo en ese intervalo.")


class ConflictoBoxError(ErrorDeDominio):
    codigo = "conflicto_box"

    def __init__(self) -> None:
        super().__init__("El box ya tiene un turno activo en ese intervalo.")


class ConIntervalo(Protocol):
    @property
    def inicio(self) -> datetime: ...

    @property
    def fin(self) -> datetime: ...


class Reservable(ConIntervalo, Protocol):
    @property
    def profesional_id(self) -> str: ...

    @property
    def box_id(self) -> str: ...


@dataclass(frozen=True)
class Intervalo:
    inicio: datetime
    fin: datetime


def se_solapan(a: ConIntervalo, b: ConIntervalo) -> bool:
    return a.inicio < b.fin and b.inicio < a.fin


def verificar_disponibilidad(candidato: Reservable, activos: Iterable[Reservable]) -> None:
    activos = list(activos)
    if any(t.profesional_id == candidato.profesional_id and se_solapan(candidato, t) for t in activos):
        raise ConflictoProfesionalError()
    if any(t.box_id == candidato.box_id and se_solapan(candidato, t) for t in activos):
        raise ConflictoBoxError()
