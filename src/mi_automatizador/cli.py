"""Interfaz de línea de comandos del automatizador."""
import argparse
import logging
import sys
from pathlib import Path

from .core import csv_handler, word_handler, pdf_handler
from .ui.menu import ejecutar as ejecutar_menu
from .utils.logger import configurar_logger
from .utils.paths import asegurar_carpetas, CARPETA_INPUT, CARPETA_OUTPUT


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


def main():
    """Punto de entrada principal."""
    parser = construir_parser()
    args = parser.parse_args()

    asegurar_carpetas()
    logger = configurar_logger()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

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