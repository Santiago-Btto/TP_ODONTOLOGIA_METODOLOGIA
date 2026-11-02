"""Escenarios de `autenticacion-y-autorizacion` (C-08) contra PostgreSQL real."""

import re
import secrets
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, sessionmaker

from app.domain.autorizacion import Rol
from app.infrastructure.modelos import HistorialModelo, TurnoModelo, UsuarioModelo
from app.infrastructure.seguridad import ConfiguracionSeguridad, EmisorJWT

URL_TOKEN = "/api/v1/auth/token"
AGENDA = {"inicio": "2030-01-10T08:00:00-03:00", "fin": "2030-01-10T12:00:00-03:00"}
TURNO = {
    "paciente_id": "paciente-demo-001", "profesional_id": "profesional-demo-001",
    "box_id": "box-demo-001", "prestacion_id": "prestacion-demo-001",
    "inicio": "2030-01-10T09:00:00-03:00",
}


def con_token(app: FastAPI, token: str) -> TestClient:
    return TestClient(app, headers={"Authorization": f"Bearer {token}"})


def assert_401(respuesta: object, codigo: str) -> None:
    assert respuesta.status_code == 401  # type: ignore[attr-defined]
    assert respuesta.json()["codigo"] == codigo  # type: ignore[attr-defined]
    assert respuesta.headers["www-authenticate"] == "Bearer"  # type: ignore[attr-defined]


def cantidad(fabrica: sessionmaker[Session], modelo: type[TurnoModelo] | type[HistorialModelo]) -> int:
    with fabrica() as sesion:
        return sesion.scalar(select(func.count()).select_from(modelo)) or 0


# Escenario: Login válido
def test_login_valido_devuelve_un_token_bearer_utilizable(cliente_anonimo: TestClient, contrasena_demo: str,
                                                          app: FastAPI) -> None:
    respuesta = cliente_anonimo.post(URL_TOKEN, data={"username": "recepcion.demo", "password": contrasena_demo})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert (cuerpo["token_type"], cuerpo["expires_in"]) == ("bearer", 1800)
    with con_token(app, cuerpo["access_token"]) as cliente:
        assert cliente.get("/api/v1/agenda", params=AGENDA).status_code == 200


# Escenarios: Contraseña incorrecta / Usuario inexistente o inactivo
@pytest.mark.parametrize("usuario,desactivar", [
    ("recepcion.demo", False),  # con contraseña incorrecta
    ("inexistente.demo", False),
    ("recepcion.demo", True),
])
def test_login_invalido_responde_401_credenciales_invalidas(
    cliente_anonimo: TestClient, fabrica: sessionmaker[Session], contrasena_demo: str,
    usuario: str, desactivar: bool
) -> None:
    contrasena = contrasena_demo if (desactivar or usuario != "recepcion.demo") else "clave-demo-incorrecta"
    if desactivar:
        with fabrica() as sesion:
            sesion.execute(update(UsuarioModelo).where(UsuarioModelo.nombre_usuario == usuario).values(activo=False))
            sesion.commit()

    respuesta = cliente_anonimo.post(URL_TOKEN, data={"username": usuario, "password": contrasena})

    assert_401(respuesta, "credenciales_invalidas")
    assert "access_token" not in respuesta.json()


def test_login_sin_formulario_responde_422(cliente_anonimo: TestClient) -> None:
    assert cliente_anonimo.post(URL_TOKEN, json={"username": "recepcion.demo"}).status_code == 422


# Escenario: Identidad del usuario autenticado
def test_yo_devuelve_identidad_sin_hash(cliente_como: Callable[[Rol], TestClient]) -> None:
    respuesta = cliente_como(Rol.ODONTOLOGO).get("/api/v1/auth/yo")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"id": "usuario-demo-odontologo", "nombre_usuario": "odontologo.demo",
                                "rol": "odontologo", "profesional_id": "profesional-demo-001"}


