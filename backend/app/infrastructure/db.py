import os

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.modelos import Base


def url_de_base(variable: str = "DATABASE_URL") -> str:
    url = os.environ.get(variable)
    if not url:
        raise RuntimeError(f"Falta la variable de entorno {variable} (ver backend/.env.example).")
    return url


def crear_motor(url: str) -> Engine:
    return create_engine(url, pool_pre_ping=True)


def crear_fabrica_de_sesiones(motor: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=motor, expire_on_commit=False)


def crear_esquema(motor: Engine) -> None:
    """Crea tablas y restricciones si no existen. Las migraciones versionadas llegan con C-07."""
    Base.metadata.create_all(motor)
