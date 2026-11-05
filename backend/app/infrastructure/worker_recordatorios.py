"""Worker síncrono para procesar tareas de recordatorio desde Redis (C-16).

Uso:
    python -m app.infrastructure.worker_recordatorios --una-vez
"""

import argparse
import logging
import os
import time
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Protocol

from redis.exceptions import RedisError

from app.application.procesar_recordatorio import ProcesarSiguienteRecordatorio, ResultadoProcesamientoRecordatorio
from app.infrastructure.db import crear_fabrica_de_sesiones, crear_motor
from app.infrastructure.recordatorios_redis import ColaRecordatoriosRedis, NotificadorSimulado
from app.infrastructure.unidad_de_trabajo import UnidadDeTrabajoSQLAlchemy


logger = logging.getLogger(__name__)


class ProcesadorDeCola(Protocol):
    def ejecutar(self) -> ResultadoProcesamientoRecordatorio: ...


def procesar_pendientes(procesador: ProcesadorDeCola, limite: int = 100) -> int:
    """Procesa hasta `limite` tareas disponibles en la cola y devuelve cuántas se extrajeron."""
    procesadas = 0
    for _ in range(limite):
        resultado = procesador.ejecutar()
        if not resultado.procesada:
            break
        procesadas += 1
    return procesadas


def ejecutar_bucle(
    procesador: ProcesadorDeCola,
    dormir: Callable[[float], None],
    intervalo_segundos: float,
    ciclos: int | None = None,
    espera_maxima: float = 30.0,
) -> None:
    """Procesa la cola en forma continua sin terminar ante una caída transitoria de Redis.

    Con Redis inaccesible, registra el error y reintenta con espera creciente (hasta
    `espera_maxima`); al recuperarse vuelve al intervalo normal. `ciclos` limita las
    vueltas para las pruebas; `None` ejecuta indefinidamente.
    """
    espera_error = intervalo_segundos
    vuelta = 0
    while ciclos is None or vuelta < ciclos:
        vuelta += 1
        try:
            resultado = procesador.ejecutar()
        except RedisError as error:
            logger.warning("Redis no disponible (%s); reintento en %.0f s.", type(error).__name__, espera_error)
            dormir(espera_error)
            espera_error = min(espera_error * 2, espera_maxima)
            continue
        espera_error = intervalo_segundos
        if not resultado.procesada:
            dormir(intervalo_segundos)


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
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    procesador = construir_procesador_desde_entorno()

    if args.una_vez:
        procesar_pendientes(procesador)
        return 0

    ejecutar_bucle(procesador, dormir=time.sleep, intervalo_segundos=args.intervalo_segundos)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