# Escenario: Sin token
def test_todas_las_rutas_api_v1_exigen_token(app: FastAPI, cliente_anonimo: TestClient,
                                             fabrica: sessionmaker[Session]) -> None:
    protegidas = [
        (metodo, re.sub(r"\{[^}]+\}", "turno-demo-x", ruta.path))
        for ruta in app.routes
        if isinstance(ruta, APIRoute) and ruta.path.startswith("/api/v1") and ruta.path != URL_TOKEN
        for metodo in ruta.methods
    ]
    assert len(protegidas) >= 7  # turnos (4), agenda, bloqueos y auth/yo; una ruta nueva entra sola al barrido

    for metodo, ruta in protegidas:
        assert_401(cliente_anonimo.request(metodo, ruta, json={}), "no_autenticado")
    assert cantidad(fabrica, TurnoModelo) == 0


@pytest.mark.parametrize("encabezado", ["Basic dXN1YXJpbzpjbGF2ZQ==", "Bearer", "Bearer "])
def test_esquema_o_token_vacio_responde_401(cliente_anonimo: TestClient, encabezado: str) -> None:
    respuesta = cliente_anonimo.get("/api/v1/agenda", params=AGENDA, headers={"Authorization": encabezado})

    assert_401(respuesta, "no_autenticado")


# Escenario: Token expirado
def test_token_expirado_responde_401(app: FastAPI, seguridad: ConfiguracionSeguridad) -> None:
    viejo = EmisorJWT(seguridad, reloj=lambda: datetime.now(UTC) - timedelta(minutes=31))

    with con_token(app, viejo.emitir("usuario-demo-recepcion").access_token) as cliente:
        assert_401(cliente.get("/api/v1/agenda", params=AGENDA), "token_expirado")


# Escenario: Firma inválida
@pytest.mark.parametrize("fabricar", [
    lambda: EmisorJWT(ConfiguracionSeguridad(secrets.token_urlsafe(48))).emitir("usuario-demo-recepcion").access_token,
    lambda: jwt.encode({"sub": "usuario-demo-recepcion", "iat": int(datetime.now(UTC).timestamp()),
                        "exp": int(datetime.now(UTC).timestamp()) + 600}, key=None, algorithm="none"),
    lambda: "no-es-un-jwt",
])
def test_token_con_firma_o_algoritmo_invalido_responde_401(app: FastAPI, fabricar: Callable[[], str]) -> None:
    with con_token(app, fabricar()) as cliente:
        assert_401(cliente.post("/api/v1/turnos", json=TURNO), "token_invalido")


# Escenario: Usuario desactivado después de emitir el token
@pytest.mark.parametrize("operacion", ["desactivar", "borrar"])
def test_usuario_desactivado_o_borrado_invalida_su_token(
    cliente: TestClient, fabrica: sessionmaker[Session], operacion: str
) -> None:
    with fabrica() as sesion:
        filtro = UsuarioModelo.id == "usuario-demo-recepcion"
        if operacion == "desactivar":
            sesion.execute(update(UsuarioModelo).where(filtro).values(activo=False))
        else:
            sesion.delete(sesion.get(UsuarioModelo, "usuario-demo-recepcion"))
        sesion.commit()

    assert_401(cliente.get("/api/v1/agenda", params=AGENDA), "token_invalido")


# Escenario: Odontólogo intenta crear un turno (y el resto de las escrituras)
@pytest.mark.parametrize("metodo,ruta,cuerpo", [
    ("POST", "/api/v1/turnos", TURNO),
    ("POST", "/api/v1/bloqueos", {"profesional_id": "profesional-demo-001",
                                  "inicio": "2030-01-10T09:00:00-03:00", "fin": "2030-01-10T10:00:00-03:00"}),
])
def test_odontologo_no_puede_escribir(
    cliente_como: Callable[[Rol], TestClient], fabrica: sessionmaker[Session],
    metodo: str, ruta: str, cuerpo: dict[str, str]
) -> None:
    respuesta = cliente_como(Rol.ODONTOLOGO).request(metodo, ruta, json=cuerpo)

    assert respuesta.status_code == 403
    assert respuesta.json()["codigo"] == "acceso_denegado"
    assert (cantidad(fabrica, TurnoModelo), cantidad(fabrica, HistorialModelo)) == (0, 0)


