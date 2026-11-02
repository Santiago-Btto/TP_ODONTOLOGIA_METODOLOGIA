"""Worker síncrono para procesar tareas de recordatorio desde Redis (C-16).

Uso:
    python -m app.infrastructure.worker_recordatorios --una-vez
"""

import argparse
import os
import time
from datetime import UTC, datetime

from app.application.procesar_recordatorio import ProcesarSiguienteRecordatorio
from app.infrastructure.db import crear_fabrica_de_sesiones, crear_motor
from app.infrastructure.recordatorios_redis import ColaRecordatoriosRedis, NotificadorSimulado
from app.infrastructure.unidad_de_trabajo import UnidadDeTrabajoSQLAlchemy


def procesar_pendientes(procesador: ProcesarSiguienteRecordatorio, limite: int = 100) -> int:
    """Procesa hasta `limite` tareas disponibles en la cola y devuelve cuántas se extrajeron."""
    procesadas = 0
    for _ in range(limite):
        resultado = procesador.ejecutar()
        if not resultado.procesada:
            break
        procesadas += 1
    return procesadas


def construir_procesador_desde_entorno() -> ProcesarSiguienteRecordatorio:
    database_url = os.environ["DATABASE_URL"]
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    motor = crear_motor(database_url)
    fabrica = crear_fabrica_de_sesiones(motor)
    cola = ColaRecordatoriosRedis.desde_url(redis_url)
    return ProcesarSiguienteRecordatorio(
        lambda: UnidadDeTrabajoSQLAlchemy(fabrica),
        cola_recordatorios=cola,
        notificador=NotificadorSimulado(),
        reloj=lambda: datetime.now(UTC),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Worker de recordatorios simulados de turnos.")
    parser.add_argument(
        "--una-vez",
        action="store_true",
        help="Procesa las tareas actualmente encoladas y finaliza.",
    )
    parser.add_argument(
        "--intervalo-segundos",
        type=float,
        default=2.0,
        help="Segundos de espera cuando la cola está vacía en modo continuo.",
    )
    args = parser.parse_args(argv)
    procesador = construir_procesador_desde_entorno()

    if args.una_vez:
        procesar_pendientes(procesador)
        return 0

    while True:
        cantidad = procesar_pendientes(procesador)
        if cantidad == 0:
            time.sleep(args.intervalo_segundos)


if __name__ == "__main__":
    raise SystemExit(main())
