"""Entidades y errores del dominio de turnos. Python puro: sin FastAPI ni SQLAlchemy."""

from dataclasses import dataclass, replace
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


class DatosPacienteInvalidosError(ErrorDeDominio):
    codigo = "datos_paciente_invalidos"

    def __init__(self, detalle: str = "El identificador y el nombre mostrado del paciente son obligatorios.") -> None:
        super().__init__(detalle)


class PacienteDuplicadoError(ErrorDeDominio):
    codigo = "paciente_duplicado"

    def __init__(self, detalle: str = "Ya existe un paciente registrado con los mismos datos únicos.") -> None:
        super().__init__(detalle)


class EstadoTurno(StrEnum):
    PROGRAMADO = "programado"
    CONFIRMADO = "confirmado"
    CANCELADO = "cancelado"


class TipoCambio(StrEnum):
    CREADO = "creado"
    CONFIRMADO = "confirmado"
    CANCELADO = "cancelado"
    REPROGRAMADO = "reprogramado"


class ReprogramacionSinCambiosError(ErrorDeDominio):
    codigo = "reprogramacion_sin_cambios"

    def __init__(self) -> None:
        super().__init__("La reprogramación no cambia horario ni recursos del turno.")


class TransicionInvalidaError(ErrorDeDominio):
    codigo = "transicion_invalida"

    def __init__(self, estado: "EstadoTurno", accion: str) -> None:
        super().__init__(f"No se puede {accion} un turno en estado '{estado.value}'.")
        self.estado = estado
        self.accion = accion


# Máquina de estados (C-05). Cancelar es terminal; confirmar dos veces no es idempotente.
_TRANSICIONES: dict[tuple["EstadoTurno", str], "EstadoTurno"] = {
    (EstadoTurno.PROGRAMADO, "confirmar"): EstadoTurno.CONFIRMADO,
    (EstadoTurno.PROGRAMADO, "cancelar"): EstadoTurno.CANCELADO,
    (EstadoTurno.CONFIRMADO, "cancelar"): EstadoTurno.CANCELADO,
}


@dataclass(frozen=True)
class Paciente:
    id: str
    nombre_mostrado: str
    contacto: str | None = None

    def __post_init__(self) -> None:
        id_limpio = self.id.strip()
        nombre_limpio = self.nombre_mostrado.strip()
        if not id_limpio or not nombre_limpio:
            raise DatosPacienteInvalidosError()
        contacto_limpio = self.contacto.strip() if self.contacto is not None else None
        object.__setattr__(self, "id", id_limpio)
        object.__setattr__(self, "nombre_mostrado", nombre_limpio)
        object.__setattr__(self, "contacto", contacto_limpio if contacto_limpio else None)

    @property
    def contacto_normalizado(self) -> str | None:
        return None if self.contacto is None else self.contacto.lower()


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

    @property
    def activo(self) -> bool:
        """Un turno cancelado ya no ocupa su intervalo (RN-TU-01)."""
        return self.estado is not EstadoTurno.CANCELADO

    def confirmar(self) -> "Turno":
        return self._transicionar("confirmar")

    def cancelar(self) -> "Turno":
        return self._transicionar("cancelar")

    def reprogramar(
        self,
        *,
        inicio: datetime | None = None,
        fin: datetime | None = None,
        profesional_id: str | None = None,
        box_id: str | None = None,
    ) -> "Turno":
        """Copia con nuevo horario y/o recursos (RN-TU-02). Conserva estado, paciente y prestación.

        Un inicio sin fin conserva la duración vigente; los campos omitidos conservan su valor.
        """
        if not self.activo:
            raise TransicionInvalidaError(self.estado, "reprogramar")
        nuevo_inicio = inicio if inicio is not None else self.inicio
        if fin is not None:
            nuevo_fin = fin
        elif inicio is not None:
            nuevo_fin = inicio + (self.fin - self.inicio)
        else:
            nuevo_fin = self.fin
        candidato = replace(
            self,
            inicio=nuevo_inicio,
            fin=nuevo_fin,
            profesional_id=profesional_id if profesional_id is not None else self.profesional_id,
            box_id=box_id if box_id is not None else self.box_id,
        )
        if ResumenTurno.de(candidato) == ResumenTurno.de(self):
            raise ReprogramacionSinCambiosError()
        return candidato

    def _transicionar(self, accion: str) -> "Turno":
        destino = _TRANSICIONES.get((self.estado, accion))
        if destino is None:
            raise TransicionInvalidaError(self.estado, accion)
        return replace(self, estado=destino)


@dataclass(frozen=True)
class ResumenTurno:
    """Lo que cambia al reprogramar; se guarda como `antes` / `despues` en el historial."""

    profesional_id: str
    box_id: str
    inicio: datetime
    fin: datetime

    @classmethod
    def de(cls, turno: Turno) -> "ResumenTurno":
        return cls(turno.profesional_id, turno.box_id, turno.inicio, turno.fin)


@dataclass(frozen=True)
class HistorialDeCambio:
    turno_id: str
    tipo: TipoCambio
    ocurrido_en: datetime
    antes: ResumenTurno | None = None
    despues: ResumenTurno | None = None
    actor_id: str | None = None


def calcular_fin(inicio: datetime, prestacion: Prestacion) -> datetime:
    if prestacion.duracion_minutos <= 0:
        raise DuracionInvalidaError()
    return inicio + timedelta(minutes=prestacion.duracion_minutos)
