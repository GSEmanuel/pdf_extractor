"""
pdf_extractor
=============
Paquete para extraer texto, metadatos, imágenes y tablas de archivos PDF.

Uso rápido como módulo:

    from pdf_extractor import PDFExtractor

    ext = PDFExtractor()
    ext.abrir_pdf("documento.pdf")
    textos = ext.obtener_texto()

Uso sin guardar archivos:

    resultado = ext.extraer_todo(
        ruta_pdf="documento.pdf",
        salida_dir="./salida",
        formato="json",
        tablas=True,
    )
"""

from .extractor import PDFExtractor

__all__ = ["PDFExtractor"]
__version__ = "1.0.0"
