from datetime import UTC, datetime
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Request, status

from app.api.esquemas import ErrorSalida, TurnoEntrada, TurnoSalida
from app.application.crear_turno import CrearTurno, SolicitudCrearTurno
from app.infrastructure.unidad_de_trabajo import UnidadDeTrabajoSQLAlchemy

router = APIRouter(prefix="/api/v1/turnos", tags=["turnos"])


def caso_crear_turno(request: Request) -> CrearTurno:
    fabrica = request.app.state.fabrica
    return CrearTurno(lambda: UnidadDeTrabajoSQLAlchemy(fabrica), reloj=lambda: datetime.now(UTC))


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=TurnoSalida,
    responses={404: {"model": ErrorSalida}, 409: {"model": ErrorSalida}, 422: {"model": ErrorSalida}},
)
def crear_turno(entrada: TurnoEntrada, caso: Annotated[CrearTurno, Depends(caso_crear_turno)]) -> TurnoSalida:
    turno = caso.ejecutar(
        SolicitudCrearTurno(
            id=str(uuid4()),
            paciente_id=entrada.paciente_id,
            profesional_id=entrada.profesional_id,
            box_id=entrada.box_id,
            prestacion_id=entrada.prestacion_id,
            inicio=entrada.inicio,
            fin=entrada.fin,
        )
    )
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
