"""
extractor.py
Lógica pura de extracción de PDF, sin dependencias de UI (tkinter).
Puede importarse como módulo desde cualquier otro software.

Dependencia requerida:
    pip install pypdf
"""

import json
import os
from pypdf import PdfReader


class PDFExtractor:
    """Extrae y guarda texto, metadatos, imágenes y tablas de un PDF.

    Uso como librería:

        from pdf_extractor import PDFExtractor

        ext = PDFExtractor()
        ext.abrir_pdf("documento.pdf")

        textos    = ext.obtener_texto()
        metadatos = ext.obtener_metadatos()
        imagenes  = ext.obtener_imagenes()
        tablas    = ext.detectar_tablas()

        ext.guardar_txt(textos,    "texto.txt")
        ext.guardar_json(metadatos, "metadatos.json")
    """

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
        self.formato: str = "txt"           # "txt" | "json" | "ambos"
        self.paginas: list[int] | None = None  # None = todas

        # Resultados intermedios
        self.metadatos: dict = {}
        self.textos: dict[int, str] = {}
        self.imagenes: dict[int, list[str]] = {}
        self.tablas: dict[str, list] = {}

    # ------------------------------------------------------------------
    # Carga del PDF
    # ------------------------------------------------------------------

    def abrir_pdf(self, ruta: str) -> None:
        """Abre el PDF y carga el reader y los datos básicos.

        Args:
            ruta: Ruta al archivo PDF.

        Raises:
            FileNotFoundError: Si el archivo no existe.
        """
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
        """Devuelve los metadatos del documento y los guarda en self.metadatos.

        Returns:
            Diccionario con título, autor, fechas, etc.
        """
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
        """Extrae texto de las páginas indicadas en self.paginas (1-based).

        Si self.paginas es None, extrae todas. Resultado en self.textos.

        Returns:
            Diccionario {número_de_página: texto}.
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
        """Lista los nombres de las imágenes (XObject) por página.

        Returns:
            Diccionario {número_de_página: [nombre_imagen, ...]}.
        """
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
        """Detecta filas donde los campos están separados por 2+ espacios.

        Opera sobre self.textos; llama primero a obtener_texto() si está vacío.

        Returns:
            Diccionario {"número_de_página": [[col1, col2, ...], ...]}.
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
        """Guarda el texto extraído en un archivo .txt.

        Args:
            datos: Diccionario {número_de_página: texto}.
            ruta_salida: Ruta completa del archivo de salida.
        """
        with open(ruta_salida, "w", encoding="utf-8") as f:
            for pagina, texto in datos.items():
                f.write(f"\n{'='*60}\n")
                f.write(f"  PÁGINA {pagina}\n")
                f.write(f"{'='*60}\n")
                f.write(texto)
                f.write("\n")
        print(f"  → Texto guardado en: {ruta_salida}")

    def guardar_json(self, datos: dict, ruta_salida: str) -> None:
        """Guarda cualquier diccionario como JSON.

        Args:
            datos: Datos a serializar.
            ruta_salida: Ruta completa del archivo de salida.
        """
        with open(ruta_salida, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        print(f"  → JSON guardado en: {ruta_salida}")

    # ------------------------------------------------------------------
    # Método de conveniencia: extracción completa sin UI
    # ------------------------------------------------------------------

    def extraer_todo(
        self,
        ruta_pdf: str,
        salida_dir: str,
        paginas: list[int] | None = None,
        formato: str = "txt",
        metadatos: bool = True,
        imagenes: bool = True,
        tablas: bool = False,
    ) -> dict:
        """Extrae y guarda todo el contenido del PDF sin interacción humana.

        Args:
            ruta_pdf:   Ruta al archivo PDF.
            salida_dir: Directorio donde se guardarán los archivos resultantes.
            paginas:    Lista de páginas (1-based) o None para todas.
            formato:    "txt", "json" o "ambos".
            metadatos:  Si True, extrae y guarda los metadatos.
            imagenes:   Si True, lista y guarda los nombres de imágenes.
            tablas:     Si True, detecta y guarda tablas simples.

        Returns:
            Diccionario con todos los resultados:
            {
                "metadatos": {...},
                "textos":    {1: "...", 2: "..."},
                "imagenes":  {1: ["Im0"], ...},
                "tablas":    {"1": [["col1", "col2"], ...]},
            }
        """
        self.paginas = paginas
        self.formato = formato
        self.extraer_metadatos = metadatos
        self.extraer_imagenes = imagenes
        self.extraer_tablas = tablas

        self.abrir_pdf(ruta_pdf)
        os.makedirs(salida_dir, exist_ok=True)
        self.salida_dir = salida_dir

        resultado: dict = {}

        if self.extraer_metadatos:
            resultado["metadatos"] = self.obtener_metadatos()
            self.guardar_json(
                self.metadatos,
                os.path.join(salida_dir, f"{self.nombre_base}_metadatos.json"),
            )

        self.obtener_texto()
        resultado["textos"] = self.textos

        if self.formato in ("txt", "ambos"):
            self.guardar_txt(
                self.textos,
                os.path.join(salida_dir, f"{self.nombre_base}_texto.txt"),
            )
        if self.formato in ("json", "ambos"):
            self.guardar_json(
                {str(k): v for k, v in self.textos.items()},
                os.path.join(salida_dir, f"{self.nombre_base}_texto.json"),
            )

        if self.extraer_imagenes:
            resultado["imagenes"] = self.obtener_imagenes()
            if self.imagenes:
                self.guardar_json(
                    {str(k): v for k, v in self.imagenes.items()},
                    os.path.join(salida_dir, f"{self.nombre_base}_imagenes.json"),
                )

        if self.extraer_tablas:
            resultado["tablas"] = self.detectar_tablas()
            if self.tablas:
                self.guardar_json(
                    self.tablas,
                    os.path.join(salida_dir, f"{self.nombre_base}_tablas.json"),
                )

        return resultado
