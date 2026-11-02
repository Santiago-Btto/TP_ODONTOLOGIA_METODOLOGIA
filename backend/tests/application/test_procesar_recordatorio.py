"""Pruebas unitarias de procesamiento y consulta de recordatorios simulados (C-16)."""

from dataclasses import replace
from datetime import UTC, datetime
from types import TracebackType
from typing import Self

import pytest

from app.application.procesar_recordatorio import (
    ConsultarRecordatoriosTurno,
    ProcesarSiguienteRecordatorio,
)
from app.domain.recordatorios import MotivoRecordatorio, RecordatorioEnviado, TareaRecordatorio
from app.domain.turnos import EstadoTurno, Paciente, RecursoInexistenteError, Turno
from tests.datos_demo import BOX, PACIENTE, PRESTACION, PROFESIONAL

AHORA = datetime(2030, 1, 10, 8, 15, tzinfo=UTC)
TURNO_ACTIVO = Turno(
    id="turno-demo-001",
    paciente_id=PACIENTE.id,
    profesional_id=PROFESIONAL.id,
    box_id=BOX.id,
    prestacion_id=PRESTACION.id,
    inicio=datetime(2030, 1, 10, 9, 0, tzinfo=UTC),
    fin=datetime(2030, 1, 10, 9, 30, tzinfo=UTC),
    estado=EstadoTurno.PROGRAMADO,
)


class ColaEnMemoria:
    def __init__(self, tareas: list[TareaRecordatorio] | None = None) -> None:
        self.tareas: list[TareaRecordatorio] = list(tareas or [])

    def encolar(self, tarea: TareaRecordatorio) -> None:
        self.tareas.append(tarea)

    def desencolar(self) -> TareaRecordatorio | None:
        return self.tareas.pop(0) if self.tareas else None


class NotificadorSimuladoEspia:
    def __init__(self) -> None:
        self.envios: list[RecordatorioEnviado] = []

    def enviar_recordatorio(
        self,
        turno: Turno,
        paciente: Paciente,
        motivo: MotivoRecordatorio,
        enviado_en: datetime,
    ) -> RecordatorioEnviado:
        registro = RecordatorioEnviado(
            turno_id=turno.id,
            motivo=motivo,
            destinatario=paciente.nombre_mostrado,
            enviado_en=enviado_en,
        )
        self.envios.append(registro)
        return registro


class RecursosMemoria:
    def __init__(self) -> None:
        self.pacientes = {PACIENTE.id: PACIENTE}

    def paciente(self, id_: str) -> Paciente | None:
        return self.pacientes.get(id_)


class TurnosMemoria:
    def __init__(self, turnos: list[Turno]) -> None:
        self.datos = {t.id: t for t in turnos}

    def obtener(self, turno_id: str) -> Turno | None:
        return self.datos.get(turno_id)


class RecordatoriosMemoria:
    def __init__(self) -> None:
        self.confirmados: dict[tuple[str, MotivoRecordatorio], RecordatorioEnviado] = {}
        self.pendientes: list[RecordatorioEnviado] = []

    def obtener(self, turno_id: str, motivo: MotivoRecordatorio) -> RecordatorioEnviado | None:
        return self.confirmados.get((turno_id, motivo))

    def agregar(self, recordatorio: RecordatorioEnviado) -> RecordatorioEnviado:
        con_id = replace(recordatorio, id=len(self.confirmados) + len(self.pendientes) + 1)
        self.pendientes.append(con_id)
        return con_id

    def listar_por_turno(self, turno_id: str) -> list[RecordatorioEnviado]:
        items = [r for r in self.confirmados.values() if r.turno_id == turno_id]
        return sorted(items, key=lambda r: (r.enviado_en, r.id or 0))


class UoWRecordatoriosMemoria:
    def __init__(self, turnos: list[Turno]) -> None:
        self.recursos = RecursosMemoria()
        self.turnos = TurnosMemoria(turnos)
        self.recordatorios = RecordatoriosMemoria()
        self.commits = 0

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        tipo: type[BaseException] | None,
        error: BaseException | None,
        traza: TracebackType | None,
    ) -> None:
        self.recordatorios.pendientes.clear()

    def commit(self) -> None:
        for item in self.recordatorios.pendientes:
            self.recordatorios.confirmados[(item.turno_id, item.motivo)] = item
        self.recordatorios.pendientes.clear()
        self.commits += 1


