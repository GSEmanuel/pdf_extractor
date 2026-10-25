"""
com_server.py – Servidor COM que expone PDFExtractor para FoxPro y otros clientes COM.

Registro (ejecutar como Administrador):
    python com_server.py --register

Des-registro:
    python com_server.py --unregister

Uso desde Visual FoxPro:
    oExtractor = CREATEOBJECT("PDFExtractor.Application")
    oExtractor.AbrirPDF("C:\ruta\documento.pdf")
    ? oExtractor.TotalPaginas
    cTexto = oExtractor.ObtenerTexto(0)
    oExtractor.Cerrar()
"""

from __future__ import annotations

import json
import os
import sys

import pythoncom
import win32com.server.register

# Agregar el directorio del script al PATH para que el paquete
# pdf_extractor se pueda importar correctamente.
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from pdf_extractor.extractor import PDFExtractor


class PDFExtractorCOM:
    """Objeto COM que envuelve PDFExtractor para su uso desde FoxPro/VBA/VBScript.

    Convenciones para FoxPro:
    - Todos los métodos devuelven tipos simples compatibles con COM/OLE Automation:
      cadenas (BSTR), enteros (LONG) y booleanos (VARIANT_BOOL).
    - Las estructuras complejas (diccionarios, listas) se serializan como
      cadenas JSON que FoxPro puede parsear con STREXTRACT o bibliotecas JSON.
    - Los números de página son base 1.  Pasar 0 significa "todas las páginas".
    - Los booleanos se representan como enteros (1 = True, 0 = False) para
      máxima compatibilidad con FoxPro, que no tiene un tipo booleano nativo
      en llamadas COM.
    """

    # ---- Metadatos COM ----
    _reg_clsid_ = "{E8A7D5B1-4F3C-4A2E-9B1D-6C8F0E2A3B5D}"
    _reg_progid_ = "PDFExtractor.Application"
    _reg_desc_ = "PDF Extractor – Extrae texto, metadatos, tablas e imágenes de PDF"
    _reg_class_spec_ = "com_server.PDFExtractorCOM"

    # Interfaz IDispatch pública (métodos y propiedades expuestos a COM)
    _public_methods_ = [
        "AbrirPDF",
        "Cerrar",
        "ObtenerTexto",
        "ObtenerTextoPagina",
        "ObtenerMetadatos",
        "ObtenerImagenes",
        "DetectarTablas",
        "ExtraerTodo",
        "UltimoError",
    ]
    _public_attrs_ = [
        "TotalPaginas",
        "NombreBase",
        "RutaPDF",
    ]
    _readonly_attrs_ = [
        "TotalPaginas",
        "NombreBase",
        "RutaPDF",
    ]

    def __init__(self):
        self._extractor = PDFExtractor()
        self._ultimo_error: str = ""

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _set_error(self, msg: str) -> None:
        self._ultimo_error = str(msg)

    def _clear_error(self) -> None:
        self._ultimo_error = ""

    # ------------------------------------------------------------------
    # Propiedades de solo lectura
    # ------------------------------------------------------------------

    @property
    def TotalPaginas(self) -> int:
        """Número total de páginas del PDF abierto (0 si no hay PDF)."""
        return self._extractor.total_paginas

    @property
    def NombreBase(self) -> str:
        """Nombre del archivo PDF sin extensión ni ruta."""
        return self._extractor.nombre_base

    @property
    def RutaPDF(self) -> str:
        """Ruta completa del PDF actualmente abierto."""
        return self._extractor.ruta_pdf

    # ------------------------------------------------------------------
    # Métodos públicos
    # ------------------------------------------------------------------

    def AbrirPDF(self, ruta: str) -> bool:
        """Abre un archivo PDF.  Devuelve True (.T.) si tuvo éxito.

        Args:
            ruta: Ruta completa al archivo PDF.
        """
        try:
            self._clear_error()
            self._extractor.abrir_pdf(ruta)
            return True
        except Exception as exc:
            self._set_error(str(exc))
            return False

    def Cerrar(self) -> bool:
        """Reinicia el extractor liberando el PDF actual."""
        try:
            self._clear_error()
            self._extractor = PDFExtractor()
            return True
        except Exception as exc:
            self._set_error(str(exc))
            return False

    def ObtenerTexto(self, paginas_csv: str = "") -> str:
        """Obtiene texto del PDF.

        Args:
            paginas_csv: Números de página separados por comas (base 1).
                         Cadena vacía o "0" = todas las páginas.

        Returns:
            Cadena JSON: {"1": "texto pág 1", "2": "texto pág 2", ...}
            En caso de error devuelve "{}".
        """
        try:
            self._clear_error()
            if paginas_csv and paginas_csv.strip() != "0":
                self._extractor.paginas = [
                    int(p.strip())
                    for p in paginas_csv.split(",")
                    if p.strip()
                ]
            else:
                self._extractor.paginas = None
            textos = self._extractor.obtener_texto()
            return json.dumps(
                {str(k): v for k, v in textos.items()},
                ensure_ascii=False,
            )
        except Exception as exc:
            self._set_error(str(exc))
            return "{}"

    def ObtenerTextoPagina(self, pagina: int) -> str:
        """Atajo: obtiene el texto de una sola página (base 1).

        Args:
            pagina: Número de página (1, 2, 3, ...).

        Returns:
            Cadena con el texto plano de esa página.
        """
        try:
            self._clear_error()
            self._extractor.paginas = [pagina]
            textos = self._extractor.obtener_texto()
            return textos.get(pagina, "")
        except Exception as exc:
            self._set_error(str(exc))
            return ""

    def ObtenerMetadatos(self) -> str:
        """Obtiene los metadatos del PDF como cadena JSON.

        Returns:
            JSON: {"titulo": "...", "autor": "...", "total_paginas": N, ...}
        """
        try:
            self._clear_error()
            meta = self._extractor.obtener_metadatos()
            return json.dumps(meta, ensure_ascii=False)
        except Exception as exc:
            self._set_error(str(exc))
            return "{}"

    def ObtenerImagenes(self) -> str:
        """Lista las imágenes (XObject) del PDF por página.

        Returns:
            JSON: {"1": ["Im0", "Im1"], "3": ["Im0"], ...}
        """
        try:
            self._clear_error()
            imgs = self._extractor.obtener_imagenes()
            return json.dumps(
                {str(k): v for k, v in imgs.items()},
                ensure_ascii=False,
            )
        except Exception as exc:
            self._set_error(str(exc))
            return "{}"

    def DetectarTablas(self) -> str:
        """Detecta tablas heurísticas basadas en columnas separadas por espacios.

        Requiere haber llamado antes a ObtenerTexto() para tener texto cargado.

        Returns:
            JSON: {"1": [["col1","col2"], ...], ...}
        """
        try:
            self._clear_error()
            tablas = self._extractor.detectar_tablas()
            return json.dumps(tablas, ensure_ascii=False)
        except Exception as exc:
            self._set_error(str(exc))
            return "{}"

    def ExtraerTodo(
        self,
        ruta_pdf: str,
        salida_dir: str,
        paginas_csv: str = "",
        formato: str = "txt",
        metadatos: int = 1,
        imagenes: int = 1,
        tablas: int = 0,
    ) -> str:
        """Extracción completa.  Abre el PDF, extrae todo y guarda en disco.

        Args:
            ruta_pdf:     Ruta completa al archivo PDF.
            salida_dir:   Directorio de salida (se crea si no existe).
            paginas_csv:  Páginas separadas por comas ("1,3,5") o vacío = todas.
            formato:      "txt", "json" o "ambos".
            metadatos:    1 = extraer metadatos, 0 = omitirlos.
            imagenes:     1 = listar imágenes, 0 = omitirlas.
            tablas:       1 = detectar tablas, 0 = omitirlas.

        Returns:
            Cadena JSON con el resultado completo.
        """
        try:
            self._clear_error()
            paginas_list = None
            if paginas_csv and paginas_csv.strip() != "0":
                paginas_list = [
                    int(p.strip())
                    for p in paginas_csv.split(",")
                    if p.strip()
                ]
            resultado = self._extractor.extraer_todo(
                ruta_pdf=ruta_pdf,
                salida_dir=salida_dir,
                paginas=paginas_list,
                formato=formato,
                metadatos=bool(metadatos),
                imagenes=bool(imagenes),
                tablas=bool(tablas),
            )
            # Convertir claves int a str para serialización JSON limpia
            serializable = {}
            for key, value in resultado.items():
                if isinstance(value, dict):
                    serializable[key] = {str(k): v for k, v in value.items()}
                else:
                    serializable[key] = value
            return json.dumps(serializable, ensure_ascii=False)
        except Exception as exc:
            self._set_error(str(exc))
            return "{}"

    def UltimoError(self) -> str:
        """Devuelve el mensaje del último error ocurrido, o cadena vacía."""
        return self._ultimo_error


# ------------------------------------------------------------------
# Registro / Des-registro del servidor COM
# ------------------------------------------------------------------

if __name__ == "__main__":
    win32com.server.register.UseCommandLine(PDFExtractorCOM)
