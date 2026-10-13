#!/usr/bin/env python3
"""
extractor_pdf.py
Extrae texto, metadatos, imágenes (nombres) y tablas simples de archivos PDF.
Librería requerida (pura Python): pypdf
    pip install pypdf
Interfaz de selección de archivos: tkinter (incluido en la stdlib de Python)
"""

import json
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

try:
    from pypdf import PdfReader
except ImportError:
    # Mostrar error en ventana si tkinter ya arrancó, o en consola
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Dependencia faltante",
            "La librería 'pypdf' no está instalada.\nInstálala con:\n\n  pip install pypdf",
        )
        root.destroy()
    except Exception:
        pass
    sys.exit("ERROR: pypdf no instalado. Ejecuta: pip install pypdf")


# ---------------------------------------------------------------------------
# Helpers de extracción
# ---------------------------------------------------------------------------

def abrir_pdf(ruta: str) -> PdfReader:
    """Abre el PDF y devuelve un PdfReader."""
    if not os.path.isfile(ruta):
        raise FileNotFoundError(f"El archivo no existe: {ruta}")
    return PdfReader(ruta)


def extraer_metadatos(reader: PdfReader) -> dict:
    """Devuelve los metadatos del documento."""
    meta = reader.metadata or {}
    return {
        "titulo":              meta.get("/Title",        ""),
        "autor":               meta.get("/Author",       ""),
        "asunto":              meta.get("/Subject",      ""),
        "creador":             meta.get("/Creator",      ""),
        "productor":           meta.get("/Producer",     ""),
        "fecha_creacion":      meta.get("/CreationDate", ""),
        "fecha_modificacion":  meta.get("/ModDate",      ""),
        "total_paginas":       len(reader.pages),
    }


def extraer_texto(reader: PdfReader, paginas: list[int] | None = None) -> dict[int, str]:
    """
    Extrae texto de las páginas indicadas (1-based).
    Si paginas es None, extrae todas.
    """
    resultado: dict[int, str] = {}
    indices = (
        [p - 1 for p in paginas]
        if paginas
        else range(len(reader.pages))
    )
    for idx in indices:
        if idx < 0 or idx >= len(reader.pages):
            print(f"  [!] Página {idx + 1} fuera de rango, omitiendo.")
            continue
        texto = reader.pages[idx].extract_text() or ""
        resultado[idx + 1] = texto
    return resultado


def listar_imagenes(reader: PdfReader) -> dict[int, list[str]]:
    """Lista los nombres de las imágenes (recursos XObject) por página."""
    imagenes: dict[int, list[str]] = {}
    for num, page in enumerate(reader.pages, start=1):
        recursos = page.get("/Resources", {})
        xobjects = recursos.get("/XObject", {})
        nombres = [
            nombre
            for nombre, obj in xobjects.items()
            if obj.get("/Subtype") == "/Image"
        ]
        if nombres:
            imagenes[num] = nombres
    return imagenes


def detectar_tablas_simples(texto: str) -> list[list[str]]:
    """
    Heurística básica: detecta filas donde los campos están
    separados por 2 o más espacios consecutivos.
    """
    tablas: list[list[str]] = []
    for linea in texto.splitlines():
        partes = [p.strip() for p in linea.split("  ") if p.strip()]
        if len(partes) >= 2:
            tablas.append(partes)
    return tablas


# ---------------------------------------------------------------------------
# Helpers de guardado
# ---------------------------------------------------------------------------

def guardar_txt(datos: dict, ruta_salida: str) -> None:
    """Guarda el texto extraído en un archivo .txt."""
    with open(ruta_salida, "w", encoding="utf-8") as f:
        for pagina, texto in datos.items():
            f.write(f"\n{'='*60}\n")
            f.write(f"  PÁGINA {pagina}\n")
            f.write(f"{'='*60}\n")
            f.write(texto)
            f.write("\n")
    print(f"  → Texto guardado en: {ruta_salida}")


def guardar_json(datos: dict, ruta_salida: str) -> None:
    """Guarda cualquier diccionario como JSON."""
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    print(f"  → JSON guardado en: {ruta_salida}")


