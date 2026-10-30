"""Ruta HTTP del caso de uso de bloqueos; sin reglas de disponibilidad."""

from datetime import UTC
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, Request, status

from app.api.esquemas import BloqueoEntrada, BloqueoSalida, ErrorSalida
from app.application.crear_bloqueo import CrearBloqueo, SolicitudCrearBloqueo
from app.infrastructure.unidad_de_trabajo import UnidadDeTrabajoSQLAlchemy

router = APIRouter(prefix="/api/v1/bloqueos", tags=["bloqueos"])


def caso_crear_bloqueo(request: Request) -> CrearBloqueo:
    return CrearBloqueo(lambda: UnidadDeTrabajoSQLAlchemy(request.app.state.fabrica))


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=BloqueoSalida,
    responses={
        404: {"model": ErrorSalida},
        409: {"model": ErrorSalida},
        422: {"description": "Error de validación de entrada (`detail` de FastAPI)."},
    },
)
def crear_bloqueo(entrada: BloqueoEntrada, caso: Annotated[CrearBloqueo, Depends(caso_crear_bloqueo)]) -> BloqueoSalida:
    creado = caso.ejecutar(SolicitudCrearBloqueo(
        id=str(uuid4()),
        profesional_id=entrada.profesional_id,
        box_id=entrada.box_id,
        inicio=entrada.inicio,
        fin=entrada.fin,
        motivo=entrada.motivo,
    ))
    return BloqueoSalida(
        id=creado.id,
        profesional_id=creado.profesional_id,
        box_id=creado.box_id,
        inicio=creado.inicio.astimezone(UTC),
        fin=creado.fin.astimezone(UTC),
        motivo=creado.motivo,
    )
