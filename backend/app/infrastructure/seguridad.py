"""Adaptadores de seguridad (C-08): hash Argon2id (pwdlib), JWT HS256 (PyJWT) y configuración por entorno."""

import os
import secrets
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from app.application.autenticacion import TokenEmitido, TokenExpiradoError, TokenInvalidoError

ALGORITMO = "HS256"
LARGO_MINIMO_SECRETO = 32
EXPIRACION_POR_DEFECTO_MINUTOS = 30


@dataclass(frozen=True)
class ConfiguracionSeguridad:
    jwt_secret: str = field(repr=False)
    expira_minutos: int = EXPIRACION_POR_DEFECTO_MINUTOS

    @classmethod
    def desde_entorno(cls, entorno: Mapping[str, str] | None = None) -> "ConfiguracionSeguridad":
        entorno = os.environ if entorno is None else entorno
        secreto = entorno.get("JWT_SECRET", "")
        if len(secreto) < LARGO_MINIMO_SECRETO:
            raise RuntimeError(
                f"Falta JWT_SECRET o tiene menos de {LARGO_MINIMO_SECRETO} caracteres. Generar uno con "
                "`python -c \"import secrets; print(secrets.token_urlsafe(48))\"` (ver backend/.env.example)."
            )
        crudo = entorno.get("JWT_EXPIRA_MINUTOS", str(EXPIRACION_POR_DEFECTO_MINUTOS))
        try:
            minutos = int(crudo)
        except ValueError:
            minutos = 0
        if minutos <= 0:
            raise RuntimeError("JWT_EXPIRA_MINUTOS debe ser un entero positivo.")
        return cls(secreto, minutos)


class HasherArgon2:
    def __init__(self) -> None:
        self._hash = PasswordHash((Argon2Hasher(),))
        self._ficticio = self._hash.hash(secrets.token_urlsafe(32))

    @property
    def hash_ficticio(self) -> str:
        return self._ficticio

    def hashear(self, contrasena: str) -> str:
        return self._hash.hash(contrasena)

    def verificar(self, contrasena: str, hash_guardado: str) -> bool:
        try:
            return self._hash.verify(contrasena, hash_guardado)
        except Exception:  # hash corrupto o de un esquema desconocido: nunca autentica
            return False


class EmisorJWT:
    """Sólo `sub`, `iat` y `exp`: el rol se resuelve desde la base en cada request."""

    def __init__(
        self, configuracion: ConfiguracionSeguridad, reloj: Callable[[], datetime] = lambda: datetime.now(UTC)
    ) -> None:
        self._configuracion = configuracion
        self._reloj = reloj

    def emitir(self, usuario_id: str) -> TokenEmitido:
        emitido_en = int(self._reloj().timestamp())
        vida = self._configuracion.expira_minutos * 60
        token = jwt.encode(
            {"sub": usuario_id, "iat": emitido_en, "exp": emitido_en + vida},
            self._configuracion.jwt_secret,
            algorithm=ALGORITMO,
        )
        return TokenEmitido(token, vida)

    def leer_sujeto(self, token: str) -> str:
        try:
            reclamos = jwt.decode(
                token,
                self._configuracion.jwt_secret,
                algorithms=[ALGORITMO],  # lista cerrada: rechaza `none` y confusión de algoritmos
                options={"require": ["sub", "iat", "exp"]},
            )
        except jwt.ExpiredSignatureError as error:
            raise TokenExpiradoError() from error
        except jwt.InvalidTokenError as error:
            raise TokenInvalidoError() from error
        sujeto = reclamos["sub"]
        if not isinstance(sujeto, str) or not sujeto:
            raise TokenInvalidoError()
        return sujeto
