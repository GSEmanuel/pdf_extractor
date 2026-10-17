# PDF Extractor

Herramienta y módulo en Python para la extracción de texto, metadatos, referencias a imágenes y detección heurística de tablas en documentos PDF.

Está diseñado de forma modular: el archivo [`extractor.py`](file:///home/santiagoemanuel/mis_proyectos/pdf_extractor/extractor.py) contiene lógica pura sin dependencias de interfaz gráfica, lo que permite importarlo fácilmente en cualquier script o aplicación externa. Además, incluye un ejecutor interactivo opcional con diálogos visuales y consola en [`cli.py`](file:///home/santiagoemanuel/mis_proyectos/pdf_extractor/cli.py).

---

## Requisitos e Instalación

Requiere **Python 3.10+** y la biblioteca `pypdf`:

```bash
pip install pypdf
```

> **Nota:** Si deseas utilizar el modo interactivo con ventanas de selección de archivos, asegúrate de tener instalado `tkinter` (incluido habitualmente con Python; en distribuciones Debian/Ubuntu puede requerir `sudo apt install python3-tk`).

---

## Uso de la Clase `PDFExtractor` (Como Módulo)

Puedes importar la clase directamente desde el paquete o desde el archivo `extractor`:

```python
from pdf_extractor import PDFExtractor
# o también: from extractor import PDFExtractor
```

### 1. Extracción completa y automática (`extraer_todo`)

El método `extraer_todo` abre el archivo, procesa los datos según las opciones indicadas, guarda los archivos en el directorio de salida especificado y devuelve un diccionario con todos los resultados obtenidos:

```python
from pdf_extractor import PDFExtractor

ext = PDFExtractor()

resultados = ext.extraer_todo(
    ruta_pdf="documento.pdf",
    salida_dir="./salida",
    paginas=[1, 2, 3],     # Lista de páginas (1-based) o None para extraer todas
    formato="ambos",       # Formatos de texto: "txt", "json" o "ambos"
    metadatos=True,        # Si se deben extraer y guardar los metadatos
    imagenes=True,         # Si se deben listar y guardar las referencias a imágenes
    tablas=True            # Si se debe aplicar la detección heurística de tablas
)

# Estructura del diccionario retornado:
# {
#     "metadatos": {...},
#     "textos":    {1: "...", 2: "..."},
#     "imagenes":  {1: ["Im0", ...]},
#     "tablas":    {"1": [["col1", "col2"], ...]}
# }
```

---

### 2. Uso paso a paso con control granular

Si prefieres realizar operaciones individuales en memoria o controlar cuándo guardar los archivos:

```python
from pdf_extractor import PDFExtractor

# Instanciar el extractor
ext = PDFExtractor()

# 1. Abrir el documento PDF
ext.abrir_pdf("documento.pdf")
print(f"Total de páginas: {ext.total_paginas}")

# 2. Extraer metadatos
metadatos = ext.obtener_metadatos()
print("Título:", metadatos.get("titulo"))
print("Autor:", metadatos.get("autor"))

# 3. Extraer texto
# Opcional: filtrar páginas específicas (1-based); si es None, extrae todas
ext.paginas = [1, 3]
textos = ext.obtener_texto()  # Devuelve {número_de_página: texto}

for pagina, texto in textos.items():
    print(f"--- Página {pagina} ---")
    print(texto[:200])  # Primeros 200 caracteres

# 4. Listar imágenes por página (objetos XObject de subtipo Image)
imagenes = ext.obtener_imagenes()  # Devuelve {número_de_página: [nombres]}
print("Imágenes detectadas:", imagenes)

# 5. Detectar tablas simples
# Heurística basada en separación de columnas por 2 o más espacios
tablas = ext.detectar_tablas()  # Devuelve {"número_de_página": [[col1, col2, ...], ...]}
print("Tablas detectadas:", tablas)

# 6. Guardar resultados en disco manualmente
ext.guardar_txt(textos, "salida_texto.txt")
ext.guardar_json(metadatos, "salida_metadatos.json")
ext.guardar_json(imagenes, "salida_imagenes.json")
ext.guardar_json(tablas, "salida_tablas.json")
```

---

## Referencia de Métodos de `PDFExtractor`

| Método | Argumentos | Retorno | Descripción |
| :--- | :--- | :--- | :--- |
| `abrir_pdf(ruta)` | `ruta: str` | `None` | Valida la existencia del archivo, crea el lector `PdfReader` y almacena la ruta y cantidad total de páginas. |
| `obtener_metadatos()` | Ninguno | `dict` | Extrae metadatos del PDF (título, autor, asunto, fechas, etc.) y los guarda en `self.metadatos`. |
| `obtener_texto()` | Ninguno | `dict[int, str]` | Extrae el texto de las páginas configuradas en `self.paginas` (o todas si es `None`). Mapea `{número_página: texto}`. |
| `obtener_imagenes()` | Ninguno | `dict[int, list[str]]` | Obtiene los nombres identificadores de imágenes (`/XObject` con `/Subtype == /Image`) organizadas por página. |
| `detectar_tablas()` | Ninguno | `dict[str, list]` | Detecta filas de posibles tablas tabuladas en el texto extraído separadas por múltiples espacios. |
| `guardar_txt(datos, ruta_salida)` | `datos: dict[int, str]`, `ruta_salida: str` | `None` | Escribe el contenido de texto organizado por páginas en un archivo plano UTF-8. |
| `guardar_json(datos, ruta_salida)` | `datos: dict`, `ruta_salida: str` | `None` | Serializa cualquier diccionario en formato JSON con indentación y soporte UTF-8. |
| `extraer_todo(...)` | Ver parámetros en el ejemplo de arriba | `dict` | Orquesta la apertura, extracción opcional de metadatos, texto, imágenes y tablas, y guarda los archivos en disco automáticamente. |

---

## Propiedades y Atributos de la Clase

La instancia de `PDFExtractor` expone los siguientes atributos útiles:

- `self.ruta_pdf` (`str`): Ruta del archivo actual.
- `self.nombre_base` (`str`): Nombre del PDF sin extensión ni directorios.
- `self.total_paginas` (`int`): Número total de páginas leídas.
- `self.paginas` (`list[int] | None`): Lista de páginas seleccionadas para la extracción (base 1) o `None` para todas.
- `self.formato` (`str`): Formato para la salida de texto (`"txt"`, `"json"` o `"ambos"`).
- `self.salida_dir` (`str`): Directorio destino de los archivos guardados.
- `self.metadatos` (`dict`): Últimos metadatos extraídos.
- `self.textos` (`dict[int, str]`): Último texto extraído por página.
- `self.imagenes` (`dict[int, list[str]]`): Últimas imágenes detectadas.
- `self.tablas` (`dict[str, list]`): Últimas tablas detectadas.

---

## Uso Interactivo por Consola / UI

También puedes ejecutar el flujo interactivo guiado por consola y ventanas de selección de archivos ejecutando el script principal [`main.py`](file:///home/santiagoemanuel/mis_proyectos/pdf_extractor/main.py):

```bash
python main.py
```

El script te solicitará:
1. Seleccionar el archivo PDF mediante un cuadro de diálogo.
2. Seleccionar la carpeta donde se guardarán los resultados.
3. Elegir qué elementos extraer (metadatos, imágenes, tablas y formato de texto).
4. Indicar qué páginas deseas procesar (o presionar ENTER para todas).
