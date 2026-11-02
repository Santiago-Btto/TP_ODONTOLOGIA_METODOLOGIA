"""Dependencias FastAPI de autenticación y autorización (C-08).

`actor_actual` protege routers completos; `requiere(permiso)` además aplica la matriz del dominio.
"""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer

from app.application.autenticacion import ResolverActor
from app.domain.autorizacion import Actor, Permiso, verificar_permiso
from app.infrastructure.unidad_de_trabajo import UsuariosSQLAlchemy

URL_TOKEN = "/api/v1/auth/token"

# auto_error=False: la ausencia de token se informa con el mismo cuerpo {codigo, detalle} que el resto.
esquema_oauth2 = OAuth2PasswordBearer(tokenUrl=URL_TOKEN, auto_error=False)


def actor_actual(request: Request, token: Annotated[str | None, Depends(esquema_oauth2)]) -> Actor:
    caso = ResolverActor(UsuariosSQLAlchemy(request.app.state.fabrica), request.app.state.emisor)
    return caso.ejecutar(token)


def requiere(permiso: Permiso) -> Callable[[Actor], Actor]:
    def dependencia(actor: Annotated[Actor, Depends(actor_actual)]) -> Actor:
        verificar_permiso(actor, permiso)
        return actor

    dependencia.__name__ = f"requiere_{permiso.value}"
    return dependencia
