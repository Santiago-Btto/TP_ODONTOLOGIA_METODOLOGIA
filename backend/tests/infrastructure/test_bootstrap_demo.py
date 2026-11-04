"""Bootstrap idempotente del entorno demo sobre PostgreSQL real."""

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.bootstrap_demo import inicializar_demo
from app.infrastructure.modelos import (
    BoxModelo, PacienteModelo, PrestacionModelo, ProfesionalModelo, UsuarioModelo,
)
from app.infrastructure.seguridad import HasherArgon2


def limpiar_datos_demo(fabrica: sessionmaker[Session]) -> None:
    with fabrica() as sesion:
        sesion.execute(text("TRUNCATE usuarios, prestaciones, boxes, profesionales, pacientes CASCADE"))
        sesion.commit()


def test_bootstrap_inserta_semillas_y_usuario_demo(fabrica: sessionmaker[Session]) -> None:
    limpiar_datos_demo(fabrica)

    inicializar_demo(fabrica, "contrasena-demo-larga-001")

    with fabrica() as sesion:
        usuario = sesion.scalar(select(UsuarioModelo).where(UsuarioModelo.nombre_usuario == "recepcion.demo"))
        assert usuario is not None
        assert usuario.rol == "recepcion" and usuario.activo and usuario.profesional_id is None
        assert HasherArgon2().verificar("contrasena-demo-larga-001", usuario.hash_contrasena)
        assert sesion.scalar(select(func.count()).select_from(PacienteModelo)) == 2
        assert sesion.scalar(select(func.count()).select_from(ProfesionalModelo)) == 2
        assert sesion.scalar(select(func.count()).select_from(BoxModelo)) == 2
        assert sesion.scalar(select(func.count()).select_from(PrestacionModelo)) == 1
        assert all(p.nombre_mostrado.startswith("Paciente Demo") for p in sesion.scalars(select(PacienteModelo)))


def test_bootstrap_repetido_conserva_identidad_hash_y_conteos(fabrica: sessionmaker[Session]) -> None:
    limpiar_datos_demo(fabrica)
    inicializar_demo(fabrica, "contrasena-demo-larga-001")
    with fabrica() as sesion:
        primero = sesion.scalar(select(UsuarioModelo).where(UsuarioModelo.nombre_usuario == "recepcion.demo"))
        assert primero is not None
        identidad, hash_anterior = primero.id, primero.hash_contrasena

    inicializar_demo(fabrica, "contrasena-demo-larga-001")

    with fabrica() as sesion:
        usuario = sesion.scalar(select(UsuarioModelo).where(UsuarioModelo.nombre_usuario == "recepcion.demo"))
        assert usuario is not None
        assert (usuario.id, usuario.hash_contrasena) == (identidad, hash_anterior)
        assert sesion.scalar(select(func.count()).select_from(UsuarioModelo)) == 1
        assert sesion.scalar(select(func.count()).select_from(PacienteModelo)) == 2


def test_bootstrap_rechaza_contrasena_distinta_sin_cambiar_hash(fabrica: sessionmaker[Session]) -> None:
    limpiar_datos_demo(fabrica)
    inicializar_demo(fabrica, "contrasena-demo-larga-001")
    with fabrica() as sesion:
        anterior = sesion.scalar(select(UsuarioModelo.hash_contrasena))

    try:
        inicializar_demo(fabrica, "otra-contrasena-larga-002")
    except ValueError as error:
        assert "no coincide" in str(error)
        assert "otra-contrasena-larga-002" not in str(error)
    else:
        raise AssertionError("Debe rechazar una contraseña que no corresponde al usuario existente")

    with fabrica() as sesion:
        assert sesion.scalar(select(UsuarioModelo.hash_contrasena)) == anterior


def test_bootstrap_rechaza_rol_incorrecto_sin_sobrescribir(fabrica: sessionmaker[Session]) -> None:
    limpiar_datos_demo(fabrica)
    inicializar_demo(fabrica, "contrasena-demo-larga-001")
    with fabrica() as sesion:
        usuario = sesion.scalar(select(UsuarioModelo).where(UsuarioModelo.nombre_usuario == "recepcion.demo"))
        assert usuario is not None
        usuario.rol = "responsable"
        sesion.commit()

    try:
        inicializar_demo(fabrica, "contrasena-demo-larga-001")
    except ValueError as error:
        assert "no coincide" in str(error)
    else:
        raise AssertionError("Debe rechazar un usuario demo de otro rol")

    with fabrica() as sesion:
        assert sesion.scalar(select(UsuarioModelo.rol)) == "responsable"
