"""Regla anti-solapamiento con intervalos semiabiertos [inicio, fin)."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from app.domain.bloqueos import BloqueoDeDisponibilidad
from app.domain.turnos import ErrorDeDominio


class ConflictoProfesionalError(ErrorDeDominio):
    codigo = "conflicto_profesional"

    def __init__(self) -> None:
        super().__init__("El profesional ya tiene un turno activo en ese intervalo.")


class ConflictoBoxError(ErrorDeDominio):
    codigo = "conflicto_box"

    def __init__(self) -> None:
        super().__init__("El box ya tiene un turno activo en ese intervalo.")


class ConflictoTurnoExistenteError(ErrorDeDominio):
    codigo = "conflicto_turno_existente"

    def __init__(self) -> None:
        super().__init__("El recurso tiene un turno activo en ese intervalo.")


class ConflictoBloqueoProfesionalError(ErrorDeDominio):
    codigo = "conflicto_bloqueo_profesional"

    def __init__(self) -> None:
        super().__init__("El profesional tiene un bloqueo en ese intervalo.")


class ConflictoBloqueoBoxError(ErrorDeDominio):
    codigo = "conflicto_bloqueo_box"

    def __init__(self) -> None:
        super().__init__("El box tiene un bloqueo en ese intervalo.")


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


def verificar_turnos_para_bloqueo(bloqueo: BloqueoDeDisponibilidad, activos: Iterable[Reservable]) -> None:
    """Un bloqueo no puede desplazar un turno existente del recurso afectado."""
    if any(
        se_solapan(bloqueo, turno)
        and (bloqueo.profesional_id == turno.profesional_id if bloqueo.profesional_id is not None
             else bloqueo.box_id == turno.box_id)
        for turno in activos
    ):
        raise ConflictoTurnoExistenteError()


def verificar_bloqueos_de_turno(candidato: Reservable, bloqueos: Iterable[BloqueoDeDisponibilidad]) -> None:
    """Prioridad profesional → box, igual que para conflictos entre turnos."""
    bloqueos = list(bloqueos)
    if any(b.profesional_id == candidato.profesional_id and se_solapan(candidato, b)
           for b in bloqueos if b.profesional_id is not None):
        raise ConflictoBloqueoProfesionalError()
    if any(b.box_id == candidato.box_id and se_solapan(candidato, b)
           for b in bloqueos if b.box_id is not None):
        raise ConflictoBloqueoBoxError()
