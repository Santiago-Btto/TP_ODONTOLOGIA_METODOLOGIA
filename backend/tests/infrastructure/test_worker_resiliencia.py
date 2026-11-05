"""El worker de recordatorios sobrevive a caídas transitorias de Redis (C-16, RN-EX-02)."""

from redis.exceptions import ConnectionError as RedisConnectionError

from app.application.procesar_recordatorio import ResultadoProcesamientoRecordatorio
from app.infrastructure.worker_recordatorios import ejecutar_bucle


class ProcesadorGuionado:
    """Devuelve, en orden, los resultados o excepciones indicados; luego cola vacía."""

    def __init__(self, guion: list[object]) -> None:
        self._guion = list(guion)
        self.llamadas = 0

    def ejecutar(self) -> ResultadoProcesamientoRecordatorio:
        self.llamadas += 1
        if not self._guion:
            return ResultadoProcesamientoRecordatorio(procesada=False, enviado=False)
        siguiente = self._guion.pop(0)
        if isinstance(siguiente, Exception):
            raise siguiente
        assert isinstance(siguiente, ResultadoProcesamientoRecordatorio)
        return siguiente


PROCESADA = ResultadoProcesamientoRecordatorio(procesada=True, enviado=True)


def test_worker_continua_tras_perder_la_conexion_con_redis() -> None:
    procesador = ProcesadorGuionado([RedisConnectionError("caída"), RedisConnectionError("caída"), PROCESADA])
    esperas: list[float] = []

    ejecutar_bucle(procesador, dormir=esperas.append, intervalo_segundos=2.0, ciclos=4)

    assert procesador.llamadas == 4  # siguió consultando la cola tras los errores
    assert esperas[:2] == [2.0, 4.0]  # reintento con espera creciente


def test_worker_reinicia_la_espera_cuando_redis_vuelve() -> None:
    procesador = ProcesadorGuionado([RedisConnectionError("caída"), PROCESADA, RedisConnectionError("caída")])
    esperas: list[float] = []

    ejecutar_bucle(procesador, dormir=esperas.append, intervalo_segundos=2.0, ciclos=3)

    # La segunda caída espera de nuevo 2 s (no 4 s): la recuperación reinició el retroceso.
    assert esperas == [2.0, 2.0]


def test_worker_limita_la_espera_maxima() -> None:
    procesador = ProcesadorGuionado([RedisConnectionError("caída")] * 10)
    esperas: list[float] = []

    ejecutar_bucle(procesador, dormir=esperas.append, intervalo_segundos=2.0, ciclos=10, espera_maxima=30.0)

    assert max(esperas) == 30.0