# ---------------------------------------------------------------------------
# Selección de archivos / carpetas con tkinter.filedialog
# ---------------------------------------------------------------------------

def pedir_pdf(root: tk.Tk) -> str:
    """Abre un diálogo para seleccionar el archivo PDF. Devuelve la ruta."""
    ruta = filedialog.askopenfilename(
        parent=root,
        title="Selecciona el archivo PDF",
        filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")],
    )
    return ruta  # "" si el usuario cancela


def pedir_directorio_salida(root: tk.Tk, directorio_inicial: str) -> str:
    """Abre un diálogo para elegir dónde guardar los resultados."""
    ruta = filedialog.askdirectory(
        parent=root,
        title="Selecciona la carpeta de salida",
        initialdir=directorio_inicial,
    )
    return ruta  # "" si el usuario cancela


def pedir_paginas(root: tk.Tk, total: int) -> list[int] | None:
    """
    Pregunta al usuario qué páginas extraer.
    Devuelve una lista de enteros o None (todas).
    """
    respuesta = simpledialog.askstring(
        "Páginas a extraer",
        f"El PDF tiene {total} páginas.\n"
        "Escribe los números separados por comas (ej: 1,3,5)\n"
        "o deja en blanco para extraer TODAS:",
        parent=root,
    )
    if respuesta is None:          # usuario canceló el diálogo completo
        return None
    respuesta = respuesta.strip()
    if not respuesta:
        return None                # todas las páginas
    try:
        return [int(p.strip()) for p in respuesta.split(",") if p.strip()]
    except ValueError:
        messagebox.showwarning(
            "Formato incorrecto",
            "No se pudo interpretar la lista de páginas.\nSe extraerán TODAS.",
            parent=root,
        )
        return None


