# Extractor de Información de Archivos PDF

Herramienta en Python para extraer texto, metadatos, nombres de imágenes y tablas simples a partir de archivos PDF utilizando `pypdf`.

---

## 📋 Requisitos

Instala la dependencia requerida antes de comenzar:

```bash
pip install pypdf
```

> **Nota:** La librería estándar `tkinter` se utiliza únicamente para mostrar las ventanas de diálogo al seleccionar archivos y carpetas de salida.

---

## 🚀 Uso de la clase `PDFExtractor`

La clase `PDFExtractor` se encuentra definida en [`main.py`](file:///home/santiagoemanuel/mis_proyectos/pdf_extractor/main.py). Puedes utilizarla de dos maneras: **modo interactivo** o **modo programático**.

---

### 1. Modo Interactivo (Asistido por Consola y Diálogos)

El método `ejecutar()` guía al usuario paso a paso abriendo ventanas de selección de archivo y carpeta, y solicitando opciones por consola:

```python
from main import PDFExtractor

extractor = PDFExtractor()
extractor.ejecutar()
```

O ejecutando el script directamente desde la terminal:

```bash
python main.py
```

**Flujo interactivo:**
1. Selección del archivo PDF mediante ventana de diálogo.
2. Selección de la carpeta de destino donde se guardarán los resultados.
3. Preguntas en consola sobre qué extraer (metadatos, imágenes, tablas y formato de texto `txt`, `json` o `ambos`).
4. Especificación de páginas a procesar (ej. `1,3,5` o Enter para todas).
5. Extracción y guardado automático de los archivos generados.

---

### 2. Modo Programático (Uso en tu propio código)

Puedes instanciar `PDFExtractor` y llamar a sus métodos directamente sin necesidad de pasar por la consola ni los diálogos interactivos:

```python
from main import PDFExtractor

# 1. Crear la instancia
extractor = PDFExtractor()

# 2. Cargar el archivo PDF
extractor.abrir_pdf("ruta/al/documento.pdf")
print(f"Total de páginas: {extractor.total_paginas}")

# 3. (Opcional) Filtrar páginas específicas (1-based index)
# None procesa todas las páginas
extractor.paginas = [1, 2]

# 4. Extraer texto
textos = extractor.obtener_texto()
for pagina, texto in textos.items():
    print(f"--- Página {pagina} ---")
    print(texto)

# 5. Obtener metadatos
metadatos = extractor.obtener_metadatos()
print("Metadatos:", metadatos)

# 6. Detectar nombres de recursos de imágenes
imagenes = extractor.obtener_imagenes()
print("Imágenes encontradas:", imagenes)

# 7. Detectar tablas simples (heurística basada en espacios)
tablas = extractor.detectar_tablas()
print("Tablas detectadas:", tablas)

# 8. Guardar resultados en disco si se desea
extractor.guardar_txt(extractor.textos, "salida_texto.txt")
extractor.guardar_json(extractor.metadatos, "salida_metadatos.json")
```

---

## ⚙️ Métodos Principales

| Método | Descripción |
| :--- | :--- |
| `abrir_pdf(ruta: str)` | Abre y analiza el PDF indicado, inicializando `reader` y `total_paginas`. |
| `obtener_metadatos() -> dict` | Extrae metadatos del documento (título, autor, fechas, etc.). |
| `obtener_texto() -> dict[int, str]` | Extrae texto de las páginas configuradas en `self.paginas` (o todas si es `None`). |
| `obtener_imagenes() -> dict[int, list[str]]` | Lista los nombres de objetos de imagen XObject por página. |
| `detectar_tablas() -> dict[str, list]` | Detecta filas y columnas separadas por 2 o más espacios a partir del texto extraído. |
| `guardar_txt(datos: dict, ruta_salida: str)` | Guarda texto formateado por páginas en un archivo `.txt`. |
| `guardar_json(datos: dict, ruta_salida: str)` | Serializa y guarda cualquier diccionario en formato `.json`. |
| `ejecutar()` | Ejecuta el flujo completo interactivo con selección de archivos y configuración por consola. |

---

## 🔧 Atributos Configurables

- `extractor.paginas`: Lista de enteros con las páginas a procesar (base 1, ej. `[1, 3]`), o `None` para todas.
- `extractor.salida_dir`: Ruta del directorio donde se almacenarán las exportaciones.
- `extractor.formato`: Formato de texto para el modo interactivo (`"txt"`, `"json"` o `"ambos"`).
- `extractor.extraer_metadatos`: Booleano que activa/desactiva la extracción de metadatos.
- `extractor.extraer_imagenes`: Booleano que activa/desactiva la detección de imágenes.
- `extractor.extraer_tablas`: Booleano que activa/desactiva la detección de tablas simples.
