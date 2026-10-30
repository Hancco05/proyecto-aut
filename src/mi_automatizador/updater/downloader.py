"""Descarga el paquete de actualización."""
import hashlib
import logging
import tempfile
import urllib.request
from pathlib import Path

logger = logging.getLogger("automatizador")


def _calcular_sha256(ruta):
    """Calcula el hash SHA256 de un archivo."""
    hash_obj = hashlib.sha256()
    with open(ruta, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def descargar_actualizacion(download_url, sha256_esperado=""):
    """
    Descarga el .zip a una carpeta temporal.
    Verifica el hash si se proporciona.
    Devuelve la ruta al archivo descargado o None si falla.
    """
    try:
        carpeta_temp = Path(tempfile.gettempdir()) / "automatizador_update"
        carpeta_temp.mkdir(exist_ok=True)
        destino = carpeta_temp / "update.zip"

        logger.info(f"Descargando actualización desde {download_url}...")
        urllib.request.urlretrieve(download_url, destino)

        # Verificar integridad si hay hash
        if sha256_esperado and sha256_esperado != "se_rellena_automaticamente":
            hash_real = _calcular_sha256(destino)
            if hash_real != sha256_esperado:
                logger.error("El archivo descargado está corrupto (hash no coincide)")
                destino.unlink()
                return None

        logger.info(f"Descarga completada: {destino}")
        return destino

    except Exception as e:
        logger.error(f"Error al descargar: {e}")
        return None