@pytest.mark.parametrize("accion", ["confirmar", "cancelar", "reprogramar"])
def test_odontologo_no_puede_cambiar_turnos_existentes(
    cliente: TestClient, cliente_como: Callable[[Rol], TestClient], accion: str
) -> None:
    turno_id = cliente.post("/api/v1/turnos", json=TURNO).json()["id"]
    odontologo = cliente_como(Rol.ODONTOLOGO)

    respuesta = (odontologo.patch(f"/api/v1/turnos/{turno_id}", json={"inicio": "2030-01-10T11:00:00-03:00"})
                 if accion == "reprogramar" else odontologo.post(f"/api/v1/turnos/{turno_id}/{accion}"))

    assert respuesta.status_code == 403
    assert cliente.get("/api/v1/agenda", params=AGENDA).json()[0]["estado"] == "programado"


# Escenario: Odontólogo consulta su propia agenda
def test_odontologo_consulta_su_propia_agenda(cliente: TestClient,
                                              cliente_como: Callable[[Rol], TestClient]) -> None:
    turno_id = cliente.post("/api/v1/turnos", json=TURNO).json()["id"]

    respuesta = cliente_como(Rol.ODONTOLOGO).get(
        "/api/v1/agenda", params={**AGENDA, "profesional_id": "profesional-demo-001"})

    assert respuesta.status_code == 200
    assert [t["id"] for t in respuesta.json()] == [turno_id]


# Escenario: Odontólogo consulta otra agenda
@pytest.mark.parametrize("filtro", [{}, {"profesional_id": "profesional-demo-002"}, {"box_id": "box-demo-001"}])
def test_odontologo_no_consulta_agendas_ajenas(cliente_como: Callable[[Rol], TestClient],
                                               filtro: dict[str, str]) -> None:
    respuesta = cliente_como(Rol.ODONTOLOGO).get("/api/v1/agenda", params={**AGENDA, **filtro})

    assert respuesta.status_code == 403
    assert respuesta.json()["codigo"] == "acceso_denegado"


# Escenarios: Recepción opera turnos y bloqueos / Actor en el historial
@pytest.mark.parametrize("rol", [Rol.RECEPCION, Rol.RESPONSABLE])
def test_personal_operativo_opera_y_queda_como_actor_del_historial(
    cliente_como: Callable[[Rol], TestClient], fabrica: sessionmaker[Session], usuarios: dict[Rol, str], rol: Rol
) -> None:
    cliente = cliente_como(rol)
    turno_id = cliente.post("/api/v1/turnos", json=TURNO).json()["id"]
    assert cliente.post(f"/api/v1/turnos/{turno_id}/confirmar").status_code == 200
    assert cliente.patch(f"/api/v1/turnos/{turno_id}", json={"inicio": "2030-01-10T11:00:00-03:00"}).status_code == 200
    assert cliente.post(f"/api/v1/turnos/{turno_id}/cancelar").status_code == 200
    assert cliente.post("/api/v1/bloqueos", json={
        "box_id": "box-demo-002", "inicio": "2030-01-10T09:00:00-03:00",
        "fin": "2030-01-10T10:00:00-03:00"}).status_code == 201

    with fabrica() as sesion:
        eventos = sesion.execute(select(HistorialModelo.tipo, HistorialModelo.actor_id)
                                 .order_by(HistorialModelo.id)).all()
    assert [tuple(e) for e in eventos] == [(tipo, usuarios[rol])
                                           for tipo in ("creado", "confirmado", "reprogramado", "cancelado")]


def test_health_y_documentacion_siguen_publicas(cliente_anonimo: TestClient) -> None:
    assert cliente_anonimo.get("/health").status_code == 200
    documento = cliente_anonimo.get("/openapi.json").json()
    assert documento["components"]["securitySchemes"]["OAuth2PasswordBearer"]["type"] == "oauth2"
