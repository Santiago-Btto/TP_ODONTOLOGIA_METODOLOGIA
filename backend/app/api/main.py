from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from app.api import agenda, auth, bloqueos, pacientes, turnos
from app.application.autenticacion import (
    CredencialesInvalidasError,
    NoAutenticadoError,
    TokenExpiradoError,
    TokenInvalidoError,
)
from app.application.puertos import ColaRecordatorios
from app.domain.autorizacion import AccesoDenegadoError
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
    DatosPacienteInvalidosError,
    DuracionInvalidaError,
    ErrorDeDominio,
    IntervaloInvalidoError,
    PacienteDuplicadoError,
    RecursoInexistenteError,
    ReprogramacionSinCambiosError,
    TransicionInvalidaError,
)
from app.infrastructure.configuracion import crear_cola_recordatorios_desde_entorno
from app.infrastructure.db import crear_esquema, crear_fabrica_de_sesiones, crear_motor, url_de_base
from app.infrastructure.seguridad import ConfiguracionSeguridad, EmisorJWT, HasherArgon2

ESTADO_HTTP: dict[type[ErrorDeDominio], int] = {
    NoAutenticadoError: status.HTTP_401_UNAUTHORIZED,
    TokenInvalidoError: status.HTTP_401_UNAUTHORIZED,
    TokenExpiradoError: status.HTTP_401_UNAUTHORIZED,
    CredencialesInvalidasError: status.HTTP_401_UNAUTHORIZED,
    AccesoDenegadoError: status.HTTP_403_FORBIDDEN,
    RecursoInexistenteError: status.HTTP_404_NOT_FOUND,
    ConflictoProfesionalError: status.HTTP_409_CONFLICT,
    ConflictoBoxError: status.HTTP_409_CONFLICT,
    ConflictoBloqueoProfesionalError: status.HTTP_409_CONFLICT,
    ConflictoBloqueoBoxError: status.HTTP_409_CONFLICT,
    ConflictoTurnoExistenteError: status.HTTP_409_CONFLICT,
    TransicionInvalidaError: status.HTTP_409_CONFLICT,
    PacienteDuplicadoError: status.HTTP_409_CONFLICT,
    RecursoDeBloqueoInvalidoError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    FechaSinZonaError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    IntervaloInvalidoError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    IntervaloBloqueoInvalidoError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    DuracionInvalidaError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    ReprogramacionSinCambiosError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    DatosPacienteInvalidosError: status.HTTP_422_UNPROCESSABLE_ENTITY,
}


def crear_app(
    fabrica: sessionmaker[Session] | None = None,
    seguridad: ConfiguracionSeguridad | None = None,
    cola_recordatorios: ColaRecordatorios | None = None,
) -> FastAPI:
    """Sin `fabrica`, se conecta a DATABASE_URL y crea el esquema al iniciar.

    Sin `seguridad`, lee JWT_SECRET / JWT_EXPIRA_MINUTOS del entorno: si falta el secreto, la API no inicia.
    """

    @asynccontextmanager
    async def ciclo_de_vida(app: FastAPI) -> AsyncIterator[None]:
        configuracion = seguridad if seguridad is not None else ConfiguracionSeguridad.desde_entorno()
        app.state.emisor = EmisorJWT(configuracion)
        app.state.hasher = HasherArgon2()
        app.state.cola_recordatorios = (
            cola_recordatorios
            if cola_recordatorios is not None
            else crear_cola_recordatorios_desde_entorno()
        )
        if fabrica is None:
            motor = crear_motor(url_de_base())
            crear_esquema(motor)
            app.state.fabrica = crear_fabrica_de_sesiones(motor)
        else:
            app.state.fabrica = fabrica
        yield

    app = FastAPI(
        title="Turnos odontología",
        version="0.3.0",
        description=(
            "API interna de agenda para el personal de la clínica. Todas las rutas `/api/v1` "
            "(salvo `/api/v1/auth/token`) exigen `Authorization: Bearer <token>` (C-08)."
        ),
        lifespan=ciclo_de_vida,
    )
    app.include_router(auth.router)
    app.include_router(turnos.router)
    app.include_router(agenda.router)
    app.include_router(bloqueos.router)
    app.include_router(pacientes.router)

    @app.exception_handler(ErrorDeDominio)
    async def error_de_dominio(_: Request, error: ErrorDeDominio) -> JSONResponse:
        estado = ESTADO_HTTP.get(type(error), status.HTTP_400_BAD_REQUEST)
        encabezados = {"WWW-Authenticate": "Bearer"} if estado == status.HTTP_401_UNAUTHORIZED else None
        return JSONResponse(
            status_code=estado, content={"codigo": error.codigo, "detalle": str(error)}, headers=encabezados
        )

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
