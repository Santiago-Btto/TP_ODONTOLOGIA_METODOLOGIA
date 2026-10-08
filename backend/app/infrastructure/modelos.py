"""Modelos SQLAlchemy y restricciones de PostgreSQL."""

from datetime import datetime

from sqlalchemy import (
    DDL,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    String,
    event,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

RESTRICCION_PROFESIONAL = "turnos_sin_solapamiento_profesional"
RESTRICCION_BOX = "turnos_sin_solapamiento_box"


class Base(DeclarativeBase):
    pass


class PacienteModelo(Base):
    __tablename__ = "pacientes"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    nombre_mostrado: Mapped[str] = mapped_column(String(200))


class ProfesionalModelo(Base):
    __tablename__ = "profesionales"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    nombre_mostrado: Mapped[str] = mapped_column(String(200))
    activo: Mapped[bool] = mapped_column(default=True)


class BoxModelo(Base):
    __tablename__ = "boxes"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100))
    activo: Mapped[bool] = mapped_column(default=True)


class PrestacionModelo(Base):
    __tablename__ = "prestaciones"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200))
    duracion_minutos: Mapped[int] = mapped_column(Integer)


class TurnoModelo(Base):
    __tablename__ = "turnos"
    __table_args__ = (CheckConstraint("fin > inicio", name="turnos_fin_posterior_al_inicio"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    paciente_id: Mapped[str] = mapped_column(ForeignKey("pacientes.id"))
    profesional_id: Mapped[str] = mapped_column(ForeignKey("profesionales.id"), index=True)
    box_id: Mapped[str] = mapped_column(ForeignKey("boxes.id"), index=True)
    prestacion_id: Mapped[str] = mapped_column(ForeignKey("prestaciones.id"))
    inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fin: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    estado: Mapped[str] = mapped_column(String(20))


class HistorialModelo(Base):
    __tablename__ = "historial_cambios"

    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    turno_id: Mapped[str] = mapped_column(ForeignKey("turnos.id"), index=True)
    tipo: Mapped[str] = mapped_column(String(20))
    ocurrido_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))


event.listen(Base.metadata, "before_create", DDL("CREATE EXTENSION IF NOT EXISTS btree_gist"))

for _nombre, _columna in ((RESTRICCION_PROFESIONAL, "profesional_id"), (RESTRICCION_BOX, "box_id")):
    event.listen(
        TurnoModelo.__table__,
        "after_create",
        DDL(
            f"ALTER TABLE turnos ADD CONSTRAINT {_nombre} "
            f"EXCLUDE USING gist ({_columna} WITH =, tstzrange(inicio, fin, '[)') WITH &&) "
            "WHERE (estado <> 'cancelado')"
        ),
    )
