#!/usr/bin/env python3
"""
main.py
Punto de entrada para ejecutar el extractor de PDF de forma interactiva.

Uso directo:
    python main.py

Uso como módulo (desde otro script):
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

from pdf_extractor.cli import ejecutar_interactivo

if __name__ == "__main__":
    ejecutar_interactivo()

