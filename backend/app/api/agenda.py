from datetime import UTC
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from pydantic import AwareDatetime

from app.api.esquemas import ErrorSalida, TurnoAgendaSalida
from app.api.seguridad import actor_actual, requiere
from app.application.consultar_agenda import ConsultarAgenda, SolicitudConsultarAgenda
from app.domain.autorizacion import Actor, Permiso, verificar_alcance_agenda
from app.infrastructure.unidad_de_trabajo import LectorAgendaSQLAlchemy

router = APIRouter(prefix="/api/v1/agenda", tags=["agenda"], dependencies=[Depends(actor_actual)])


def caso_consultar_agenda(request: Request) -> ConsultarAgenda:
    fabrica = request.app.state.fabrica
    return ConsultarAgenda(LectorAgendaSQLAlchemy(fabrica))


@router.get(
    "",
    response_model=list[TurnoAgendaSalida],
    responses={401: {"model": ErrorSalida}, 403: {"model": ErrorSalida}, 422: {"model": ErrorSalida}},
)
def consultar_agenda(
    inicio: AwareDatetime,
    fin: AwareDatetime,
    caso: Annotated[ConsultarAgenda, Depends(caso_consultar_agenda)],
    actor: Annotated[Actor, Depends(requiere(Permiso.CONSULTAR_AGENDA))],
    profesional_id: Annotated[str | None, Query(min_length=1, max_length=64)] = None,
    box_id: Annotated[str | None, Query(min_length=1, max_length=64)] = None,
) -> list[TurnoAgendaSalida]:
    verificar_alcance_agenda(actor, profesional_id)
    turnos = caso.ejecutar(
        SolicitudConsultarAgenda(
            inicio=inicio,
            fin=fin,
            profesional_id=profesional_id,
            box_id=box_id,
        )
    )
    return [
        TurnoAgendaSalida(
            id=t.id,
            profesional_id=t.profesional_id,
            box_id=t.box_id,
            inicio=t.inicio.astimezone(UTC),
            fin=t.fin.astimezone(UTC),
            estado=t.estado.value,
        )
        for t in turnos
    ]
