"""Adaptadores de cola Redis, cola en memoria y `NotificadorSimulado` (C-16)."""

import json
import logging
from collections import deque
from datetime import datetime
from typing import Protocol

import redis

from app.domain.recordatorios import MotivoRecordatorio, RecordatorioEnviado, TareaRecordatorio
from app.domain.turnos import Paciente, Turno

logger = logging.getLogger(__name__)

CLAVE_COLA_DEFECTO = "turnos:recordatorios:cola"


class ClienteListaRedis(Protocol):
    def rpush(self, clave: str, valor: str) -> object: ...

    def lpop(self, clave: str) -> str | bytes | None: ...


class ColaRecordatoriosRedis:
    """Cola FIFO respaldada por una lista Redis usando serialización JSON."""

    def __init__(self, cliente: ClienteListaRedis, clave_cola: str = CLAVE_COLA_DEFECTO) -> None:
        self._cliente = cliente
        self._clave_cola = clave_cola

    @classmethod
    def desde_url(
        cls,
        redis_url: str,
        clave_cola: str = CLAVE_COLA_DEFECTO,
    ) -> "ColaRecordatoriosRedis":
        cliente = redis.Redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=1.0,
            socket_timeout=1.0,
        )
        return cls(cliente=cliente, clave_cola=clave_cola)

    def encolar(self, tarea: TareaRecordatorio) -> None:
        carga = json.dumps(
            {"turno_id": tarea.turno_id, "motivo": tarea.motivo.value},
            separators=(",", ":"),
        )
        self._cliente.rpush(self._clave_cola, carga)

    def desencolar(self) -> TareaRecordatorio | None:
        crudo = self._cliente.lpop(self._clave_cola)
        if crudo is None:
            return None
        texto = crudo.decode("utf-8") if isinstance(crudo, bytes) else str(crudo)
        datos = json.loads(texto)
        return TareaRecordatorio(
            turno_id=str(datos["turno_id"]),
            motivo=MotivoRecordatorio(str(datos["motivo"])),
        )


class ColaRecordatoriosMemoria:
    """Cola FIFO en memoria para pruebas o ejecución local sin Redis."""

    def __init__(self) -> None:
        self._cola: deque[TareaRecordatorio] = deque()

    def encolar(self, tarea: TareaRecordatorio) -> None:
        self._cola.append(tarea)

    def desencolar(self) -> TareaRecordatorio | None:
        return self._cola.popleft() if self._cola else None


class NotificadorSimulado:
    """Simula el envío de un recordatorio registrando el evento sin llamar a WhatsApp real."""

    def enviar_recordatorio(
        self,
        turno: Turno,
        paciente: Paciente,
        motivo: MotivoRecordatorio,
        enviado_en: datetime,
    ) -> RecordatorioEnviado:
        logger.info(
            "Recordatorio simulado enviado: turno_id=%s motivo=%s destinatario=%s",
            turno.id,
            motivo.value,
            paciente.nombre_mostrado,
        )
        return RecordatorioEnviado(
            turno_id=turno.id,
            motivo=motivo,
            destinatario=paciente.nombre_mostrado,
            enviado_en=enviado_en,
        )
