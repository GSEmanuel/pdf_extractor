"""
Punto de entrada para ejecutar el paquete directamente:

    python -m pdf_extractor
"""

from .cli import ejecutar_interactivo

if __name__ == "__main__":
    ejecutar_interactivo()
