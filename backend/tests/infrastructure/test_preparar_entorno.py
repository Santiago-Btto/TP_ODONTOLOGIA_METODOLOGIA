"""Preparación local de secretos demo sin exponerlos ni versionarlos."""

import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "preparar_entorno.py"


def ejecutar(destino: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--output", str(destino)],
        capture_output=True,
        text=True,
        check=False,
    )


def leer_valores(destino: Path) -> dict[str, str]:
    return dict(linea.split("=", 1) for linea in destino.read_text(encoding="utf-8").splitlines())


def test_preparacion_crea_secretos_validos_y_no_los_imprime(tmp_path: Path) -> None:
    destino = tmp_path / ".env"

    resultado = ejecutar(destino)

    assert resultado.returncode == 0
    valores = leer_valores(destino)
    assert set(valores) == {"JWT_SECRET", "DEMO_PASSWORD"}
    assert len(valores["JWT_SECRET"]) >= 32
    assert len(valores["DEMO_PASSWORD"]) >= 12
    assert all(valor not in resultado.stdout + resultado.stderr for valor in valores.values())


def test_preparacion_repetida_conserva_credenciales_y_no_las_imprime(tmp_path: Path) -> None:
    destino = tmp_path / ".env"
    assert ejecutar(destino).returncode == 0
    anterior = leer_valores(destino)

    resultado = ejecutar(destino)

    assert resultado.returncode == 0
    assert leer_valores(destino) == anterior
    assert all(valor not in resultado.stdout + resultado.stderr for valor in anterior.values())


def test_preparacion_rechaza_archivo_incompleto_sin_sobrescribirlo(tmp_path: Path) -> None:
    destino = tmp_path / ".env"
    destino.write_text("JWT_SECRET=secreto-incompleto\n", encoding="utf-8")

    resultado = ejecutar(destino)

    assert resultado.returncode != 0
    assert "Configuración local incompleta o inválida" in resultado.stderr
    assert destino.read_text(encoding="utf-8") == "JWT_SECRET=secreto-incompleto\n"
    assert "secreto-incompleto" not in resultado.stdout + resultado.stderr


def test_preparacion_rechaza_clave_debil_y_contrasena_corta(tmp_path: Path) -> None:
    destino = tmp_path / ".env"
    destino.write_text("JWT_SECRET=corta\nDEMO_PASSWORD=corta\n", encoding="utf-8")

    resultado = ejecutar(destino)

    assert resultado.returncode != 0
    assert "Configuración local incompleta o inválida" in resultado.stderr
    assert destino.read_text(encoding="utf-8") == "JWT_SECRET=corta\nDEMO_PASSWORD=corta\n"
