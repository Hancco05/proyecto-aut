"""Fixtures compartidas para todos los tests."""
import pytest
from pathlib import Path
from openpyxl import Workbook


@pytest.fixture
def excel_temporal(tmp_path):
    """
    Crea un archivo Excel temporal con datos de prueba.
    tmp_path es una carpeta temporal que pytest crea y limpia automáticamente.
    """
    ruta = tmp_path / "datos_prueba.xlsx"
    wb = Workbook()
    hoja = wb.active
    hoja.title = "Datos"

    # Encabezados
    hoja.append(["Nombre", "Edad", "Ciudad"])
    # Filas de datos
    hoja.append(["Ana", 28, "Santiago"])
    hoja.append(["Luis", 35, "Valparaíso"])
    hoja.append(["María", 42, "Concepción"])

    wb.save(ruta)
    wb.close()
    return ruta


@pytest.fixture
def excel_vacio(tmp_path):
    """Crea un Excel sin datos para probar casos borde."""
    ruta = tmp_path / "vacio.xlsx"
    wb = Workbook()
    wb.save(ruta)
    wb.close()
    return ruta


@pytest.fixture
def carpeta_output_temporal(tmp_path, monkeypatch):
    """
    Redirige la carpeta output/ a una temporal para no ensuciar el proyecto.
    monkeypatch cambia variables durante el test y las restaura al terminar.
    """
    from mi_automatizador.utils import paths
    carpeta = tmp_path / "output"
    carpeta.mkdir()
    monkeypatch.setattr(paths, "CARPETA_OUTPUT", carpeta)
    return carpeta