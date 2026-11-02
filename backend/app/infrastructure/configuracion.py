"""Configuración de infraestructura para Redis y servicios auxiliares (C-16)."""

import os

from app.application.puertos import ColaRecordatorios, ColaRecordatoriosNoOp
from app.infrastructure.recordatorios_redis import ColaRecordatoriosRedis


def url_de_redis(variable: str = "REDIS_URL") -> str | None:
    valor = os.environ.get(variable)
    if valor is None or not valor.strip():
        return None
    return valor.strip()


def crear_cola_recordatorios_desde_entorno(variable: str = "REDIS_URL") -> ColaRecordatorios:
    url = url_de_redis(variable)
    if url is None:
        return ColaRecordatoriosNoOp()
    return ColaRecordatoriosRedis.desde_url(url)
