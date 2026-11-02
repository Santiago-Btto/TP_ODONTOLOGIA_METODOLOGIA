"""Autorización por rol (C-08). Matriz *propuesta* en la KB: se ajusta aquí cuando se valide.

Python puro: sin FastAPI, SQLAlchemy ni detalles de tokens.
"""

from dataclasses import dataclass
from enum import StrEnum

from app.domain.turnos import ErrorDeDominio


class Rol(StrEnum):
    RECEPCION = "recepcion"
    ODONTOLOGO = "odontologo"
    RESPONSABLE = "responsable"


class Permiso(StrEnum):
    CREAR_TURNO = "crear_turno"
    REPROGRAMAR_TURNO = "reprogramar_turno"
    CONFIRMAR_TURNO = "confirmar_turno"
    CANCELAR_TURNO = "cancelar_turno"
    CREAR_BLOQUEO = "crear_bloqueo"
    CONSULTAR_AGENDA = "consultar_agenda"
    CONSULTAR_RECORDATORIOS = "consultar_recordatorios"


PERMISOS_POR_ROL: dict[Rol, frozenset[Permiso]] = {
    Rol.RECEPCION: frozenset(Permiso),
    Rol.RESPONSABLE: frozenset(Permiso),
    # “Agenda propia: consultar; cambios pendientes de definición” (03_actores_y_roles.md).
    Rol.ODONTOLOGO: frozenset({Permiso.CONSULTAR_AGENDA}),
}


class AccesoDenegadoError(ErrorDeDominio):
    codigo = "acceso_denegado"

    def __init__(self, detalle: str = "El rol del usuario no permite esta operación.") -> None:
        super().__init__(detalle)


@dataclass(frozen=True)
class Actor:
    """Usuario autenticado que ejecuta una operación."""

    id: str
    rol: Rol
    profesional_id: str | None = None


@dataclass(frozen=True)
class Usuario:
    id: str
    nombre_usuario: str
    hash_contrasena: str
    rol: Rol
    profesional_id: str | None = None
    activo: bool = True

    def como_actor(self) -> Actor:
        return Actor(self.id, self.rol, self.profesional_id)


def verificar_permiso(actor: Actor, permiso: Permiso) -> None:
    if permiso not in PERMISOS_POR_ROL[actor.rol]:
        raise AccesoDenegadoError()


def verificar_alcance_agenda(actor: Actor, profesional_id: str | None) -> None:
    """El odontólogo/a sólo consulta la agenda del profesional vinculado a su usuario."""
    verificar_permiso(actor, Permiso.CONSULTAR_AGENDA)
    if actor.rol is Rol.ODONTOLOGO and (actor.profesional_id is None or profesional_id != actor.profesional_id):
        raise AccesoDenegadoError("Un odontólogo/a sólo puede consultar su propia agenda (filtrar por su profesional).")
