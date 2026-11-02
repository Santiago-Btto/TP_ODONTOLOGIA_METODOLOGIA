"""Hash de contraseñas, JWT y configuración (C-08). No usan base de datos."""

import secrets
from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.application.autenticacion import TokenExpiradoError, TokenInvalidoError
from app.infrastructure.seguridad import ConfiguracionSeguridad, EmisorJWT, HasherArgon2

SECRETO = secrets.token_urlsafe(48)
AHORA = datetime(2030, 1, 1, 8, 0, tzinfo=UTC)


def emisor(reloj: datetime = AHORA, secreto: str = SECRETO) -> EmisorJWT:
    return EmisorJWT(ConfiguracionSeguridad(secreto, expira_minutos=30), reloj=lambda: reloj)


def test_hash_argon2id_verifica_la_contrasena_correcta_y_no_la_guarda_en_claro() -> None:
    hasher = HasherArgon2()
    guardado = hasher.hashear("clave-demo-larga-001")

    assert guardado.startswith("$argon2id$")
    assert "clave-demo-larga-001" not in guardado
    assert hasher.verificar("clave-demo-larga-001", guardado)
    assert not hasher.verificar("clave-demo-incorrecta", guardado)
    assert not hasher.verificar("clave-demo-larga-001", hasher.hash_ficticio)


def test_verificar_un_hash_corrupto_devuelve_falso() -> None:
    assert not HasherArgon2().verificar("clave-demo", "no-es-un-hash")


@pytest.mark.parametrize("entorno", [{}, {"JWT_SECRET": ""}, {"JWT_SECRET": "corto"}])
def test_configuracion_rechaza_secreto_ausente_o_corto(entorno: dict[str, str]) -> None:
    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        ConfiguracionSeguridad.desde_entorno(entorno)


@pytest.mark.parametrize("minutos", ["0", "-5", "abc"])
def test_configuracion_rechaza_expiracion_invalida(minutos: str) -> None:
    with pytest.raises(RuntimeError, match="JWT_EXPIRA_MINUTOS"):
        ConfiguracionSeguridad.desde_entorno({"JWT_SECRET": SECRETO, "JWT_EXPIRA_MINUTOS": minutos})


def test_configuracion_toma_valores_del_entorno() -> None:
    configuracion = ConfiguracionSeguridad.desde_entorno({"JWT_SECRET": SECRETO, "JWT_EXPIRA_MINUTOS": "15"})

    assert (configuracion.jwt_secret, configuracion.expira_minutos) == (SECRETO, 15)
    assert ConfiguracionSeguridad.desde_entorno({"JWT_SECRET": SECRETO}).expira_minutos == 30
    assert SECRETO not in repr(configuracion)


def test_token_lleva_solo_sujeto_y_tiempos() -> None:
    emitido = emisor().emitir("usuario-demo-001")

    reclamos = jwt.decode(emitido.access_token, SECRETO, algorithms=["HS256"], options={"verify_exp": False, "verify_iat": False})
    assert reclamos == {"sub": "usuario-demo-001", "iat": int(AHORA.timestamp()),
                        "exp": int((AHORA + timedelta(minutes=30)).timestamp())}
    assert emitido.expira_en_segundos == 1800
    assert jwt.get_unverified_header(emitido.access_token)["alg"] == "HS256"


def test_leer_sujeto_de_un_token_vigente() -> None:
    token = emisor(datetime.now(UTC)).emitir("usuario-demo-001").access_token

    assert emisor().leer_sujeto(token) == "usuario-demo-001"


def test_token_vencido_se_informa_como_expirado() -> None:
    token = emisor(datetime.now(UTC) - timedelta(minutes=31)).emitir("usuario-demo-001").access_token

    with pytest.raises(TokenExpiradoError):
        emisor().leer_sujeto(token)


def test_token_con_otra_firma_es_invalido() -> None:
    token = emisor(datetime.now(UTC), secreto=secrets.token_urlsafe(48)).emitir("usuario-demo-001").access_token

    with pytest.raises(TokenInvalidoError):
        emisor().leer_sujeto(token)


@pytest.mark.parametrize("token", [
    jwt.encode({"sub": "usuario-demo-001", "iat": 1, "exp": 4102444800}, key=None, algorithm="none"),
    jwt.encode({"sub": "usuario-demo-001", "exp": 4102444800}, SECRETO, algorithm="HS256"),
    jwt.encode({"iat": 1, "exp": 4102444800}, SECRETO, algorithm="HS256"),
    jwt.encode({"sub": "usuario-demo-001", "iat": 1, "exp": 4102444800}, SECRETO, algorithm="HS512"),
    "no-es-un-jwt",
])
def test_tokens_sin_algoritmo_permitido_o_sin_reclamos_son_invalidos(token: str) -> None:
    with pytest.raises(TokenInvalidoError):
        emisor().leer_sujeto(token)
