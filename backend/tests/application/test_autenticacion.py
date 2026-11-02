"""Casos de uso `Autenticar` y `ResolverActor` (C-08) con dobles en memoria."""

import pytest

from app.application.autenticacion import (
    Autenticar,
    CredencialesInvalidasError,
    NoAutenticadoError,
    ResolverActor,
    TokenEmitido,
    TokenExpiradoError,
    TokenInvalidoError,
)
from app.domain.autorizacion import Actor, Rol, Usuario

RECEPCION = Usuario("usuario-demo-001", "recepcion.demo", "hash:clave-demo-correcta", Rol.RECEPCION)
INACTIVO = Usuario("usuario-demo-002", "inactivo.demo", "hash:clave-demo-correcta", Rol.RECEPCION, activo=False)


class UsuariosEnMemoria:
    def __init__(self, *usuarios: Usuario) -> None:
        self.usuarios = {u.id: u for u in usuarios}

    def por_nombre(self, nombre_usuario: str) -> Usuario | None:
        return next((u for u in self.usuarios.values() if u.nombre_usuario == nombre_usuario), None)

    def por_id(self, usuario_id: str) -> Usuario | None:
        return self.usuarios.get(usuario_id)


class HasherFalso:
    hash_ficticio = "hash:__ficticio__"

    def __init__(self) -> None:
        self.verificados: list[str] = []

    def verificar(self, contrasena: str, hash_guardado: str) -> bool:
        self.verificados.append(hash_guardado)
        return hash_guardado == f"hash:{contrasena}"


class EmisorFalso:
    def emitir(self, usuario_id: str) -> TokenEmitido:
        return TokenEmitido(f"token:{usuario_id}", 1800)

    def leer_sujeto(self, token: str) -> str:
        if token == "expirado":
            raise TokenExpiradoError()
        if not token.startswith("token:"):
            raise TokenInvalidoError()
        return token.removeprefix("token:")


def autenticar(*usuarios: Usuario) -> tuple[Autenticar, HasherFalso]:
    hasher = HasherFalso()
    return Autenticar(UsuariosEnMemoria(*usuarios), hasher, EmisorFalso()), hasher


def test_login_valido_emite_token_para_el_usuario() -> None:
    caso, _ = autenticar(RECEPCION)

    assert caso.ejecutar("recepcion.demo", "clave-demo-correcta") == TokenEmitido("token:usuario-demo-001", 1800)


@pytest.mark.parametrize("nombre,contrasena", [
    ("recepcion.demo", "clave-demo-incorrecta"),
    ("inactivo.demo", "clave-demo-correcta"),
    ("inexistente.demo", "clave-demo-correcta"),
])
def test_credenciales_invalidas_se_rechazan_con_el_mismo_error(nombre: str, contrasena: str) -> None:
    caso, _ = autenticar(RECEPCION, INACTIVO)

    with pytest.raises(CredencialesInvalidasError) as error:
        caso.ejecutar(nombre, contrasena)

    assert error.value.codigo == "credenciales_invalidas"


def test_usuario_inexistente_igual_verifica_contra_un_hash_ficticio() -> None:
    caso, hasher = autenticar(RECEPCION)

    with pytest.raises(CredencialesInvalidasError):
        caso.ejecutar("inexistente.demo", "clave-demo-correcta")

    assert hasher.verificados == [HasherFalso.hash_ficticio]


def test_resolver_actor_con_token_valido() -> None:
    caso = ResolverActor(UsuariosEnMemoria(RECEPCION), EmisorFalso())

    assert caso.ejecutar("token:usuario-demo-001") == Actor("usuario-demo-001", Rol.RECEPCION)


@pytest.mark.parametrize("token,esperado", [
    (None, NoAutenticadoError),
    ("", NoAutenticadoError),
    ("expirado", TokenExpiradoError),
    ("basura", TokenInvalidoError),
    ("token:usuario-demo-borrado", TokenInvalidoError),
    ("token:usuario-demo-002", TokenInvalidoError),
])
def test_resolver_actor_rechaza_tokens_no_validos(token: str | None, esperado: type[Exception]) -> None:
    caso = ResolverActor(UsuariosEnMemoria(RECEPCION, INACTIVO), EmisorFalso())

    with pytest.raises(esperado):
        caso.ejecutar(token)
