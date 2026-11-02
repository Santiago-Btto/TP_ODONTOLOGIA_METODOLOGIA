"""Rutas HTTP para el alta y la búsqueda de pacientes con datos mínimos (C-17)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status

from app.api.esquemas import ErrorSalida, PacienteEntrada, PacienteSalida
from app.api.seguridad import actor_actual, requiere
from app.application.pacientes import BuscarPacientes, NuevoPaciente, RegistrarPaciente
from app.domain.autorizacion import Actor, Permiso
from app.domain.turnos import Paciente
from app.infrastructure.unidad_de_trabajo import UnidadDeTrabajoSQLAlchemy

router = APIRouter(prefix="/api/v1/pacientes", tags=["pacientes"], dependencies=[Depends(actor_actual)])


def caso_registrar_paciente(request: Request) -> RegistrarPaciente:
    return RegistrarPaciente(UnidadDeTrabajoSQLAlchemy(request.app.state.fabrica))


def caso_buscar_pacientes(request: Request) -> BuscarPacientes:
    return BuscarPacientes(UnidadDeTrabajoSQLAlchemy(request.app.state.fabrica))


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=PacienteSalida,
    responses={409: {"model": ErrorSalida}, 422: {"model": ErrorSalida}},
)
def registrar_paciente(
    entrada: PacienteEntrada,
    caso: Annotated[RegistrarPaciente, Depends(caso_registrar_paciente)],
    _: Annotated[Actor, Depends(requiere(Permiso.REGISTRAR_PACIENTE))],
) -> PacienteSalida:
    creado = caso.ejecutar(
        NuevoPaciente(
            id=entrada.id,
            nombre_mostrado=entrada.nombre_mostrado,
            contacto=entrada.contacto,
        )
    )
    return _a_paciente_salida(creado)


@router.get(
    "",
    response_model=list[PacienteSalida],
)
def buscar_pacientes(
    caso: Annotated[BuscarPacientes, Depends(caso_buscar_pacientes)],
    _: Annotated[Actor, Depends(requiere(Permiso.CONSULTAR_PACIENTES))],
    q: Annotated[str | None, Query(max_length=200)] = None,
) -> list[PacienteSalida]:
    return [_a_paciente_salida(paciente) for paciente in caso.ejecutar(q)]


def _a_paciente_salida(paciente: Paciente) -> PacienteSalida:
    return PacienteSalida(
        id=paciente.id,
        nombre_mostrado=paciente.nombre_mostrado,
        contacto=paciente.contacto,
    )
