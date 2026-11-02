"""Puertos que el caso de uso necesita. Los implementa la infraestructura (SQLAlchemy) o los tests."""

from datetime import datetime
from types import TracebackType
from typing import Protocol, Self

from app.domain.bloqueos import BloqueoDeDisponibilidad
from app.domain.recordatorios import MotivoRecordatorio, RecordatorioEnviado, TareaRecordatorio
from app.domain.turnos import Box, HistorialDeCambio, Paciente, Prestacion, Profesional, Turno


class RepositorioPacientes(Protocol):
    def obtener(self, id_: str) -> Paciente | None:
        """Devuelve el paciente por identificador, o `None` si no existe."""
        ...

    def obtener_por_contacto(self, contacto: str) -> Paciente | None:
        """Devuelve el paciente cuyo contacto coincide (ignorando mayúsculas/espacios), o `None`."""
        ...

    def agregar(self, paciente: Paciente) -> None:
        """Registra un nuevo paciente en la transacción actual."""
        ...

    def buscar(self, consulta: str | None = None) -> list[Paciente]:
        """Lista pacientes ordenados por `nombre_mostrado` e `id`, filtrando opcionalmente por `consulta`."""
        ...


class RepositorioRecursos(Protocol):
    def paciente(self, id_: str) -> Paciente | None: ...

    def profesional(self, id_: str) -> Profesional | None: ...

    def box(self, id_: str) -> Box | None: ...

    def prestacion(self, id_: str) -> Prestacion | None: ...

    def bloquear(self, profesional_id: str | None, box_id: str | None) -> None:
        """Bloquea las filas de recursos hasta el fin de la transacción."""
        ...


class RepositorioTurnos(Protocol):
    def obtener(self, turno_id: str) -> Turno | None:
        """Lee el turno por su identificador sin bloquear fila; `None` si no existe."""
        ...

    def activos_que_se_solapan(
        self, profesional_id: str, box_id: str, inicio: datetime, fin: datetime
    ) -> list[Turno]:
        """Turnos activos del profesional o del box que intersectan [inicio, fin)."""
        ...

    def agregar(self, turno: Turno) -> None: ...

    def obtener_para_actualizar(self, turno_id: str) -> Turno | None:
        """Lee el turno y bloquea su fila hasta commit/rollback; `None` si no existe."""
        ...

    def actualizar(self, turno: Turno) -> None:
        """Reemplaza estado, intervalo y recursos del turno ya existente."""
        ...

    def activos_del_recurso_que_se_solapan(
        self, profesional_id: str | None, box_id: str | None, inicio: datetime, fin: datetime
    ) -> list[Turno]:
        """Turnos activos del único recurso indicado que intersectan el intervalo."""
        ...


class RepositorioBloqueos(Protocol):
    def que_se_solapan(
        self, profesional_id: str, box_id: str, inicio: datetime, fin: datetime
    ) -> list[BloqueoDeDisponibilidad]: ...

    def agregar(self, bloqueo: BloqueoDeDisponibilidad) -> None: ...


class RepositorioHistoriales(Protocol):
    def agregar(self, historial: HistorialDeCambio) -> None: ...


class RepositorioRecordatorios(Protocol):
    def obtener(self, turno_id: str, motivo: MotivoRecordatorio) -> RecordatorioEnviado | None:
        """Devuelve el recordatorio ya registrado para `(turno_id, motivo)`, o `None`."""
        ...

    def agregar(self, recordatorio: RecordatorioEnviado) -> RecordatorioEnviado:
        """Registra un envío simulado de recordatorio dentro de la transacción actual."""
        ...

    def listar_por_turno(self, turno_id: str) -> list[RecordatorioEnviado]:
        """Lista los recordatorios enviados de un turno en orden cronológico ascendente."""
        ...


class ColaRecordatorios(Protocol):
    def encolar(self, tarea: TareaRecordatorio) -> None:
        """Encola una tarea de recordatorio para procesamiento asíncrono."""
        ...

    def desencolar(self) -> TareaRecordatorio | None:
        """Extrae la siguiente tarea pendiente de la cola, o `None` si está vacía."""
        ...


class ColaRecordatoriosNoOp:
    """Implementación nula por defecto cuando no se configura una cola externa."""

    def encolar(self, tarea: TareaRecordatorio) -> None:
        return None

    def desencolar(self) -> TareaRecordatorio | None:
        return None


class NotificadorRecordatorios(Protocol):
    def enviar_recordatorio(
        self,
        turno: Turno,
        paciente: Paciente,
        motivo: MotivoRecordatorio,
        enviado_en: datetime,
    ) -> RecordatorioEnviado:
        """Simula el envío del recordatorio y devuelve el registro generado."""
        ...


class LectorAgenda(Protocol):
    def en_rango(
        self,
        inicio: datetime,
        fin: datetime,
        profesional_id: str | None = None,
        box_id: str | None = None,
    ) -> list[Turno]:
        """Turnos que intersectan [inicio, fin), filtrados opcionalmente y ordenados por inicio ascendente."""
        ...


class UnidadDeTrabajo(Protocol):
    """Transacción: lo agregado sólo se persiste con `commit`; salir sin commit descarta todo."""

    recursos: RepositorioRecursos
    pacientes: RepositorioPacientes
    turnos: RepositorioTurnos
    historiales: RepositorioHistoriales
    bloqueos: RepositorioBloqueos
    recordatorios: RepositorioRecordatorios

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        tipo: type[BaseException] | None,
        error: BaseException | None,
        traza: TracebackType | None,
    ) -> None: ...

    def commit(self) -> None: ...
