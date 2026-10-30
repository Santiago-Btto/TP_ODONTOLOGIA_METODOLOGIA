from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from app.api import agenda, bloqueos, turnos
from app.domain.bloqueos import (
    FechaSinZonaError, IntervaloBloqueoInvalidoError, RecursoDeBloqueoInvalidoError,
)
from app.domain.disponibilidad import (
    ConflictoBloqueoBoxError,
    ConflictoBloqueoProfesionalError,
    ConflictoBoxError,
    ConflictoProfesionalError,
    ConflictoTurnoExistenteError,
)
from app.domain.turnos import (
    DuracionInvalidaError,
    ErrorDeDominio,
    IntervaloInvalidoError,
    RecursoInexistenteError,
)
from app.infrastructure.db import crear_esquema, crear_fabrica_de_sesiones, crear_motor, url_de_base

ESTADO_HTTP: dict[type[ErrorDeDominio], int] = {
    RecursoInexistenteError: status.HTTP_404_NOT_FOUND,
    ConflictoProfesionalError: status.HTTP_409_CONFLICT,
    ConflictoBoxError: status.HTTP_409_CONFLICT,
    ConflictoBloqueoProfesionalError: status.HTTP_409_CONFLICT,
    ConflictoBloqueoBoxError: status.HTTP_409_CONFLICT,
    ConflictoTurnoExistenteError: status.HTTP_409_CONFLICT,
    RecursoDeBloqueoInvalidoError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    FechaSinZonaError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    IntervaloInvalidoError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    IntervaloBloqueoInvalidoError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    DuracionInvalidaError: status.HTTP_422_UNPROCESSABLE_ENTITY,
}


def crear_app(fabrica: sessionmaker[Session] | None = None) -> FastAPI:
    """Sin `fabrica`, se conecta a DATABASE_URL y crea el esquema al iniciar."""

    @asynccontextmanager
    async def ciclo_de_vida(app: FastAPI) -> AsyncIterator[None]:
        if fabrica is None:
            motor = crear_motor(url_de_base())
            crear_esquema(motor)
            app.state.fabrica = crear_fabrica_de_sesiones(motor)
        else:
            app.state.fabrica = fabrica
        yield

    app = FastAPI(
        title="Turnos odontología",
        version="0.2.0",
        description="API interna de agenda. Sin autenticación hasta C-08: sólo para desarrollo local.",
        lifespan=ciclo_de_vida,
    )
    app.include_router(turnos.router)
    app.include_router(agenda.router)
    app.include_router(bloqueos.router)

    @app.exception_handler(ErrorDeDominio)
    async def error_de_dominio(_: Request, error: ErrorDeDominio) -> JSONResponse:
        estado = ESTADO_HTTP.get(type(error), status.HTTP_400_BAD_REQUEST)
        return JSONResponse(status_code=estado, content={"codigo": error.codigo, "detalle": str(error)})

    @app.get("/health", tags=["operación"])
    def salud(request: Request) -> JSONResponse:
        try:
            with request.app.state.fabrica() as sesion:
                sesion.execute(text("SELECT 1"))
        except Exception:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"estado": "degradado", "base_de_datos": "no disponible"},
            )
        return JSONResponse(content={"estado": "ok", "base_de_datos": "ok"})

    return app


app = crear_app()
