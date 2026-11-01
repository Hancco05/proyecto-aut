"""Punto de entrada para PyInstaller."""
import sys
from pathlib import Path

# Añadir src al path para que PyInstaller pueda encontrar el paquete mi_automatizador
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mi_automatizador.cli import main

if __name__ == "__main__":
    main()