def pedir_opciones(root: tk.Tk) -> dict:
    """
    Ventana modal con checkboxes para elegir qué extraer y el formato.
    Devuelve un diccionario con las preferencias del usuario.
    """
    opciones = {
        "metadatos": tk.BooleanVar(value=True),
        "imagenes":  tk.BooleanVar(value=True),
        "tablas":    tk.BooleanVar(value=False),
        "formato":   tk.StringVar(value="txt"),
        "confirmado": False,
    }

    dialogo = tk.Toplevel(root)
    dialogo.title("Opciones de extracción")
    dialogo.resizable(False, False)
    dialogo.grab_set()             # modal

    tk.Label(dialogo, text="¿Qué deseas extraer?", font=("", 11, "bold")).grid(
        row=0, column=0, columnspan=2, pady=(12, 4), padx=16, sticky="w"
    )
    tk.Checkbutton(dialogo, text="Metadatos del documento", variable=opciones["metadatos"]).grid(
        row=1, column=0, columnspan=2, padx=20, sticky="w"
    )
    tk.Checkbutton(dialogo, text="Listar imágenes por página", variable=opciones["imagenes"]).grid(
        row=2, column=0, columnspan=2, padx=20, sticky="w"
    )
    tk.Checkbutton(dialogo, text="Detectar tablas simples (heurística)", variable=opciones["tablas"]).grid(
        row=3, column=0, columnspan=2, padx=20, sticky="w"
    )

    tk.Label(dialogo, text="Formato del texto extraído:", font=("", 10, "bold")).grid(
        row=4, column=0, columnspan=2, pady=(10, 2), padx=16, sticky="w"
    )
    for i, (texto, valor) in enumerate([("TXT", "txt"), ("JSON", "json"), ("Ambos", "ambos")]):
        tk.Radiobutton(dialogo, text=texto, variable=opciones["formato"], value=valor).grid(
            row=5, column=i, padx=(20 if i == 0 else 0, 0), sticky="w"
        )

    def confirmar():
        opciones["confirmado"] = True
        dialogo.destroy()

    def cancelar():
        dialogo.destroy()

    frame_botones = tk.Frame(dialogo)
    frame_botones.grid(row=6, column=0, columnspan=3, pady=12)
    tk.Button(frame_botones, text="Continuar", width=10, command=confirmar).pack(side="left", padx=6)
    tk.Button(frame_botones, text="Cancelar",  width=10, command=cancelar).pack(side="left", padx=6)

    dialogo.wait_window()
    return opciones


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # Ventana raíz oculta (sólo para los diálogos)
    root = tk.Tk()
    root.withdraw()

    # 1. Seleccionar PDF
    ruta_pdf = pedir_pdf(root)
    if not ruta_pdf:
        messagebox.showinfo("Cancelado", "No se seleccionó ningún archivo.", parent=root)
        root.destroy()
        return

    # 2. Abrir PDF
    try:
        reader = abrir_pdf(ruta_pdf)
    except Exception as e:
        messagebox.showerror("Error al abrir el PDF", str(e), parent=root)
        root.destroy()
        return

    total_paginas = len(reader.pages)
    nombre_base   = os.path.splitext(os.path.basename(ruta_pdf))[0]
    dir_inicial   = os.path.dirname(ruta_pdf)

    print(f"\n📄 Abriendo: {ruta_pdf}")
    print(f"   Páginas totales: {total_paginas}")

    # 3. Seleccionar carpeta de salida
    salida_dir = pedir_directorio_salida(root, dir_inicial)
    if not salida_dir:
        messagebox.showinfo("Cancelado", "No se seleccionó carpeta de salida.", parent=root)
        root.destroy()
        return

    os.makedirs(salida_dir, exist_ok=True)

    # 4. Opciones de extracción
    opciones = pedir_opciones(root)
    if not opciones["confirmado"]:
        messagebox.showinfo("Cancelado", "Operación cancelada.", parent=root)
        root.destroy()
        return

    formato   = opciones["formato"].get()
    metadatos = opciones["metadatos"].get()
    imagenes  = opciones["imagenes"].get()
    tablas    = opciones["tablas"].get()

    # 5. Páginas a extraer
    paginas = pedir_paginas(root, total_paginas)

    # 6. Metadatos
    if metadatos:
        print("\n📋 METADATOS")
        print("-" * 40)
        meta = extraer_metadatos(reader)
        for clave, valor in meta.items():
            print(f"  {clave:<22}: {valor}")
        guardar_json(meta, os.path.join(salida_dir, f"{nombre_base}_metadatos.json"))

    # 7. Texto
    modo = "(páginas seleccionadas)" if paginas else "(todas las páginas)"
    print(f"\n📝 Extrayendo texto {modo}...")
    textos = extraer_texto(reader, paginas)

    if formato in ("txt", "ambos"):
        guardar_txt(textos, os.path.join(salida_dir, f"{nombre_base}_texto.txt"))

    if formato in ("json", "ambos"):
        guardar_json(
            {str(k): v for k, v in textos.items()},
            os.path.join(salida_dir, f"{nombre_base}_texto.json"),
        )

    # 8. Imágenes
    if imagenes:
        print("\n🖼️  Imágenes detectadas por página:")
        imgs = listar_imagenes(reader)
        if imgs:
            for pagina, nombres in imgs.items():
                print(f"  Página {pagina}: {', '.join(nombres)}")
            guardar_json(
                {str(k): v for k, v in imgs.items()},
                os.path.join(salida_dir, f"{nombre_base}_imagenes.json"),
            )
        else:
            print("  (No se encontraron imágenes)")

    # 9. Tablas
    if tablas:
        print("\n📊 Detección de tablas simples (heurística):")
        todas_tablas: dict[str, list] = {}
        for pagina, texto in textos.items():
            filas = detectar_tablas_simples(texto)
            if filas:
                print(f"  Página {pagina}: {len(filas)} filas detectadas")
                todas_tablas[str(pagina)] = filas
        if todas_tablas:
            guardar_json(
                todas_tablas,
                os.path.join(salida_dir, f"{nombre_base}_tablas.json"),
            )
        else:
            print("  (No se detectaron tablas)")

    # 10. Fin
    print("\n✅ ¡Proceso completado!\n")
    messagebox.showinfo(
        "¡Listo!",
        f"Extracción completada.\nArchivos guardados en:\n{salida_dir}",
        parent=root,
    )
    root.destroy()


if __name__ == "__main__":
    main()
