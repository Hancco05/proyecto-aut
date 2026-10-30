"""
Programa independiente que reemplaza la app y la reinicia.
Se compila como updater.exe separado de Automatizador.exe.
"""
import argparse
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path


def esperar_a_que_cierre_app(ruta_app, timeout=30):
    """Espera a que la app principal se cierre (Windows la bloqueará si está abierta)."""
    inicio = time.time()
    while time.time() - inicio < timeout:
        try:
            with open(ruta_app, "ab"):
                return True
        except PermissionError:
            time.sleep(0.5)
    return False


def extraer_zip(ruta_zip, carpeta_destino):
    """Extrae el .zip de actualización."""
    with zipfile.ZipFile(ruta_zip, "r") as zf:
        zf.extractall(carpeta_destino)


def copiar_archivos(origen, destino):
    """Copia el contenido del origen al destino, sobreescribiendo."""
    for item in origen.iterdir():
        target = destino / item.name
        if item.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


def main():
    parser = argparse.ArgumentParser(description="Updater del Automatizador")
    parser.add_argument("--zip", required=True, help="Ruta al .zip de la actualización")
    parser.add_argument("--target", required=True, help="Ruta al ejecutable/app actual")
    parser.add_argument("--restart", required=True, help="Ruta a reiniciar al terminar")
    args = parser.parse_args()

    ruta_zip = Path(args.zip)
    ruta_target = Path(args.target).resolve()
    ruta_restart = Path(args.restart).resolve()

    carpeta_app = ruta_target.parent
    carpeta_temp = carpeta_app / "_update_temp"

    try:
        # 1. Esperar a que la app se cierre
        print(f"Esperando a que cierre {ruta_target.name}...")
        if not esperar_a_que_cierre_app(ruta_target):
            print("Timeout esperando cierre. Abortando.")
            sys.exit(1)

        # 2. Extraer ZIP
        print(f"Extrayendo {ruta_zip.name}...")
        if carpeta_temp.exists():
            shutil.rmtree(carpeta_temp)
        carpeta_temp.mkdir()
        extraer_zip(ruta_zip, carpeta_temp)

        # 3. Copiar archivos nuevos sobre la carpeta de la app
        print(f"Copiando archivos a {carpeta_app}...")
        copiar_archivos(carpeta_temp, carpeta_app)

        # 4. Limpiar
        shutil.rmtree(carpeta_temp)
        ruta_zip.unlink(missing_ok=True)

        # 5. Reiniciar la app
        print(f"Reiniciando {ruta_restart.name}...")
        subprocess.Popen([str(ruta_restart)])

    except Exception as e:
        print(f"Error durante la actualización: {e}")
        input("Presiona Enter para cerrar...")
        sys.exit(1)


if __name__ == "__main__":
    main()