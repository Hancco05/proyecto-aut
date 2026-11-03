"""Punto de entrada para PyInstaller."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from mi_automatizador.cli import main

if __name__ == "__main__":
    main()