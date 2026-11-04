"""Inicialización repetible del MVP con datos exclusivamente ficticios.

Uso: python -m app.infrastructure.bootstrap_demo
Requiere DATABASE_URL y DEMO_PASSWORD por entorno; no imprime credenciales.
"""

import os

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.domain.autorizacion import Rol
from app.infrastructure.crear_usuario import LARGO_MINIMO_CONTRASENA, crear_usuario
from app.infrastructure.db import crear_esquema, crear_fabrica_de_sesiones, crear_motor, url_de_base
from app.infrastructure.modelos import UsuarioModelo
from app.infrastructure.seguridad import HasherArgon2
from app.infrastructure.semillas import cargar_semillas


def inicializar_demo(fabrica: sessionmaker[Session], contrasena: str) -> None:
    if len(contrasena) < LARGO_MINIMO_CONTRASENA:
        raise ValueError("DEMO_PASSWORD falta o es demasiado corta.")
    hasher = HasherArgon2()
    with fabrica() as sesion:
        existente = sesion.scalar(
            select(UsuarioModelo).where(UsuarioModelo.nombre_usuario == "recepcion.demo")
        )
        if existente is not None and (
            existente.rol != Rol.RECEPCION.value
            or not existente.activo
            or existente.profesional_id is not None
            or not hasher.verificar(contrasena, existente.hash_contrasena)
        ):
            raise ValueError("El usuario recepcion.demo no coincide con la configuración local.")
        cargar_semillas(sesion)
        if existente is None:
            crear_usuario(sesion, hasher, "recepcion.demo", contrasena, Rol.RECEPCION)


def main() -> int:
    contrasena = os.environ.get("DEMO_PASSWORD", "")
    if len(contrasena) < LARGO_MINIMO_CONTRASENA:
        raise SystemExit("DEMO_PASSWORD falta o es demasiado corta.")
    motor = crear_motor(url_de_base())
    try:
        crear_esquema(motor)
        inicializar_demo(crear_fabrica_de_sesiones(motor), contrasena)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    finally:
        motor.dispose()
    print("Datos Demo y usuario de recepción listos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
