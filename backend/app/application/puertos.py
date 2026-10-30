"""Puertos que el caso de uso necesita. Los implementa la infraestructura (SQLAlchemy) o los tests."""

from datetime import datetime
from types import TracebackType
from typing import Protocol, Self

from app.domain.bloqueos import BloqueoDeDisponibilidad
from app.domain.turnos import Box, HistorialDeCambio, Paciente, Prestacion, Profesional, Turno


class RepositorioRecursos(Protocol):
    def paciente(self, id_: str) -> Paciente | None: ...

    def profesional(self, id_: str) -> Profesional | None: ...

    def box(self, id_: str) -> Box | None: ...

    def prestacion(self, id_: str) -> Prestacion | None: ...

    def bloquear(self, profesional_id: str | None, box_id: str | None) -> None:
        """Bloquea las filas de recursos hasta el fin de la transacción."""
        ...


class RepositorioTurnos(Protocol):
    def activos_que_se_solapan(
        self, profesional_id: str, box_id: str, inicio: datetime, fin: datetime
    ) -> list[Turno]:
        """Turnos activos del profesional o del box que intersectan [inicio, fin)."""
        ...

    def agregar(self, turno: Turno) -> None: ...

    def activos_del_recurso_que_se_solapan(
        self, profesional_id: str | None, box_id: str | None, inicio: datetime, fin: datetime
    ) -> list[Turno]:
        """Turnos activos del único recurso indicado que intersectan el intervalo."""
        ...


class RepositorioBloqueos(Protocol):
    def que_se_solapan(
        self, profesional_id: str, box_id: str, inicio: datetime, fin: datetime
    ) -> list[BloqueoDeDisponibilidad]: ...

    def agregar(self, bloqueo: BloqueoDeDisponibilidad) -> None: ...


class RepositorioHistoriales(Protocol):
    def agregar(self, historial: HistorialDeCambio) -> None: ...


class LectorAgenda(Protocol):
    def en_rango(
        self,
        inicio: datetime,
        fin: datetime,
        profesional_id: str | None = None,
        box_id: str | None = None,
    ) -> list[Turno]:
        """Turnos que intersectan [inicio, fin), filtrados opcionalmente y ordenados por inicio ascendente."""
        ...


class UnidadDeTrabajo(Protocol):
    """Transacción: lo agregado sólo se persiste con `commit`; salir sin commit descarta todo."""

    recursos: RepositorioRecursos
    turnos: RepositorioTurnos
    historiales: RepositorioHistoriales
    bloqueos: RepositorioBloqueos

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        tipo: type[BaseException] | None,
        error: BaseException | None,
        traza: TracebackType | None,
    ) -> None: ...

    def commit(self) -> None: ...
