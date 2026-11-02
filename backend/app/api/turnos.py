from datetime import UTC, datetime
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Path, Request, status

from app.api.esquemas import ErrorSalida, ReprogramacionEntrada, TurnoEntrada, TurnoSalida
from app.api.seguridad import actor_actual, requiere
from app.application.cambiar_estado_turno import CancelarTurno, ConfirmarTurno, SolicitudCambioDeEstado
from app.application.crear_turno import CrearTurno, SolicitudCrearTurno
from app.application.reprogramar_turno import ReprogramarTurno, SolicitudReprogramarTurno
from app.domain.autorizacion import Actor, Permiso
from app.domain.turnos import Turno
from app.infrastructure.unidad_de_trabajo import UnidadDeTrabajoSQLAlchemy

router = APIRouter(prefix="/api/v1/turnos", tags=["turnos"], dependencies=[Depends(actor_actual)])

IdTurno = Annotated[str, Path(min_length=1, max_length=64)]


def caso_crear_turno(request: Request) -> CrearTurno:
    fabrica = request.app.state.fabrica
    return CrearTurno(lambda: UnidadDeTrabajoSQLAlchemy(fabrica), reloj=lambda: datetime.now(UTC))


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=TurnoSalida,
    responses={404: {"model": ErrorSalida}, 409: {"model": ErrorSalida}, 422: {"model": ErrorSalida}},
)
def crear_turno(
    entrada: TurnoEntrada,
    caso: Annotated[CrearTurno, Depends(caso_crear_turno)],
    actor: Annotated[Actor, Depends(requiere(Permiso.CREAR_TURNO))],
) -> TurnoSalida:
    turno = caso.ejecutar(
        SolicitudCrearTurno(
            id=str(uuid4()),
            paciente_id=entrada.paciente_id,
            profesional_id=entrada.profesional_id,
            box_id=entrada.box_id,
            prestacion_id=entrada.prestacion_id,
            inicio=entrada.inicio,
            fin=entrada.fin,
            actor_id=actor.id,
        )
    )
    return a_salida(turno)


def caso_confirmar_turno(request: Request) -> ConfirmarTurno:
    fabrica = request.app.state.fabrica
    return ConfirmarTurno(lambda: UnidadDeTrabajoSQLAlchemy(fabrica), reloj=lambda: datetime.now(UTC))


def caso_cancelar_turno(request: Request) -> CancelarTurno:
    fabrica = request.app.state.fabrica
    return CancelarTurno(lambda: UnidadDeTrabajoSQLAlchemy(fabrica), reloj=lambda: datetime.now(UTC))


@router.post(
    "/{turno_id}/confirmar",
    response_model=TurnoSalida,
    responses={404: {"model": ErrorSalida}, 409: {"model": ErrorSalida}},
)
def confirmar_turno(
    turno_id: IdTurno,
    caso: Annotated[ConfirmarTurno, Depends(caso_confirmar_turno)],
    actor: Annotated[Actor, Depends(requiere(Permiso.CONFIRMAR_TURNO))],
) -> TurnoSalida:
    return a_salida(caso.ejecutar(SolicitudCambioDeEstado(turno_id, actor_id=actor.id)))


@router.post(
    "/{turno_id}/cancelar",
    response_model=TurnoSalida,
    responses={404: {"model": ErrorSalida}, 409: {"model": ErrorSalida}},
)
def cancelar_turno(
    turno_id: IdTurno,
    caso: Annotated[CancelarTurno, Depends(caso_cancelar_turno)],
    actor: Annotated[Actor, Depends(requiere(Permiso.CANCELAR_TURNO))],
) -> TurnoSalida:
    return a_salida(caso.ejecutar(SolicitudCambioDeEstado(turno_id, actor_id=actor.id)))


def caso_reprogramar_turno(request: Request) -> ReprogramarTurno:
    fabrica = request.app.state.fabrica
    return ReprogramarTurno(lambda: UnidadDeTrabajoSQLAlchemy(fabrica), reloj=lambda: datetime.now(UTC))


@router.patch(
    "/{turno_id}",
    response_model=TurnoSalida,
    responses={404: {"model": ErrorSalida}, 409: {"model": ErrorSalida}, 422: {"model": ErrorSalida}},
)
def reprogramar_turno(
    turno_id: IdTurno,
    entrada: ReprogramacionEntrada,
    caso: Annotated[ReprogramarTurno, Depends(caso_reprogramar_turno)],
    actor: Annotated[Actor, Depends(requiere(Permiso.REPROGRAMAR_TURNO))],
) -> TurnoSalida:
    return a_salida(caso.ejecutar(SolicitudReprogramarTurno(
        turno_id=turno_id,
        inicio=entrada.inicio,
        fin=entrada.fin,
        profesional_id=entrada.profesional_id,
        box_id=entrada.box_id,
        actor_id=actor.id,
    )))


def a_salida(turno: Turno) -> TurnoSalida:
    return TurnoSalida(
        id=turno.id,
        paciente_id=turno.paciente_id,
        profesional_id=turno.profesional_id,
        box_id=turno.box_id,
        prestacion_id=turno.prestacion_id,
        inicio=turno.inicio.astimezone(UTC),
        fin=turno.fin.astimezone(UTC),
        estado=turno.estado.value,
    )
