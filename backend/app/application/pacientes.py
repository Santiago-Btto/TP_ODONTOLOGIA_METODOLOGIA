"""Casos de uso de alta y búsqueda de pacientes con datos mínimos (C-17)."""

from collections.abc import Callable
from dataclasses import dataclass
from types import TracebackType
from typing import Protocol, Self
from uuid import uuid4

from app.application.puertos import RepositorioPacientes
from app.domain.turnos import Paciente, PacienteDuplicadoError


class UnidadDeTrabajoPacientes(Protocol):
    """Puerto de unidad de trabajo acotado al repositorio de pacientes."""

    pacientes: RepositorioPacientes

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        tipo: type[BaseException] | None,
        error: BaseException | None,
        traza: TracebackType | None,
    ) -> None: ...

    def commit(self) -> None: ...


ProveedorUnidadDeTrabajoPacientes = (
    UnidadDeTrabajoPacientes | Callable[[], UnidadDeTrabajoPacientes]
)


def _abrir_uow(proveedor: ProveedorUnidadDeTrabajoPacientes) -> UnidadDeTrabajoPacientes:
    return proveedor() if callable(proveedor) else proveedor


def _generar_id_paciente() -> str:
    return f"paciente-{uuid4().hex[:12]}"


@dataclass(frozen=True)
class NuevoPaciente:
    nombre_mostrado: str
    contacto: str | None = None
    id: str | None = None


class RegistrarPaciente:
    """Da de alta un paciente con datos mínimos validando unicidad por id y contacto."""

    def __init__(self, unidad_de_trabajo: ProveedorUnidadDeTrabajoPacientes) -> None:
        self._uow = unidad_de_trabajo

    def ejecutar(self, nuevo: NuevoPaciente) -> Paciente:
        paciente_id = _generar_id_paciente() if nuevo.id is None else nuevo.id
        paciente = Paciente(
            id=paciente_id,
            nombre_mostrado=nuevo.nombre_mostrado,
            contacto=nuevo.contacto,
        )
        with _abrir_uow(self._uow) as uow:
            if uow.pacientes.obtener(paciente.id) is not None:
                raise PacienteDuplicadoError(f"Ya existe un paciente registrado con id '{paciente.id}'.")
            if (
                paciente.contacto_normalizado is not None
                and uow.pacientes.obtener_por_contacto(paciente.contacto_normalizado) is not None
            ):
                raise PacienteDuplicadoError("Ya existe un paciente registrado con ese contacto.")
            uow.pacientes.agregar(paciente)
            uow.commit()
        return paciente


class BuscarPacientes:
    """Lista y filtra pacientes registrados por nombre mostrado, id o contacto."""

    def __init__(self, unidad_de_trabajo: ProveedorUnidadDeTrabajoPacientes) -> None:
        self._uow = unidad_de_trabajo

    def ejecutar(self, consulta: str | None = None) -> list[Paciente]:
        termino = consulta.strip() if consulta is not None else None
        with _abrir_uow(self._uow) as uow:
            return uow.pacientes.buscar(termino if termino else None)
