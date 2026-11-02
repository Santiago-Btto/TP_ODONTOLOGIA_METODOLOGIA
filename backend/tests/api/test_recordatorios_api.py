"""Contrato HTTP de recordatorios simulados y resiliencia con Redis caído (C-16)."""

from collections.abc import Callable
from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app.api.main import crear_app
from app.application.procesar_recordatorio import ProcesarSiguienteRecordatorio
from app.domain.autorizacion import Rol
from app.domain.recordatorios import MotivoRecordatorio, TareaRecordatorio
from app.infrastructure.recordatorios_redis import (
    ColaRecordatoriosMemoria,
    ColaRecordatoriosRedis,
    NotificadorSimulado,
)
from app.infrastructure.seguridad import ConfiguracionSeguridad
from app.infrastructure.unidad_de_trabajo import UnidadDeTrabajoSQLAlchemy
from app.infrastructure.worker_recordatorios import procesar_pendientes

URL_TURNOS = "/api/v1/turnos"


def _cuerpo_turno(**cambios: str) -> dict[str, str]:
    base = {
        "paciente_id": "paciente-demo-001",
        "profesional_id": "profesional-demo-001",
        "box_id": "box-demo-001",
        "prestacion_id": "prestacion-demo-001",
        "inicio": "2030-01-10T09:00:00-03:00",
    }
    base.update(cambios)
    return base


# Escenario: Consulta exitosa de recordatorios simulados tras crear, confirmar y ejecutar worker
def test_flujo_crear_confirmar_worker_y_consultar_recordatorios_por_api(
    fabrica: sessionmaker[Session],
    seguridad: ConfiguracionSeguridad,
    token_de: Callable[[Rol], str],
) -> None:
    cola = ColaRecordatoriosMemoria()
    app = crear_app(fabrica, seguridad, cola_recordatorios=cola)

    with TestClient(app, headers={"Authorization": f"Bearer {token_de(Rol.RECEPCION)}"}) as cliente:
        alta = cliente.post(URL_TURNOS, json=_cuerpo_turno())
        assert alta.status_code == 201
        turno_id = str(alta.json()["id"])

        conf = cliente.post(f"{URL_TURNOS}/{turno_id}/confirmar")
        assert conf.status_code == 200

        # Encolar duplicado adicional para verificar idempotencia extremo a extremo
        cola.encolar(TareaRecordatorio(turno_id=turno_id, motivo=MotivoRecordatorio.CREADO))

        procesador = ProcesarSiguienteRecordatorio(
            lambda: UnidadDeTrabajoSQLAlchemy(fabrica),
            cola_recordatorios=cola,
            notificador=NotificadorSimulado(),
            reloj=lambda: datetime(2030, 1, 10, 12, 0, tzinfo=UTC),
        )
        assert procesar_pendientes(procesador) == 3

        respuesta = cliente.get(f"{URL_TURNOS}/{turno_id}/recordatorios")
        assert respuesta.status_code == 200
        datos = respuesta.json()
        assert [r["motivo"] for r in datos] == ["creado", "confirmado"]
        assert all(r["turno_id"] == turno_id for r in datos)
        assert all(r["destinatario"] == "Paciente Demo Ficticia 001" for r in datos)

    with TestClient(app, headers={"Authorization": f"Bearer {token_de(Rol.RESPONSABLE)}"}) as resp_cli:
        assert resp_cli.get(f"{URL_TURNOS}/{turno_id}/recordatorios").status_code == 200


# Escenario: Turno cancelado antes del worker no genera recordatorio en la API
def test_turno_cancelado_antes_del_worker_devuelve_lista_vacia_de_recordatorios(
    fabrica: sessionmaker[Session],
    seguridad: ConfiguracionSeguridad,
    token_de: Callable[[Rol], str],
) -> None:
    cola = ColaRecordatoriosMemoria()
    app = crear_app(fabrica, seguridad, cola_recordatorios=cola)

    with TestClient(app, headers={"Authorization": f"Bearer {token_de(Rol.RECEPCION)}"}) as cliente:
        alta = cliente.post(URL_TURNOS, json=_cuerpo_turno())
        turno_id = str(alta.json()["id"])
        assert cliente.post(f"{URL_TURNOS}/{turno_id}/cancelar").status_code == 200

        procesador = ProcesarSiguienteRecordatorio(
            lambda: UnidadDeTrabajoSQLAlchemy(fabrica),
            cola_recordatorios=cola,
            notificador=NotificadorSimulado(),
            reloj=lambda: datetime(2030, 1, 10, 12, 0, tzinfo=UTC),
        )
        assert procesar_pendientes(procesador) == 1

        respuesta = cliente.get(f"{URL_TURNOS}/{turno_id}/recordatorios")
        assert respuesta.status_code == 200
        assert respuesta.json() == []


# Escenario: Consulta de recordatorios para un turno inexistente o sin permisos
def test_consultar_recordatorios_valida_existencia_autenticacion_y_rbac(
    cliente: TestClient,
    cliente_anonimo: TestClient,
    cliente_como: Callable[[Rol], TestClient],
) -> None:
    inexistente = cliente.get(f"{URL_TURNOS}/turno-inexistente/recordatorios")
    assert inexistente.status_code == 404
    assert inexistente.json()["codigo"] == "recurso_inexistente"

    anonimo = cliente_anonimo.get(f"{URL_TURNOS}/turno-demo-1/recordatorios")
    assert anonimo.status_code == 401
    assert anonimo.json()["codigo"] == "no_autenticado"

    odontologo = cliente_como(Rol.ODONTOLOGO).get(f"{URL_TURNOS}/turno-demo-1/recordatorios")
    assert odontologo.status_code == 403
    assert odontologo.json()["codigo"] == "acceso_denegado"


# Escenario: Crear turno, confirmar turno y consultar agenda con Redis caído (RN-EX-02)
def test_agenda_y_turnos_funcionan_normalmente_con_redis_caido(
    fabrica: sessionmaker[Session],
    seguridad: ConfiguracionSeguridad,
    token_de: Callable[[Rol], str],
) -> None:
    cola_caida = ColaRecordatoriosRedis.desde_url("redis://127.0.0.1:63999/0")
    app = crear_app(fabrica, seguridad, cola_recordatorios=cola_caida)

    with TestClient(app, headers={"Authorization": f"Bearer {token_de(Rol.RECEPCION)}"}) as cliente:
        alta = cliente.post(URL_TURNOS, json=_cuerpo_turno())
        assert alta.status_code == 201
        turno_id = str(alta.json()["id"])

        conf = cliente.post(f"{URL_TURNOS}/{turno_id}/confirmar")
        assert conf.status_code == 200
        assert conf.json()["estado"] == "confirmado"

        agenda = cliente.get(
            "/api/v1/agenda",
            params={
                "inicio": "2030-01-10T08:00:00-03:00",
                "fin": "2030-01-10T12:00:00-03:00",
            },
        )
        assert agenda.status_code == 200
        assert [t["id"] for t in agenda.json()] == [turno_id]
