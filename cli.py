"""
cli.py
Flujo interactivo de extracción: diálogos tkinter + preguntas por consola.
Sólo se importa cuando se ejecuta el programa directamente.
"""

import os
import tkinter as tk
from tkinter import filedialog

from .extractor import PDFExtractor


# ------------------------------------------------------------------
# Helpers tkinter
# ------------------------------------------------------------------

def _seleccionar_archivo() -> str:
    """Abre un diálogo para seleccionar el archivo PDF. Devuelve la ruta."""
    root = tk.Tk()
    root.withdraw()
    ruta = filedialog.askopenfilename(
        title="Selecciona el archivo PDF",
        filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")],
    )
    root.destroy()
    return ruta


def _seleccionar_directorio(directorio_inicial: str = "") -> str:
    """Abre un diálogo para elegir dónde guardar los resultados."""
    root = tk.Tk()
    root.withdraw()
    ruta = filedialog.askdirectory(
        title="Selecciona la carpeta de salida",
        initialdir=directorio_inicial,
    )
    root.destroy()
    return ruta


# ------------------------------------------------------------------
# Preguntas por consola
# ------------------------------------------------------------------

def pedir_opciones(extractor: PDFExtractor) -> None:
    """Pregunta al usuario qué extraer y en qué formato (por consola)."""
    print("\n--- Opciones de extracción ---")
    extractor.extraer_metadatos = input("  ¿Extraer metadatos? (s/n) [s]: ").strip().lower() != "n"
    extractor.extraer_imagenes  = input("  ¿Listar imágenes?   (s/n) [s]: ").strip().lower() != "n"
    extractor.extraer_tablas    = input("  ¿Detectar tablas?    (s/n) [n]: ").strip().lower() == "s"

    print("  Formato del texto: 1) txt  2) json  3) ambos")
    opcion = input("  Elige [1]: ").strip()
    extractor.formato = {"2": "json", "3": "ambos"}.get(opcion, "txt")


def pedir_paginas(extractor: PDFExtractor) -> None:
    """Pregunta qué páginas extraer (por consola). Resultado en extractor.paginas."""
    print(f"\n  El PDF tiene {extractor.total_paginas} páginas.")
    respuesta = input("  Páginas a extraer (ej: 1,3,5) o ENTER para todas: ").strip()
    if not respuesta:
        extractor.paginas = None
        return
    try:
        extractor.paginas = [int(p.strip()) for p in respuesta.split(",") if p.strip()]
    except ValueError:
        print("  [!] Formato incorrecto. Se extraerán TODAS las páginas.")
        extractor.paginas = None


# ------------------------------------------------------------------
# Flujo principal interactivo
# ------------------------------------------------------------------

def ejecutar_interactivo() -> None:
    """Flujo completo de extracción interactiva (tkinter + consola)."""
    extractor = PDFExtractor()

    # 1. Seleccionar PDF (tkinter)
    ruta = _seleccionar_archivo()
    if not ruta:
        print("Cancelado: no se seleccionó ningún archivo.")
        return

    # 2. Abrir PDF
    try:
        extractor.abrir_pdf(ruta)
    except Exception as e:
        print(f"Error al abrir el PDF: {e}")
        return

    print(f"\n Abriendo: {extractor.ruta_pdf}")
    print(f"   Páginas totales: {extractor.total_paginas}")

    # 3. Seleccionar carpeta de salida (tkinter)
    salida_dir = _seleccionar_directorio(os.path.dirname(ruta))
    if not salida_dir:
        print("Cancelado: no se seleccionó carpeta de salida.")
        return
    os.makedirs(salida_dir, exist_ok=True)
    extractor.salida_dir = salida_dir

    # 4. Opciones (consola)
    pedir_opciones(extractor)

    # 5. Páginas (consola)
    pedir_paginas(extractor)

    # 6. Metadatos
    if extractor.extraer_metadatos:
        print("\n METADATOS")
        print("-" * 40)
        extractor.obtener_metadatos()
        for clave, valor in extractor.metadatos.items():
            print(f"  {clave:<22}: {valor}")
        extractor.guardar_json(
            extractor.metadatos,
            os.path.join(salida_dir, f"{extractor.nombre_base}_metadatos.json"),
        )

    # 7. Texto
    modo = "(páginas seleccionadas)" if extractor.paginas else "(todas las páginas)"
    print(f"\n Extrayendo texto {modo}...")
    extractor.obtener_texto()

    if extractor.formato in ("txt", "ambos"):
        extractor.guardar_txt(
            extractor.textos,
            os.path.join(salida_dir, f"{extractor.nombre_base}_texto.txt"),
        )
    if extractor.formato in ("json", "ambos"):
        extractor.guardar_json(
            {str(k): v for k, v in extractor.textos.items()},
            os.path.join(salida_dir, f"{extractor.nombre_base}_texto.json"),
        )

    # 8. Imágenes
    if extractor.extraer_imagenes:
        print("\n Imágenes detectadas por página:")
        extractor.obtener_imagenes()
        if extractor.imagenes:
            for pagina, nombres in extractor.imagenes.items():
                print(f"  Página {pagina}: {', '.join(nombres)}")
            extractor.guardar_json(
                {str(k): v for k, v in extractor.imagenes.items()},
                os.path.join(salida_dir, f"{extractor.nombre_base}_imagenes.json"),
            )
        else:
            print("  (No se encontraron imágenes)")

    # 9. Tablas
    if extractor.extraer_tablas:
        print("\n Detección de tablas simples (heurística):")
        extractor.detectar_tablas()
        if extractor.tablas:
            for pagina, filas in extractor.tablas.items():
                print(f"  Página {pagina}: {len(filas)} filas detectadas")
            extractor.guardar_json(
                extractor.tablas,
                os.path.join(salida_dir, f"{extractor.nombre_base}_tablas.json"),
            )
        else:
            print("  (No se detectaron tablas)")

    # 10. Fin
    print(f"\n ¡Proceso completado!")
    print(f"   Archivos guardados en: {salida_dir}\n")
