"""Prueba de caja negra del MVP; ejecutar sólo en Compose E2E aislado."""

import os
import time
from datetime import UTC, datetime, time as hora, timedelta

import httpx


def respuesta(cliente: httpx.Client, metodo: str, ruta: str, estado: int, **kwargs: object) -> httpx.Response:
    resultado = cliente.request(metodo, ruta, **kwargs)
    assert resultado.status_code == estado, f"{metodo} {ruta}: esperado {estado}, recibido {resultado.status_code}"
    return resultado


def test_recorrido_http_completo_del_mvp() -> None:
    api = os.environ["MVP_API_URL"]
    web = os.environ["MVP_WEB_URL"]
    contrasena = os.environ["DEMO_PASSWORD"]
    dia = datetime.now(UTC).date() + timedelta(days=2)
    inicio = datetime.combine(dia, hora(12, 0), tzinfo=UTC)
    bloqueado = inicio + timedelta(hours=2)
    reprogramado = inicio + timedelta(hours=4)

    with httpx.Client(base_url=api, timeout=10) as directo, httpx.Client(base_url=web, timeout=10) as cliente:
        assert respuesta(directo, "GET", "/health", 200).json()["estado"] == "ok"
        assert "<html" in respuesta(cliente, "GET", "/", 200).text.lower()
        respuesta(cliente, "GET", "/api/v1/auth/yo", 401)  # proxy del mismo origen

        login_respuesta = cliente.post(
            "/api/v1/auth/token", data={"username": "recepcion.demo", "password": contrasena}
        )
        assert login_respuesta.status_code == 200, "El usuario demo no pudo autenticarse"
        login = login_respuesta.json()
        assert login["token_type"] == "bearer" and login["access_token"]
        cliente.headers["Authorization"] = f"Bearer {login['access_token']}"
        assert respuesta(cliente, "GET", "/api/v1/auth/yo", 200).json()["rol"] == "recepcion"

        semillas = respuesta(cliente, "GET", "/api/v1/pacientes", 200,
                            params={"q": "Paciente Demo"}).json()
        assert len(semillas) >= 2
        paciente = respuesta(cliente, "POST", "/api/v1/pacientes", 201,
                             json={"nombre_mostrado": "Paciente Demo E2E C-06",
                                   "contacto": "paciente.demo.e2e@example.invalid"}).json()
        assert paciente["nombre_mostrado"].startswith("Paciente Demo")

        base_turno = {
            "paciente_id": paciente["id"], "profesional_id": "profesional-demo-001",
            "box_id": "box-demo-001", "prestacion_id": "prestacion-demo-001",
        }
        turno = respuesta(cliente, "POST", "/api/v1/turnos", 201,
                          json={**base_turno, "inicio": inicio.isoformat()}).json()
        turno_id = turno["id"]
        assert turno["estado"] == "programado" and turno["paciente_id"] == paciente["id"]

        parametros_agenda = {
            "inicio": (inicio - timedelta(hours=1)).isoformat(),
            "fin": (inicio + timedelta(hours=8)).isoformat(),
            "profesional_id": "profesional-demo-001",
        }
        agenda = respuesta(cliente, "GET", "/api/v1/agenda", 200, params=parametros_agenda).json()
        assert any(item["id"] == turno_id and item["estado"] == "programado" for item in agenda)

        bloqueo = respuesta(cliente, "POST", "/api/v1/bloqueos", 201,
                           json={"box_id": "box-demo-001", "inicio": bloqueado.isoformat(),
                                 "fin": (bloqueado + timedelta(hours=1)).isoformat(),
                                 "motivo": "Bloqueo Demo E2E"}).json()
        assert bloqueo["box_id"] == "box-demo-001"
        conflicto = respuesta(cliente, "POST", "/api/v1/turnos", 409,
                             json={**base_turno, "profesional_id": "profesional-demo-002",
                                   "inicio": (bloqueado + timedelta(minutes=15)).isoformat()}).json()
        assert conflicto["codigo"] == "conflicto_bloqueo_box"

        movido = respuesta(cliente, "PATCH", f"/api/v1/turnos/{turno_id}", 200,
                           json={"inicio": reprogramado.isoformat()}).json()
        assert movido["id"] == turno_id and movido["inicio"] == reprogramado.isoformat().replace("+00:00", "Z")

        limite = time.monotonic() + 30
        recordatorios: list[dict[str, object]] = []
        while time.monotonic() < limite:
            recordatorios = respuesta(cliente, "GET", f"/api/v1/turnos/{turno_id}/recordatorios", 200).json()
            if any(item["motivo"] == "creado" and item["turno_id"] == turno_id for item in recordatorios):
                break
            time.sleep(1)
        assert any(item["motivo"] == "creado" and item["turno_id"] == turno_id for item in recordatorios), \
            "El worker no registró el recordatorio simulado dentro del plazo"

        cancelado = respuesta(cliente, "POST", f"/api/v1/turnos/{turno_id}/cancelar", 200).json()
        assert cancelado["estado"] == "cancelado"
        reutilizado = respuesta(cliente, "POST", "/api/v1/turnos", 201,
                               json={**base_turno, "inicio": reprogramado.isoformat()}).json()
        assert reutilizado["id"] != turno_id and reutilizado["estado"] == "programado"
        agenda_final = respuesta(cliente, "GET", "/api/v1/agenda", 200, params=parametros_agenda).json()
        estados = {item["id"]: item["estado"] for item in agenda_final}
        assert estados[turno_id] == "cancelado" and estados[reutilizado["id"]] == "programado"
