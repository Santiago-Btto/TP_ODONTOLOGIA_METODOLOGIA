"""Implementación SQLAlchemy de los puertos de aplicación."""

from collections.abc import Callable
from datetime import datetime
from types import TracebackType
from typing import Self

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.domain.disponibilidad import ConflictoBoxError, ConflictoProfesionalError
from app.domain.turnos import (
    Box,
    EstadoTurno,
    HistorialDeCambio,
    Paciente,
    Prestacion,
    Profesional,
    Turno,
)
from app.infrastructure.modelos import (
    RESTRICCION_BOX,
    RESTRICCION_PROFESIONAL,
    BoxModelo,
    HistorialModelo,
    PacienteModelo,
    PrestacionModelo,
    ProfesionalModelo,
    TurnoModelo,
)


class RecursosSQLAlchemy:
    def __init__(self, sesion: Session) -> None:
        self._sesion = sesion

    def paciente(self, id_: str) -> Paciente | None:
        fila = self._sesion.get(PacienteModelo, id_)
        return None if fila is None else Paciente(fila.id, fila.nombre_mostrado)

    def profesional(self, id_: str) -> Profesional | None:
        fila = self._sesion.get(ProfesionalModelo, id_)
        return None if fila is None else Profesional(fila.id, fila.nombre_mostrado, fila.activo)

    def box(self, id_: str) -> Box | None:
        fila = self._sesion.get(BoxModelo, id_)
        return None if fila is None else Box(fila.id, fila.nombre, fila.activo)

    def prestacion(self, id_: str) -> Prestacion | None:
        fila = self._sesion.get(PrestacionModelo, id_)
        return None if fila is None else Prestacion(fila.id, fila.nombre, fila.duracion_minutos)


class TurnosSQLAlchemy:
    def __init__(self, sesion: Session) -> None:
        self._sesion = sesion

    def activos_que_se_solapan(
        self, profesional_id: str, box_id: str, inicio: datetime, fin: datetime
    ) -> list[Turno]:
        consulta = select(TurnoModelo).where(
            TurnoModelo.estado != "cancelado",
            or_(TurnoModelo.profesional_id == profesional_id, TurnoModelo.box_id == box_id),
            TurnoModelo.inicio < fin,
            inicio < TurnoModelo.fin,
        )
        return [_a_dominio(fila) for fila in self._sesion.scalars(consulta)]

    def agregar(self, turno: Turno) -> None:
        self._sesion.add(
            TurnoModelo(
                id=turno.id,
                paciente_id=turno.paciente_id,
                profesional_id=turno.profesional_id,
                box_id=turno.box_id,
                prestacion_id=turno.prestacion_id,
                inicio=turno.inicio,
                fin=turno.fin,
                estado=turno.estado.value,
            )
        )
        # Sin relación ORM declarada, el turno debe existir antes de insertar su historial.
        # Si una restricción de exclusión lo rechaza, se informa como conflicto de dominio.
        _confirmar_o_traducir(self._sesion, self._sesion.flush)


class HistorialesSQLAlchemy:
    def __init__(self, sesion: Session) -> None:
        self._sesion = sesion

    def agregar(self, historial: HistorialDeCambio) -> None:
        self._sesion.add(
            HistorialModelo(turno_id=historial.turno_id, tipo=historial.tipo.value, ocurrido_en=historial.ocurrido_en)
        )


class UnidadDeTrabajoSQLAlchemy:
    def __init__(self, fabrica: sessionmaker[Session]) -> None:
        self._fabrica = fabrica

    def __enter__(self) -> Self:
        self._sesion = self._fabrica()
        self.recursos = RecursosSQLAlchemy(self._sesion)
        self.turnos = TurnosSQLAlchemy(self._sesion)
        self.historiales = HistorialesSQLAlchemy(self._sesion)
        return self

    def __exit__(
        self,
        tipo: type[BaseException] | None,
        error: BaseException | None,
        traza: TracebackType | None,
    ) -> None:
        self._sesion.rollback()
        self._sesion.close()

    def commit(self) -> None:
        _confirmar_o_traducir(self._sesion, self._sesion.commit)


class LectorAgendaSQLAlchemy:
    def __init__(self, fabrica: sessionmaker[Session]) -> None:
        self._fabrica = fabrica

    def en_rango(
        self,
        inicio: datetime,
        fin: datetime,
        profesional_id: str | None = None,
        box_id: str | None = None,
    ) -> list[Turno]:
        consulta = select(TurnoModelo).where(
            TurnoModelo.inicio < fin,
            TurnoModelo.fin > inicio,
        )
        if profesional_id is not None:
            consulta = consulta.where(TurnoModelo.profesional_id == profesional_id)
        if box_id is not None:
            consulta = consulta.where(TurnoModelo.box_id == box_id)
        consulta = consulta.order_by(TurnoModelo.inicio.asc())
        with self._fabrica() as sesion:
            return [_a_dominio(fila) for fila in sesion.scalars(consulta)]


def _confirmar_o_traducir(sesion: Session, operacion: Callable[[], None]) -> None:
    try:
        operacion()
    except IntegrityError as error:
        sesion.rollback()
        raise _traducir(error) from error


def _traducir(error: IntegrityError) -> Exception:
    diag = getattr(error.orig, "diag", None)
    restriccion = getattr(diag, "constraint_name", None)
    if restriccion == RESTRICCION_PROFESIONAL:
        return ConflictoProfesionalError()
    if restriccion == RESTRICCION_BOX:
        return ConflictoBoxError()
    return error


def _a_dominio(fila: TurnoModelo) -> Turno:
    return Turno(
        id=fila.id,
        paciente_id=fila.paciente_id,
        profesional_id=fila.profesional_id,
        box_id=fila.box_id,
        prestacion_id=fila.prestacion_id,
        inicio=fila.inicio,
        fin=fila.fin,
        estado=EstadoTurno(fila.estado),
    )
