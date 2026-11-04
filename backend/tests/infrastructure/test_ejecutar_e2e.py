"""El lanzador comunica fallos de limpieza aunque el recorrido HTTP haya pasado."""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "ejecutar_e2e.py"


def cargar_lanzador() -> ModuleType:
    especificacion = importlib.util.spec_from_file_location("lanzador_e2e_demo", SCRIPT)
    assert especificacion is not None and especificacion.loader is not None
    modulo = importlib.util.module_from_spec(especificacion)
    especificacion.loader.exec_module(modulo)
    return modulo


@pytest.mark.parametrize("fallar_limpieza,estado_esperado", [(False, 0), (True, 1)])
def test_lanzador_reporta_estado_de_limpieza(
    monkeypatch: pytest.MonkeyPatch, fallar_limpieza: bool, estado_esperado: int
) -> None:
    lanzador = cargar_lanzador()
    llamadas: list[str] = []
    monkeypatch.setattr(lanzador, "comprobar_aislamiento", lambda: True)

    def simular_ejecucion(*argumentos: str) -> int:
        llamadas.append(argumentos[0])
        return 1 if fallar_limpieza and argumentos[0] == "down" else 0

    monkeypatch.setattr(lanzador, "ejecutar", simular_ejecucion)

    assert lanzador.main() == estado_esperado
    assert llamadas == ["up", "run", "down"]
