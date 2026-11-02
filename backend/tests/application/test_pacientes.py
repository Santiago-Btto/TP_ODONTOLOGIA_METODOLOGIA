"""Pruebas unitarias de los casos de uso RegistrarPaciente y BuscarPacientes (C-17)."""

from types import TracebackType
from typing import Self

import pytest

from app.application.pacientes import BuscarPacientes, NuevoPaciente, RegistrarPaciente
from app.application.puertos import RepositorioPacientes
from app.domain.turnos import DatosPacienteInvalidosError, Paciente, PacienteDuplicadoError


class _RepositorioPacientesFalso(RepositorioPacientes):
    def __init__(self, iniciales: list[Paciente] | None = None) -> None:
        self._por_id: dict[str, Paciente] = {p.id: p for p in (iniciales or [])}

    def obtener(self, id_: str) -> Paciente | None:
        return self._por_id.get(id_)

    def obtener_por_contacto(self, contacto: str) -> Paciente | None:
        normalizado = contacto.strip().lower()
        for paciente in self._por_id.values():
            if paciente.contacto_normalizado == normalizado:
                return paciente
        return None

    def agregar(self, paciente: Paciente) -> None:
        if paciente.id in self._por_id:
            raise PacienteDuplicadoError(f"Ya existe un paciente con id '{paciente.id}'.")
        if paciente.contacto_normalizado is not None and self.obtener_por_contacto(paciente.contacto_normalizado):
            raise PacienteDuplicadoError("Ya existe un paciente registrado con ese contacto.")
        self._por_id[paciente.id] = paciente

    def buscar(self, consulta: str | None = None) -> list[Paciente]:
        ordenados = sorted(self._por_id.values(), key=lambda p: (p.nombre_mostrado, p.id))
        if consulta is None or not consulta.strip():
            return ordenados
        termino = consulta.strip().lower()
        return [
            p
            for p in ordenados
            if termino in p.nombre_mostrado.lower()
            or termino in p.id.lower()
            or (p.contacto is not None and termino in p.contacto.lower())
        ]


class _UnidadDeTrabajoPacientesFalsa:
    def __init__(self, iniciales: list[Paciente] | None = None) -> None:
        self.pacientes = _RepositorioPacientesFalso(iniciales)
        self.commits = 0

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        tipo: type[BaseException] | None,
        error: BaseException | None,
        traza: TracebackType | None,
    ) -> None:
        return None

    def commit(self) -> None:
        self.commits += 1


def test_registrar_paciente_con_id_autogenerado_y_contacto_confirma_transaccion() -> None:
    uow = _UnidadDeTrabajoPacientesFalsa()
    caso_de_uso = RegistrarPaciente(uow)

    creado = caso_de_uso.ejecutar(
        NuevoPaciente(
            nombre_mostrado="  Paciente Demo Ficticio 010  ",
            contacto="  +54 9 11 0000-0010  ",
        )
    )

    assert creado.id.startswith("paciente-")
    assert creado.nombre_mostrado == "Paciente Demo Ficticio 010"
    assert creado.contacto == "+54 9 11 0000-0010"
    assert uow.commits == 1
    assert uow.pacientes.obtener(creado.id) == creado


def test_registrar_paciente_con_id_explicito_y_sin_contacto_persiste_null() -> None:
    uow = _UnidadDeTrabajoPacientesFalsa()
    caso_de_uso = RegistrarPaciente(uow)

    creado = caso_de_uso.ejecutar(
        NuevoPaciente(
            id="paciente-demo-011",
            nombre_mostrado="Paciente Demo Ficticia 011",
            contacto="   ",
        )
    )

    assert creado == Paciente(id="paciente-demo-011", nombre_mostrado="Paciente Demo Ficticia 011", contacto=None)
    assert uow.commits == 1


def test_registrar_paciente_con_id_duplicado_lanza_error_y_no_confirma() -> None:
    existente = Paciente("paciente-demo-001", "Paciente Demo Ficticia 001")
    uow = _UnidadDeTrabajoPacientesFalsa([existente])
    caso_de_uso = RegistrarPaciente(uow)

    with pytest.raises(PacienteDuplicadoError):
        caso_de_uso.ejecutar(
            NuevoPaciente(
                id="paciente-demo-001",
                nombre_mostrado="Paciente Demo Otra",
            )
        )

    assert uow.commits == 0
    assert uow.pacientes.obtener("paciente-demo-001") == existente


def test_registrar_paciente_con_contacto_duplicado_insensible_a_mayusculas_lanza_error() -> None:
    existente = Paciente(
        "paciente-demo-001",
        "Paciente Demo Ficticia 001",
        "paciente.demo.001@example.invalid",
    )
    uow = _UnidadDeTrabajoPacientesFalsa([existente])
    caso_de_uso = RegistrarPaciente(uow)

    with pytest.raises(PacienteDuplicadoError):
        caso_de_uso.ejecutar(
            NuevoPaciente(
                nombre_mostrado="Paciente Demo Ficticio 002",
                contacto="  PACIENTE.DEMO.001@Example.Invalid ",
            )
        )

    assert uow.commits == 0


def test_registrar_dos_pacientes_sin_contacto_es_valido() -> None:
    uow = _UnidadDeTrabajoPacientesFalsa()
    caso_de_uso = RegistrarPaciente(uow)

    primero = caso_de_uso.ejecutar(NuevoPaciente(nombre_mostrado="Paciente Demo Sin Contacto 1"))
    segundo = caso_de_uso.ejecutar(NuevoPaciente(nombre_mostrado="Paciente Demo Sin Contacto 2"))

    assert primero.id != segundo.id
    assert primero.contacto is None
    assert segundo.contacto is None
    assert uow.commits == 2


@pytest.mark.parametrize(
    "entrada",
    [
        NuevoPaciente(nombre_mostrado="   "),
        NuevoPaciente(id="   ", nombre_mostrado="Paciente Demo Ficticio"),
    ],
)
def test_registrar_paciente_con_datos_invalidos_lanza_error_y_no_confirma(
    entrada: NuevoPaciente,
) -> None:
    uow = _UnidadDeTrabajoPacientesFalsa()
    caso_de_uso = RegistrarPaciente(uow)

    with pytest.raises(DatosPacienteInvalidosError):
        caso_de_uso.ejecutar(entrada)

    assert uow.commits == 0


def test_buscar_pacientes_filtra_por_nombre_id_o_contacto_y_ordena() -> None:
    ana = Paciente("paciente-demo-002", "Paciente Demo Ana", "+54 9 11 0000-0101")
    bruno = Paciente("paciente-demo-001", "Paciente Demo Bruno", "bruno.demo@example.invalid")
    uow = _UnidadDeTrabajoPacientesFalsa([bruno, ana])
    buscador = BuscarPacientes(uow)

    assert buscador.ejecutar() == [ana, bruno]
    assert buscador.ejecutar("   ") == [ana, bruno]
    assert buscador.ejecutar("ANA") == [ana]
    assert buscador.ejecutar("0101") == [ana]
    assert buscador.ejecutar("bruno.demo") == [bruno]
    assert buscador.ejecutar("inexistente") == []
