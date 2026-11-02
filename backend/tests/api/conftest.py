"""Fixtures de API con autenticación (C-08).

El secreto JWT y la contraseña se generan al azar por sesión: nada sensible queda versionado.
`cliente` opera como recepción (todos los permisos de agenda); `cliente_como(rol)` y
`cliente_anonimo` cubren el resto de los casos.
"""

import secrets
from collections.abc import Callable, Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.api.main import crear_app
from app.domain.autorizacion import Rol
from app.infrastructure.modelos import UsuarioModelo
from app.infrastructure.seguridad import ConfiguracionSeguridad, EmisorJWT, HasherArgon2

USUARIOS_DEMO: dict[Rol, tuple[str, str, str | None]] = {
    Rol.RECEPCION: ("usuario-demo-recepcion", "recepcion.demo", None),
    Rol.RESPONSABLE: ("usuario-demo-responsable", "responsable.demo", None),
    Rol.ODONTOLOGO: ("usuario-demo-odontologo", "odontologo.demo", "profesional-demo-001"),
}


@pytest.fixture(scope="session")
def seguridad() -> ConfiguracionSeguridad:
    return ConfiguracionSeguridad(secrets.token_urlsafe(48), expira_minutos=30)


@pytest.fixture(scope="session")
def contrasena_demo() -> str:
    return secrets.token_urlsafe(18)


@pytest.fixture(scope="session")
def hash_demo(contrasena_demo: str) -> str:
    return HasherArgon2().hashear(contrasena_demo)  # una sola vez: Argon2id es lento a propósito


@pytest.fixture
def usuarios(fabrica: sessionmaker[Session], hash_demo: str) -> dict[Rol, str]:
    with fabrica() as sesion:
        for rol, (id_, nombre, profesional_id) in USUARIOS_DEMO.items():
            sesion.add(UsuarioModelo(id=id_, nombre_usuario=nombre, hash_contrasena=hash_demo,
                                     rol=rol.value, profesional_id=profesional_id, activo=True))
        sesion.commit()
    return {rol: datos[0] for rol, datos in USUARIOS_DEMO.items()}


@pytest.fixture
def app(fabrica: sessionmaker[Session], seguridad: ConfiguracionSeguridad, usuarios: dict[Rol, str]) -> FastAPI:
    return crear_app(fabrica, seguridad)


@pytest.fixture
def token_de(seguridad: ConfiguracionSeguridad, usuarios: dict[Rol, str]) -> Callable[[Rol], str]:
    emisor = EmisorJWT(seguridad)
    return lambda rol: emisor.emitir(usuarios[rol]).access_token


@pytest.fixture
def cliente_como(app: FastAPI, token_de: Callable[[Rol], str]) -> Iterator[Callable[[Rol], TestClient]]:
    abiertos: list[TestClient] = []

    def crear(rol: Rol) -> TestClient:
        cliente = TestClient(app, headers={"Authorization": f"Bearer {token_de(rol)}"})
        cliente.__enter__()
        abiertos.append(cliente)
        return cliente

    yield crear
    for cliente in abiertos:
        cliente.__exit__(None, None, None)


@pytest.fixture
def cliente(cliente_como: Callable[[Rol], TestClient]) -> TestClient:
    return cliente_como(Rol.RECEPCION)


@pytest.fixture
def cliente_anonimo(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as cliente:
        yield cliente
