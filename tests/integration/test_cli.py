"""Tests de integración para la CLI."""
import subprocess
import sys


def test_version():
    """El flag --version debe funcionar."""
    resultado = subprocess.run(
        [sys.executable, "-m", "mi_automatizador", "--version"],
        capture_output=True,
        text=True,
    )
    assert resultado.returncode == 0
    assert "3.0.0" in resultado.stdout


def test_help():
    """El flag --help debe mostrar los flags disponibles."""
    resultado = subprocess.run(
        [sys.executable, "-m", "mi_automatizador", "--help"],
        capture_output=True,
        text=True,
    )
    assert resultado.returncode == 0
    assert "--output" in resultado.stdout
    assert "--input" in resultado.stdout
    assert "--verbose" in resultado.stdout


def test_batch_pdf(excel_temporal, carpeta_output_temporal, tmp_path, monkeypatch):
    """El modo batch debe convertir todos los Excel de la carpeta."""
    import shutil
    from mi_automatizador.utils import paths

    # Preparar carpeta de entrada con 2 archivos
    carpeta_input = tmp_path / "input"
    carpeta_input.mkdir()
    shutil.copy(excel_temporal, carpeta_input / "a.xlsx")
    shutil.copy(excel_temporal, carpeta_input / "b.xlsx")

    monkeypatch.setattr(paths, "CARPETA_INPUT", carpeta_input)
    monkeypatch.setattr(paths, "CARPETA_OUTPUT", carpeta_output_temporal)

    # Nota: PDF requiere Excel instalado; aquí solo verificamos CSV para evitar dependencia
    from mi_automatizador.cli import procesar_archivo, CONVERSORES
    import logging
    logger = logging.getLogger("test")

    for archivo in carpeta_input.iterdir():
        if archivo.suffix == ".xlsx":
            procesar_archivo(archivo, "csv", logger)

    archivos_generados = list(carpeta_output_temporal.glob("*.csv"))
    assert len(archivos_generados) == 2