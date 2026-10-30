"""Verifica si hay una versión nueva disponible."""
import json
import logging
import urllib.request
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger("automatizador")


@dataclass
class UpdateInfo:
    """Información sobre una actualización disponible."""
    latest_version: str
    current_version: str
    download_url: str
    release_notes: str
    min_version_required: str
    sha256: str

    @property
    def is_newer(self):
        return _comparar_versiones(self.latest_version, self.current_version) > 0

    @property
    def is_forced(self):
        return _comparar_versiones(self.current_version, self.min_version_required) < 0


def _comparar_versiones(v1, v2):
    """Compara dos versiones semánticas. Retorna 1 si v1>v2, -1 si v1<v2, 0 si iguales."""
    partes1 = [int(p) for p in v1.split(".")]
    partes2 = [int(p) for p in v2.split(".")]
    for a, b in zip(partes1, partes2):
        if a > b:
            return 1
        if a < b:
            return -1
    return 0


def _leer_manifest(url):
    """Lee el JSON del servidor (soporta file:// y https://)."""
    with urllib.request.urlopen(url, timeout=10) as respuesta:
        return json.loads(respuesta.read().decode("utf-8"))


def consultar_actualizacion(version_manifest_url, version_actual):
    """
    Consulta si hay una actualización.
    Devuelve UpdateInfo o None si no hay nada nuevo o hay error.
    """
    try:
        data = _leer_manifest(version_manifest_url)
        info = UpdateInfo(
            latest_version=data["latest_version"],
            current_version=version_actual,
            download_url=data["download_url"],
            release_notes=data.get("release_notes", ""),
            min_version_required=data.get("min_version_required", version_actual),
            sha256=data.get("sha256", ""),
        )

        if info.is_newer:
            logger.info(f"Actualización disponible: {info.latest_version}")
            return info

        logger.info(f"Sin actualizaciones. Versión actual: {version_actual}")
        return None

    except Exception as e:
        logger.warning(f"No se pudo consultar el servidor de versiones: {e}")
        return None