"""Emisión de tokens (OAuth2 password flow) e identidad del usuario autenticado (C-08)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.api.esquemas import ErrorSalida, TokenSalida, UsuarioSalida
from app.api.seguridad import actor_actual
from app.application.autenticacion import Autenticar, TokenInvalidoError
from app.domain.autorizacion import Actor
from app.infrastructure.unidad_de_trabajo import UsuariosSQLAlchemy

router = APIRouter(prefix="/api/v1/auth", tags=["autenticación"])


@router.post("/token", response_model=TokenSalida, responses={401: {"model": ErrorSalida}})
def emitir_token(request: Request, formulario: Annotated[OAuth2PasswordRequestForm, Depends()]) -> TokenSalida:
    caso = Autenticar(UsuariosSQLAlchemy(request.app.state.fabrica), request.app.state.hasher, request.app.state.emisor)
    emitido = caso.ejecutar(formulario.username, formulario.password)
    return TokenSalida(access_token=emitido.access_token, token_type="bearer", expires_in=emitido.expira_en_segundos)


@router.get("/yo", response_model=UsuarioSalida, responses={401: {"model": ErrorSalida}})
def yo(request: Request, actor: Annotated[Actor, Depends(actor_actual)]) -> UsuarioSalida:
    usuario = UsuariosSQLAlchemy(request.app.state.fabrica).por_id(actor.id)
    if usuario is None:
        raise TokenInvalidoError()
    return UsuarioSalida(id=usuario.id, nombre_usuario=usuario.nombre_usuario,
                         rol=usuario.rol.value, profesional_id=usuario.profesional_id)
