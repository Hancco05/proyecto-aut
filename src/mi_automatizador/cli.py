"""Interfaz de línea de comandos del automatizador."""
import argparse
import json
import logging
import sys
from pathlib import Path

from .core import csv_handler, word_handler, pdf_handler
from .ui.menu import ejecutar as ejecutar_menu
from .utils.logger import configurar_logger
from .utils.paths import asegurar_carpetas, CARPETA_INPUT, CARPETA_OUTPUT
from .updater.checker import consultar_actualizacion
from .updater.downloader import descargar_actualizacion
from .updater.installer import lanzar_updater


CONVERSORES = {
    "pdf": pdf_handler,
    "word": word_handler,
    "csv": csv_handler,
}


def construir_parser():
    """Construye el parser de argumentos."""
    parser = argparse.ArgumentParser(
        prog="mi-automatizador",
        description="Convierte archivos Excel a PDF, Word o CSV.",
    )

    parser.add_argument(
        "-i", "--input",
        type=Path,
        default=CARPETA_INPUT,
        help="Carpeta o archivo de entrada (por defecto: input/)",
    )

    parser.add_argument(
        "-o", "--output",
        choices=["pdf", "word", "csv"],
        help="Formato de salida. Si se omite, se abre el menú interactivo.",
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Muestra información detallada",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="mi-automatizador 3.0.0",
    )

    return parser


def procesar_archivo(ruta, formato, logger):
    """Convierte un solo archivo al formato indicado."""
    modulo = CONVERSORES[formato]
    logger.info(f"Procesando {ruta.name} -> {formato.upper()}")
    try:
        resultado = modulo.convertir(ruta)
        if resultado:
            print(f"✅ {ruta.name} -> {resultado.name}")
        else:
            print(f"⚠️ No se generó salida para {ruta.name}")
    except Exception as e:
        logger.exception("Error al convertir")
        print(f"❌ Error en {ruta.name}: {e}")


def _ruta_carpeta_app():
    """
    Devuelve la carpeta donde está el ejecutable (si es .exe)
    o la raíz del proyecto (si corre en desarrollo).
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent.parent


def buscar_actualizaciones():
    """
    Consulta al servidor si hay versión nueva.
    Si hay, la descarga y lanza updater.exe.
    Retorna True si lanzó una actualización (la app debe cerrarse).
    """
    from . import __version__

    carpeta_app = _ruta_carpeta_app()
    config_path = carpeta_app / "config" / "updater_config.json"

    if not config_path.exists():
        return False

    try:
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)
    except (json.JSONDecodeError, OSError):
        return False

    if not config.get("check_on_startup", True):
        return False

    info = consultar_actualizacion(config["version_manifest_url"], __version__)
    if not info:
        return False

    if info.is_forced:
        print(f"⚠️ Actualización obligatoria disponible: {info.latest_version}")
    else:
        print(f"\n🔄 Nueva versión disponible: {info.latest_version}")
        if info.release_notes:
            print(f"   Notas: {info.release_notes}")
        respuesta = input("¿Actualizar ahora? (s/n): ").strip().lower()
        if respuesta != "s":
            print("Continuando con la versión actual...")
            return False

    print(f"⬇️ Descargando {info.latest_version}...")
    ruta_zip = descargar_actualizacion(info.download_url, info.sha256)
    if not ruta_zip:
        print("❌ Error descargando la actualización.")
        return False

    ruta_updater = carpeta_app / config["updater_executable_name"]

    if lanzar_updater(ruta_zip, ruta_updater):
        print("✅ Actualización en curso. La app se reiniciará en unos segundos.")
        return True

    print("❌ No se pudo lanzar el updater.")
    return False


def main():
    """Punto de entrada principal."""
    parser = construir_parser()
    args = parser.parse_args()

    asegurar_carpetas()
    logger = configurar_logger()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Buscar actualizaciones SOLO cuando corre como .exe compilado
    # (evita que se actualice mientras desarrollas)
    if getattr(sys, "frozen", False):
        if buscar_actualizaciones():
            sys.exit(0)

    # Sin --output: modo menú interactivo
    if args.output is None:
        logger.info("Modo interactivo")
        ejecutar_menu()
        return

    # Con --output: modo batch
    entrada = args.input
    if not entrada.exists():
        print(f"❌ No existe: {entrada}")
        sys.exit(1)

    if entrada.is_file():
        archivos = [entrada]
    else:
        archivos = [
            f for f in entrada.iterdir()
            if f.suffix.lower() in (".xlsx", ".xlsm")
        ]

    if not archivos:
        print(f"⚠️ No se encontraron archivos Excel en {entrada}")
        sys.exit(0)

    logger.info(f"Modo batch: {len(archivos)} archivo(s) -> {args.output}")
    for archivo in archivos:
        procesar_archivo(archivo, args.output, logger)

    logger.info("Batch completado")


if __name__ == "__main__":
    main()