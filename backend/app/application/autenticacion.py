"""Casos de uso de autenticación (C-08): emitir un token y resolver el actor de un request."""

from dataclasses import dataclass
from typing import Protocol

from app.domain.autorizacion import Actor, Usuario
from app.domain.turnos import ErrorDeDominio


class CredencialesInvalidasError(ErrorDeDominio):
    codigo = "credenciales_invalidas"

    def __init__(self) -> None:
        super().__init__("Usuario o contraseña incorrectos.")


class NoAutenticadoError(ErrorDeDominio):
    codigo = "no_autenticado"

    def __init__(self) -> None:
        super().__init__("Se requiere un token de acceso (Authorization: Bearer).")


class TokenInvalidoError(ErrorDeDominio):
    codigo = "token_invalido"

    def __init__(self) -> None:
        super().__init__("El token de acceso no es válido.")


class TokenExpiradoError(ErrorDeDominio):
    codigo = "token_expirado"

    def __init__(self) -> None:
        super().__init__("El token de acceso expiró.")


@dataclass(frozen=True)
class TokenEmitido:
    access_token: str
    expira_en_segundos: int


class RepositorioUsuarios(Protocol):
    def por_nombre(self, nombre_usuario: str) -> Usuario | None: ...

    def por_id(self, usuario_id: str) -> Usuario | None: ...


class HasherDeContrasenas(Protocol):
    @property
    def hash_ficticio(self) -> str:
        """Hash válido de un valor aleatorio, para igualar el costo cuando el usuario no existe."""
        ...

    def verificar(self, contrasena: str, hash_guardado: str) -> bool: ...


class EmisorDeTokens(Protocol):
    def emitir(self, usuario_id: str) -> TokenEmitido: ...

    def leer_sujeto(self, token: str) -> str:
        """Valida firma, algoritmo y vigencia; lanza `TokenInvalidoError` o `TokenExpiradoError`."""
        ...


class Autenticar:
    def __init__(self, usuarios: RepositorioUsuarios, hasher: HasherDeContrasenas, emisor: EmisorDeTokens) -> None:
        self._usuarios = usuarios
        self._hasher = hasher
        self._emisor = emisor

    def ejecutar(self, nombre_usuario: str, contrasena: str) -> TokenEmitido:
        usuario = self._usuarios.por_nombre(nombre_usuario)
        if usuario is None:
            # Mismo costo que un usuario existente: no revela qué nombres están registrados.
            self._hasher.verificar(contrasena, self._hasher.hash_ficticio)
            raise CredencialesInvalidasError()
        if not self._hasher.verificar(contrasena, usuario.hash_contrasena) or not usuario.activo:
            raise CredencialesInvalidasError()
        return self._emisor.emitir(usuario.id)


class ResolverActor:
    """El rol se lee de la base en cada request: desactivar o cambiar el rol aplica de inmediato."""

    def __init__(self, usuarios: RepositorioUsuarios, emisor: EmisorDeTokens) -> None:
        self._usuarios = usuarios
        self._emisor = emisor

    def ejecutar(self, token: str | None) -> Actor:
        if not token:
            raise NoAutenticadoError()
        usuario = self._usuarios.por_id(self._emisor.leer_sujeto(token))
        if usuario is None or not usuario.activo:
            raise TokenInvalidoError()
        return usuario.como_actor()
