"""Lanza el updater.exe para aplicar la actualización."""
import logging
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger("automatizador")


def lanzar_updater(ruta_zip, ruta_updater_exe):
    """
    Lanza updater.exe como proceso separado.
    La app principal debe cerrarse después de llamar a esta función.
    """
    if not ruta_updater_exe.exists():
        logger.error(f"No se encuentra updater.exe en {ruta_updater_exe}")
        return False

    # La app principal se está ejecutando desde aquí
    ruta_app_actual = Path(sys.executable) if getattr(sys, "frozen", False) \
                      else Path(sys.argv[0])

    logger.info(f"Lanzando updater: {ruta_updater_exe}")
    logger.info(f"Archivo ZIP: {ruta_zip}")
    logger.info(f"App actual: {ruta_app_actual}")

    subprocess.Popen([
        str(ruta_updater_exe),
        "--zip", str(ruta_zip),
        "--target", str(ruta_app_actual),
        "--restart", str(ruta_app_actual),
    ], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)

    return True