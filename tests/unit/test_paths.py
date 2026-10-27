"""Tests para el módulo de rutas."""
from mi_automatizador.utils import paths


def test_carpetas_definidas():
    """Todas las rutas deben estar definidas como Path."""
    assert paths.CARPETA_INPUT is not None
    assert paths.CARPETA_OUTPUT is not None
    assert paths.CARPETA_LOGS is not None


def test_asegurar_carpetas_crea_las_que_faltan(tmp_path, monkeypatch):
    """Si las carpetas no existen, asegurar_carpetas las crea."""
    monkeypatch.setattr(paths, "CARPETA_INPUT", tmp_path / "input")
    monkeypatch.setattr(paths, "CARPETA_OUTPUT", tmp_path / "output")
    monkeypatch.setattr(paths, "CARPETA_LOGS", tmp_path / "logs")

    paths.asegurar_carpetas()

    assert (tmp_path / "input").exists()
    assert (tmp_path / "output").exists()
    assert (tmp_path / "logs").exists()