# Escenario: Procesar tarea de recordatorio para un turno activo
@pytest.mark.parametrize("estado", [EstadoTurno.PROGRAMADO, EstadoTurno.CONFIRMADO])
@pytest.mark.parametrize("motivo", [MotivoRecordatorio.CREADO, MotivoRecordatorio.CONFIRMADO])
def test_procesa_tarea_para_turno_activo_y_registra_envio_simulado(
    estado: EstadoTurno, motivo: MotivoRecordatorio
) -> None:
    turno = replace(TURNO_ACTIVO, estado=estado)
    uow = UoWRecordatoriosMemoria([turno])
    cola = ColaEnMemoria([TareaRecordatorio(turno_id=turno.id, motivo=motivo)])
    notificador = NotificadorSimuladoEspia()
    caso = ProcesarSiguienteRecordatorio(
        lambda: uow, cola_recordatorios=cola, notificador=notificador, reloj=lambda: AHORA
    )

    resultado = caso.ejecutar()

    assert resultado.procesada is True
    assert resultado.enviado is True
    assert resultado.recordatorio is not None
    assert resultado.recordatorio.turno_id == turno.id
    assert resultado.recordatorio.motivo is motivo
    assert resultado.recordatorio.destinatario == PACIENTE.nombre_mostrado
    assert len(notificador.envios) == 1
    assert uow.commits == 1


# Escenario: Reintento idempotente de la misma tarea de recordatorio
def test_reintento_de_misma_tarea_es_idempotente_y_no_duplica_envio() -> None:
    uow = UoWRecordatoriosMemoria([TURNO_ACTIVO])
    tarea = TareaRecordatorio(turno_id=TURNO_ACTIVO.id, motivo=MotivoRecordatorio.CREADO)
    cola = ColaEnMemoria([tarea, tarea])
    notificador = NotificadorSimuladoEspia()
    caso = ProcesarSiguienteRecordatorio(
        lambda: uow, cola_recordatorios=cola, notificador=notificador, reloj=lambda: AHORA
    )

    primero = caso.ejecutar()
    segundo = caso.ejecutar()

    assert primero.enviado is True
    assert segundo.procesada is True
    assert segundo.enviado is False
    assert segundo.recordatorio == primero.recordatorio
    assert len(notificador.envios) == 1
    assert len(uow.recordatorios.listar_por_turno(TURNO_ACTIVO.id)) == 1


# Escenario: Turno cancelado antes de que el worker procese su recordatorio
def test_omite_recordatorio_si_el_turno_fue_cancelado() -> None:
    cancelado = TURNO_ACTIVO.cancelar()
    uow = UoWRecordatoriosMemoria([cancelado])
    cola = ColaEnMemoria([TareaRecordatorio(turno_id=cancelado.id, motivo=MotivoRecordatorio.CREADO)])
    notificador = NotificadorSimuladoEspia()
    caso = ProcesarSiguienteRecordatorio(
        lambda: uow, cola_recordatorios=cola, notificador=notificador, reloj=lambda: AHORA
    )

    resultado = caso.ejecutar()

    assert resultado.procesada is True
    assert resultado.enviado is False
    assert resultado.recordatorio is None
    assert notificador.envios == []
    assert uow.commits == 0


# Escenario: Tarea de recordatorio para un turno inexistente o cola vacía
def test_omite_recordatorio_si_turno_no_existe_o_cola_esta_vacia() -> None:
    uow = UoWRecordatoriosMemoria([])
    cola = ColaEnMemoria([TareaRecordatorio(turno_id="turno-inexistente", motivo=MotivoRecordatorio.CREADO)])
    notificador = NotificadorSimuladoEspia()
    caso = ProcesarSiguienteRecordatorio(
        lambda: uow, cola_recordatorios=cola, notificador=notificador, reloj=lambda: AHORA
    )

    inexistente = caso.ejecutar()
    vacia = caso.ejecutar()

    assert (inexistente.procesada, inexistente.enviado) == (True, False)
    assert (vacia.procesada, vacia.enviado) == (False, False)
    assert notificador.envios == []


def test_consultar_recordatorios_devuelve_envios_o_falla_si_turno_no_existe() -> None:
    uow = UoWRecordatoriosMemoria([TURNO_ACTIVO])
    cola = ColaEnMemoria([
        TareaRecordatorio(turno_id=TURNO_ACTIVO.id, motivo=MotivoRecordatorio.CREADO),
        TareaRecordatorio(turno_id=TURNO_ACTIVO.id, motivo=MotivoRecordatorio.CONFIRMADO),
    ])
    notificador = NotificadorSimuladoEspia()
    procesador = ProcesarSiguienteRecordatorio(
        lambda: uow, cola_recordatorios=cola, notificador=notificador, reloj=lambda: AHORA
    )
    procesador.ejecutar()
    procesador.ejecutar()

    consulta = ConsultarRecordatoriosTurno(lambda: uow)
    lista = consulta.ejecutar(TURNO_ACTIVO.id)

    assert [r.motivo for r in lista] == [MotivoRecordatorio.CREADO, MotivoRecordatorio.CONFIRMADO]

    with pytest.raises(RecursoInexistenteError):
        consulta.ejecutar("turno-inexistente")
