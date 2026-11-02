"""Matriz RBAC propuesta en `knowledge-base/03_actores_y_roles.md` (C-08)."""

import pytest

from app.domain.autorizacion import (
    AccesoDenegadoError,
    Actor,
    Permiso,
    Rol,
    verificar_alcance_agenda,
    verificar_permiso,
)

RECEPCION = Actor("usuario-demo-recepcion", Rol.RECEPCION)
RESPONSABLE = Actor("usuario-demo-responsable", Rol.RESPONSABLE)
ODONTOLOGO = Actor("usuario-demo-odontologo", Rol.ODONTOLOGO, profesional_id="profesional-demo-001")


@pytest.mark.parametrize("actor", [RECEPCION, RESPONSABLE])
@pytest.mark.parametrize("permiso", list(Permiso))
def test_recepcion_y_responsable_tienen_todos_los_permisos(actor: Actor, permiso: Permiso) -> None:
    verificar_permiso(actor, permiso)


def test_odontologo_puede_consultar_la_agenda() -> None:
    verificar_permiso(ODONTOLOGO, Permiso.CONSULTAR_AGENDA)


@pytest.mark.parametrize("permiso", [p for p in Permiso if p is not Permiso.CONSULTAR_AGENDA])
def test_odontologo_no_puede_modificar(permiso: Permiso) -> None:
    with pytest.raises(AccesoDenegadoError) as error:
        verificar_permiso(ODONTOLOGO, permiso)

    assert error.value.codigo == "acceso_denegado"


def test_odontologo_consulta_su_propia_agenda() -> None:
    verificar_alcance_agenda(ODONTOLOGO, "profesional-demo-001")


@pytest.mark.parametrize("actor,filtro", [
    (ODONTOLOGO, None),
    (ODONTOLOGO, "profesional-demo-002"),
    (Actor("usuario-demo-sin-vinculo", Rol.ODONTOLOGO), "profesional-demo-001"),
])
def test_odontologo_no_consulta_agendas_ajenas(actor: Actor, filtro: str | None) -> None:
    with pytest.raises(AccesoDenegadoError):
        verificar_alcance_agenda(actor, filtro)


@pytest.mark.parametrize("actor", [RECEPCION, RESPONSABLE])
@pytest.mark.parametrize("filtro", [None, "profesional-demo-002"])
def test_recepcion_y_responsable_consultan_cualquier_agenda(actor: Actor, filtro: str | None) -> None:
    verificar_alcance_agenda(actor, filtro)
