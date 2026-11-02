"""Pruebas de integración de `ColaRecordatoriosRedis`, `NotificadorSimulado` y worker (C-16)."""

from datetime import UTC, datetime

import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.application.cambiar_estado_turno import (
    CancelarTurno,
    ConfirmarTurno,
    SolicitudCambioDeEstado,
)
from app.application.crear_turno import CrearTurno, SolicitudCrearTurno
from app.application.procesar_recordatorio import (
    ConsultarRecordatoriosTurno,
    ProcesarSiguienteRecordatorio,
)
from app.domain.recordatorios import MotivoRecordatorio, TareaRecordatorio
from app.infrastructure.recordatorios_redis import (
    CLAVE_COLA_DEFECTO,
    ColaRecordatoriosMemoria,
    ColaRecordatoriosRedis,
    NotificadorSimulado,
)
from app.infrastructure.unidad_de_trabajo import UnidadDeTrabajoSQLAlchemy
from app.infrastructure.worker_recordatorios import procesar_pendientes
from tests.datos_demo import BOX, PACIENTE, PRESTACION, PROFESIONAL

AHORA = datetime(2030, 1, 10, 8, 0, tzinfo=UTC)
INICIO = datetime(2030, 1, 10, 9, 0, tzinfo=UTC)


class ClienteRedisFalso:
    """Doble de cliente Redis que implementa `rpush` y `lpop` con la misma firma que `redis.Redis`."""

    def __init__(self) -> None:
        self.listas: dict[str, list[str]] = {}

    def rpush(self, clave: str, valor: str) -> int:
        lista = self.listas.setdefault(clave, [])
        lista.append(valor)
        return len(lista)

    def lpop(self, clave: str) -> str | None:
        lista = self.listas.get(clave, [])
        return lista.pop(0) if lista else None


def test_cola_recordatorios_redis_serializa_y_desencola_fifo() -> None:
    cliente = ClienteRedisFalso()
    cola = ColaRecordatoriosRedis(cliente)
    t1 = TareaRecordatorio(turno_id="turno-demo-1", motivo=MotivoRecordatorio.CREADO)
    t2 = TareaRecordatorio(turno_id="turno-demo-1", motivo=MotivoRecordatorio.CONFIRMADO)

    cola.encolar(t1)
    cola.encolar(t2)

    assert len(cliente.listas[CLAVE_COLA_DEFECTO]) == 2
    assert cola.desencolar() == t1
    assert cola.desencolar() == t2
    assert cola.desencolar() is None


def test_cola_recordatorios_redis_desde_url_inaccesible_falla_al_conectar_y_crear_turno_lo_absorbe(
    fabrica: sessionmaker[Session],
) -> None:
    cola_caida = ColaRecordatoriosRedis.desde_url("redis://127.0.0.1:63999/0")
    uow_fn = lambda: UnidadDeTrabajoSQLAlchemy(fabrica)
    crear = CrearTurno(uow_fn, reloj=lambda: AHORA, cola_recordatorios=cola_caida)

    creado = crear.ejecutar(
        SolicitudCrearTurno(
            id="turno-demo-redis-caido",
            paciente_id=PACIENTE.id,
            profesional_id=PROFESIONAL.id,
            box_id=BOX.id,
            prestacion_id=PRESTACION.id,
            inicio=INICIO,
        )
    )

    assert creado.id == "turno-demo-redis-caido"
    with uow_fn() as uow:
        assert uow.turnos.obtener("turno-demo-redis-caido") is not None


def test_worker_procesa_cola_con_notificador_simulado_idempotencia_y_omite_cancelados(
    fabrica: sessionmaker[Session],
) -> None:
    cola = ColaRecordatoriosRedis(ClienteRedisFalso())
    notificador = NotificadorSimulado()
    uow_fn = lambda: UnidadDeTrabajoSQLAlchemy(fabrica)

    crear = CrearTurno(uow_fn, reloj=lambda: AHORA, cola_recordatorios=cola)
    confirmar = ConfirmarTurno(uow_fn, reloj=lambda: AHORA, cola_recordatorios=cola)
    cancelar = CancelarTurno(uow_fn, reloj=lambda: AHORA)

    # 1. Crear y confirmar turno 1 -> encola 'creado' y 'confirmado'
    crear.ejecutar(
        SolicitudCrearTurno(
            id="turno-demo-w1",
            paciente_id=PACIENTE.id,
            profesional_id=PROFESIONAL.id,
            box_id=BOX.id,
            prestacion_id=PRESTACION.id,
            inicio=INICIO,
        )
    )
    confirmar.ejecutar(SolicitudCambioDeEstado("turno-demo-w1"))
    # Encolar duplicado manual de 'creado' para comprobar idempotencia
    cola.encolar(TareaRecordatorio(turno_id="turno-demo-w1", motivo=MotivoRecordatorio.CREADO))

    # 2. Crear y luego cancelar turno 2 antes de correr el worker
    crear.ejecutar(
        SolicitudCrearTurno(
            id="turno-demo-w2",
            paciente_id=PACIENTE.id,
            profesional_id=PROFESIONAL.id,
            box_id=BOX.id,
            prestacion_id=PRESTACION.id,
            inicio=datetime(2030, 1, 10, 10, 0, tzinfo=UTC),
        )
    )
    cancelar.ejecutar(SolicitudCambioDeEstado("turno-demo-w2"))

    procesador = ProcesarSiguienteRecordatorio(
        uow_fn,
        cola_recordatorios=cola,
        notificador=notificador,
        reloj=lambda: AHORA,
    )
    cantidad = procesar_pendientes(procesador)

    assert cantidad == 4
    consulta = ConsultarRecordatoriosTurno(uow_fn)
    enviados_w1 = consulta.ejecutar("turno-demo-w1")
    enviados_w2 = consulta.ejecutar("turno-demo-w2")

    assert [r.motivo for r in enviados_w1] == [
        MotivoRecordatorio.CREADO,
        MotivoRecordatorio.CONFIRMADO,
    ]
    assert enviados_w2 == []
