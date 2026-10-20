"""Manejo centralizado de rutas del proyecto."""
from pathlib import Path

# Antes: subíamos 3 niveles desde src/utils/paths.py
# Ahora: subimos 4 niveles desde src/mi_automatizador/utils/paths.py
RAIZ = Path(__file__).resolve().parent.parent.parent.parent

CARPETA_INPUT = RAIZ / "input"
CARPETA_OUTPUT = RAIZ / "output"
CARPETA_LOGS = RAIZ / "logs"
ARCHIVO_CONFIG = RAIZ / "config" / "settings.json"


def asegurar_carpetas():
    for carpeta in (CARPETA_INPUT, CARPETA_OUTPUT, CARPETA_LOGS):
        carpeta.mkdir(parents=True, exist_ok=True)