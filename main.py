#!/usr/bin/env python3
"""
extractor_pdf.py
Extrae texto, metadatos, imágenes (nombres) y tablas simples de archivos PDF.
Librería requerida (pura Python): pypdf
    pip install pypdf
Interfaz de selección de archivos: tkinter (sólo para diálogos de ruta)
"""

import json
import os
import sys
import tkinter as tk
from tkinter import filedialog

from pypdf import PdfReader


class PDFExtractor:
    """Extrae y guarda texto, metadatos, imágenes y tablas de un PDF."""

    def __init__(self) -> None:
        # Atributos principales
        self.ruta_pdf: str = ""
        self.nombre_base: str = ""
        self.reader: PdfReader | None = None
        self.total_paginas: int = 0

        # Ruta de salida
        self.salida_dir: str = ""

        # Opciones de extracción
        self.extraer_metadatos: bool = True
        self.extraer_imagenes: bool = True
        self.extraer_tablas: bool = False
        self.formato: str = "txt"          # "txt" | "json" | "ambos"
        self.paginas: list[int] | None = None  # None = todas

        # Resultados intermedios
        self.metadatos: dict = {}
        self.textos: dict[int, str] = {}
        self.imagenes: dict[int, list[str]] = {}
        self.tablas: dict[str, list] = {}

    # ------------------------------------------------------------------
    # Selección de rutas (único uso de tkinter)
    # ------------------------------------------------------------------

    @staticmethod
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

    @staticmethod
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
    # Carga del PDF
    # ------------------------------------------------------------------

    def abrir_pdf(self, ruta: str) -> None:
        """Abre el PDF y carga el reader y los datos básicos."""
        if not os.path.isfile(ruta):
            raise FileNotFoundError(f"El archivo no existe: {ruta}")
        self.ruta_pdf = ruta
        self.nombre_base = os.path.splitext(os.path.basename(ruta))[0]
        self.reader = PdfReader(ruta)
        self.total_paginas = len(self.reader.pages)

    # ------------------------------------------------------------------
    # Extracción
    # ------------------------------------------------------------------

    def obtener_metadatos(self) -> dict:
        """Devuelve los metadatos del documento y los guarda en self.metadatos."""
        meta = self.reader.metadata or {}
        self.metadatos = {
            "titulo":              meta.get("/Title",        ""),
            "autor":               meta.get("/Author",       ""),
            "asunto":              meta.get("/Subject",      ""),
            "creador":             meta.get("/Creator",      ""),
            "productor":           meta.get("/Producer",     ""),
            "fecha_creacion":      meta.get("/CreationDate", ""),
            "fecha_modificacion":  meta.get("/ModDate",      ""),
            "total_paginas":       self.total_paginas,
        }
        return self.metadatos

    def obtener_texto(self) -> dict[int, str]:
        """
        Extrae texto de las páginas indicadas en self.paginas (1-based).
        Si self.paginas es None, extrae todas. Resultado en self.textos.
        """
        resultado: dict[int, str] = {}
        indices = (
            [p - 1 for p in self.paginas]
            if self.paginas
            else range(self.total_paginas)
        )
        for idx in indices:
            if idx < 0 or idx >= self.total_paginas:
                print(f"  [!] Página {idx + 1} fuera de rango, omitiendo.")
                continue
            texto = self.reader.pages[idx].extract_text() or ""
            resultado[idx + 1] = texto
        self.textos = resultado
        return self.textos

    def obtener_imagenes(self) -> dict[int, list[str]]:
        """Lista los nombres de las imágenes (XObject) por página."""
        imagenes: dict[int, list[str]] = {}
        for num, page in enumerate(self.reader.pages, start=1):
            recursos = page.get("/Resources", {})
            xobjects = recursos.get("/XObject", {})
            nombres = [
                nombre
                for nombre, obj in xobjects.items()
                if obj.get("/Subtype") == "/Image"
            ]
            if nombres:
                imagenes[num] = nombres
        self.imagenes = imagenes
        return self.imagenes

    def detectar_tablas(self) -> dict[str, list]:
        """
        Heurística básica: detecta filas donde los campos están
        separados por 2+ espacios consecutivos. Opera sobre self.textos.
        """
        todas: dict[str, list] = {}
        for pagina, texto in self.textos.items():
            filas: list[list[str]] = []
            for linea in texto.splitlines():
                partes = [p.strip() for p in linea.split("  ") if p.strip()]
                if len(partes) >= 2:
                    filas.append(partes)
            if filas:
                todas[str(pagina)] = filas
        self.tablas = todas
        return self.tablas

    # ------------------------------------------------------------------
    # Guardado
    # ------------------------------------------------------------------

    def guardar_txt(self, datos: dict[int, str], ruta_salida: str) -> None:
        """Guarda el texto extraído en un archivo .txt."""
        with open(ruta_salida, "w", encoding="utf-8") as f:
            for pagina, texto in datos.items():
                f.write(f"\n{'='*60}\n")
                f.write(f"  PÁGINA {pagina}\n")
                f.write(f"{'='*60}\n")
                f.write(texto)
                f.write("\n")
        print(f"  → Texto guardado en: {ruta_salida}")

    def guardar_json(self, datos: dict, ruta_salida: str) -> None:
        """Guarda cualquier diccionario como JSON."""
        with open(ruta_salida, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        print(f"  → JSON guardado en: {ruta_salida}")

    # ------------------------------------------------------------------
    # Interacción por consola (sin tkinter)
    # ------------------------------------------------------------------

    def pedir_opciones(self) -> None:
        """Pregunta al usuario qué extraer y en qué formato (por consola)."""
        print("\n--- Opciones de extracción ---")

        self.extraer_metadatos = input("  ¿Extraer metadatos? (s/n) [s]: ").strip().lower() != "n"
        self.extraer_imagenes  = input("  ¿Listar imágenes?   (s/n) [s]: ").strip().lower() != "n"
        self.extraer_tablas    = input("  ¿Detectar tablas?    (s/n) [n]: ").strip().lower() == "s"

        print("  Formato del texto: 1) txt  2) json  3) ambos")
        opcion = input("  Elige [1]: ").strip()
        self.formato = {"2": "json", "3": "ambos"}.get(opcion, "txt")

    def pedir_paginas(self) -> None:
        """Pregunta qué páginas extraer (por consola). Resultado en self.paginas."""
        print(f"\n  El PDF tiene {self.total_paginas} páginas.")
        respuesta = input("  Páginas a extraer (ej: 1,3,5) o ENTER para todas: ").strip()
        if not respuesta:
            self.paginas = None
            return
        try:
            self.paginas = [int(p.strip()) for p in respuesta.split(",") if p.strip()]
        except ValueError:
            print("  [!] Formato incorrecto. Se extraerán TODAS las páginas.")
            self.paginas = None

    # ------------------------------------------------------------------
    # Ejecución principal
    # ------------------------------------------------------------------

    def ejecutar(self) -> None:
        """Flujo completo de extracción interactiva."""

        # 1. Seleccionar PDF (tkinter)
        ruta = self._seleccionar_archivo()
        if not ruta:
            print("Cancelado: no se seleccionó ningún archivo.")
            return

        # 2. Abrir PDF
        try:
            self.abrir_pdf(ruta)
        except Exception as e:
            print(f"Error al abrir el PDF: {e}")
            return

        print(f"\n Abriendo: {self.ruta_pdf}")
        print(f"   Páginas totales: {self.total_paginas}")

        # 3. Seleccionar carpeta de salida (tkinter)
        self.salida_dir = self._seleccionar_directorio(os.path.dirname(ruta))
        if not self.salida_dir:
            print("Cancelado: no se seleccionó carpeta de salida.")
            return
        os.makedirs(self.salida_dir, exist_ok=True)

        # 4. Opciones (consola)
        self.pedir_opciones()

        # 5. Páginas (consola)
        self.pedir_paginas()

        # 6. Metadatos
        if self.extraer_metadatos:
            print("\n METADATOS")
            print("-" * 40)
            self.obtener_metadatos()
            for clave, valor in self.metadatos.items():
                print(f"  {clave:<22}: {valor}")
            self.guardar_json(
                self.metadatos,
                os.path.join(self.salida_dir, f"{self.nombre_base}_metadatos.json"),
            )

        # 7. Texto
        modo = "(páginas seleccionadas)" if self.paginas else "(todas las páginas)"
        print(f"\n Extrayendo texto {modo}...")
        self.obtener_texto()

        if self.formato in ("txt", "ambos"):
            self.guardar_txt(
                self.textos,
                os.path.join(self.salida_dir, f"{self.nombre_base}_texto.txt"),
            )
        if self.formato in ("json", "ambos"):
            self.guardar_json(
                {str(k): v for k, v in self.textos.items()},
                os.path.join(self.salida_dir, f"{self.nombre_base}_texto.json"),
            )

        # 8. Imágenes
        if self.extraer_imagenes:
            print("\n Imágenes detectadas por página:")
            self.obtener_imagenes()
            if self.imagenes:
                for pagina, nombres in self.imagenes.items():
                    print(f"  Página {pagina}: {', '.join(nombres)}")
                self.guardar_json(
                    {str(k): v for k, v in self.imagenes.items()},
                    os.path.join(self.salida_dir, f"{self.nombre_base}_imagenes.json"),
                )
            else:
                print("  (No se encontraron imágenes)")

        # 9. Tablas
        if self.extraer_tablas:
            print("\n Detección de tablas simples (heurística):")
            self.detectar_tablas()
            if self.tablas:
                for pagina, filas in self.tablas.items():
                    print(f"  Página {pagina}: {len(filas)} filas detectadas")
                self.guardar_json(
                    self.tablas,
                    os.path.join(self.salida_dir, f"{self.nombre_base}_tablas.json"),
                )
            else:
                print("  (No se detectaron tablas)")

        # 10. Fin
        print(f"\n ¡Proceso completado!")
        print(f"   Archivos guardados en: {self.salida_dir}\n")


if __name__ == "__main__":
    extractor = PDFExtractor()
    extractor.ejecutar()
