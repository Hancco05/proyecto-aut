"""Tests para el handler de CSV."""
import csv
from mi_automatizador.core import csv_handler


def test_convertir_genera_archivo(excel_temporal, carpeta_output_temporal, monkeypatch):
    """Verifica que se genera el CSV en la ruta esperada."""
    from mi_automatizador.core import common
    monkeypatch.setattr(common, "CARPETA_OUTPUT", carpeta_output_temporal)

    resultado = csv_handler.convertir(excel_temporal)

    assert resultado is not None
    assert resultado.exists()
    assert resultado.suffix == ".csv"


def test_contenido_correcto(excel_temporal, carpeta_output_temporal, monkeypatch):
    """Verifica que el contenido del CSV coincide con el Excel."""
    from mi_automatizador.core import common
    monkeypatch.setattr(common, "CARPETA_OUTPUT", carpeta_output_temporal)

    resultado = csv_handler.convertir(excel_temporal)

    with open(resultado, encoding="utf-8") as f:
        filas = list(csv.reader(f))

    assert filas[0] == ["Nombre", "Edad", "Ciudad"]
    assert filas[1] == ["Ana", "28", "Santiago"]
    assert len(filas) == 4  # 1 encabezado + 3 filas


def test_excel_vacio_no_falla(excel_vacio, carpeta_output_temporal, monkeypatch):
    """Un Excel vacío no debe romper el programa."""
    from mi_automatizador.core import common
    monkeypatch.setattr(common, "CARPETA_OUTPUT", carpeta_output_temporal)

    resultado = csv_handler.convertir(excel_vacio)
    assert resultado is not None
    assert resultado.exists()