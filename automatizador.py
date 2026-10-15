"""
Automatizador de Archivos v1.0
Convierte Excel a PDF, Word y CSV.
"""

import os
import csv
from pathlib import Path

from openpyxl import load_workbook
from docx import Document
from docx.shared import Pt



CARPETA_INPUT = Path("input")
CARPETA_OUTPUT = Path("output")



def listar_excel():
    """Devuelve una lista de archivos Excel en la carpeta input/."""
    if not CARPETA_INPUT.exists():
        return []
    return [f for f in CARPETA_INPUT.iterdir() if f.suffix.lower() in (".xlsx", ".xlsm")]


def elegir_archivo(archivos):
    """Muestra los archivos y deja al usuario elegir uno."""
    print("\nArchivos disponibles:")
    for i, archivo in enumerate(archivos, start=1):
        print(f"  {i}. {archivo.name}")

    while True:
        try:
            opcion = int(input("\nElige el número del archivo: "))
            if 1 <= opcion <= len(archivos):
                return archivos[opcion - 1]
            print("Número fuera de rango.")
        except ValueError:
            print("Debes ingresar un número.")


def asegurar_output():
    """Crea la carpeta output/ si no existe."""
    CARPETA_OUTPUT.mkdir(exist_ok=True)


def excel_a_csv(ruta_excel):
    """Convierte la primera hoja de un Excel a CSV."""
    wb = load_workbook(ruta_excel, data_only=True)
    hoja = wb.active

    nombre_salida = CARPETA_OUTPUT / f"{ruta_excel.stem}.csv"

    with open(nombre_salida, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for fila in hoja.iter_rows(values_only=True):
            writer.writerow(fila)

    wb.close()
    print(f"✅ CSV generado: {nombre_salida}")


def excel_a_word(ruta_excel):
    """Convierte la primera hoja de un Excel a una tabla en Word."""
    wb = load_workbook(ruta_excel, data_only=True)
    hoja = wb.active

    doc = Document()
    doc.add_heading(ruta_excel.stem, level=1)

    filas = list(hoja.iter_rows(values_only=True))
    if not filas:
        print("⚠️ La hoja está vacía.")
        return

    columnas = len(filas[0])
    tabla = doc.add_table(rows=len(filas), cols=columnas)
    tabla.style = "Light Grid Accent 1"

    for i, fila in enumerate(filas):
        for j, valor in enumerate(fila):
            celda = tabla.cell(i, j)
            celda.text = str(valor) if valor is not None else ""
            for p in celda.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(9)

    nombre_salida = CARPETA_OUTPUT / f"{ruta_excel.stem}.docx"
    doc.save(nombre_salida)
    wb.close()
    print(f"✅ Word generado: {nombre_salida}")


def excel_a_pdf(ruta_excel):
    """
    Convierte Excel a PDF.
    NOTA: Requiere tener Excel instalado en Windows.
    Usa win32com para controlar Excel.
    """
    try:
        import win32com.client
    except ImportError:
        print("⚠️ Falta la librería pywin32. Instálala con: pip install pywin32")
        return

    ruta_absoluta = ruta_excel.resolve()
    nombre_salida = (CARPETA_OUTPUT / f"{ruta_excel.stem}.pdf").resolve()

    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False

    try:
        wb = excel.Workbooks.Open(str(ruta_absoluta))
        wb.ExportAsFixedFormat(0, str(nombre_salida))  # 0 = PDF
        wb.Close(False)
        print(f"✅ PDF generado: {nombre_salida}")
    finally:
        excel.Quit()



def menu():
    print("\n" + "=" * 45)
    print("   AUTOMATIZADOR DE ARCHIVOS v1.0")
    print("=" * 45)
    print("1. Convertir Excel a PDF")
    print("2. Convertir Excel a Word")
    print("3. Convertir Excel a CSV")
    print("4. Salir")


def main():
    asegurar_output()

    while True:
        menu()
        opcion = input("\nElige una opción: ").strip()

        if opcion == "4":
            print("👋 Hasta luego.")
            break

        if opcion not in ("1", "2", "3"):
            print("⚠️ Opción inválida.")
            continue

        archivos = listar_excel()
        if not archivos:
            print(f"⚠️ No hay archivos Excel en '{CARPETA_INPUT}/'. Coloca uno y vuelve a intentar.")
            continue

        archivo = elegir_archivo(archivos)

        try:
            if opcion == "1":
                excel_a_pdf(archivo)
            elif opcion == "2":
                excel_a_word(archivo)
            elif opcion == "3":
                excel_a_csv(archivo)
        except Exception as e:
            print(f"❌ Error al procesar el archivo: {e}")


if __name__ == "__main__":
    main()