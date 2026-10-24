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


---

## Uso como Objeto COM en Windows (FoxPro / VBA / VBScript)

PDF Extractor puede registrarse como un **objeto COM (OLE Automation)** en Windows, lo que permite usarlo desde **Visual FoxPro**, VBA (Excel, Access), VBScript y cualquier lenguaje que soporte `CREATEOBJECT`.

### Archivos del módulo COM

| Archivo | Descripción |
| :--- | :--- |
| [`com_server.py`](file:///home/santiagoemanuel/mis_proyectos/pdf_extractor/com_server.py) | Servidor COM que envuelve `PDFExtractor` en una interfaz IDispatch compatible con OLE Automation. |
| [`registrar_com.bat`](file:///home/santiagoemanuel/mis_proyectos/pdf_extractor/registrar_com.bat) | Script batch para instalar dependencias y registrar el objeto COM (ejecutar como Administrador). |
| [`desregistrar_com.bat`](file:///home/santiagoemanuel/mis_proyectos/pdf_extractor/desregistrar_com.bat) | Script batch para eliminar el registro COM del sistema. |
| [`ejemplo_foxpro.prg`](file:///home/santiagoemanuel/mis_proyectos/pdf_extractor/ejemplo_foxpro.prg) | Programa de ejemplo completo para Visual FoxPro. |

---

### Requisitos en Windows

1. **Python 3.10+** instalado y agregado al `PATH` del sistema (marcar "Add Python to PATH" durante la instalación).
2. **pypdf** – biblioteca para leer archivos PDF.
3. **pywin32** – biblioteca que provee el soporte COM para Python.

Ambas bibliotecas se instalan automáticamente al ejecutar `registrar_com.bat`, o manualmente con:

```cmd
pip install pypdf pywin32
```

---

### Instalación y Registro del Objeto COM

1. Copiar toda la carpeta `pdf_extractor` al equipo Windows (por ejemplo, en `C:\pdf_extractor\`).
2. Hacer **clic derecho** sobre `registrar_com.bat` → **"Ejecutar como administrador"**.
3. Si todo sale bien, verás el mensaje:

```
ProgID:  PDFExtractor.Application
CLSID:   {E8A7D5B1-4F3C-4A2E-9B1D-6C8F0E2A3B5D}
```

El objeto queda registrado globalmente y disponible para cualquier aplicación COM del sistema.

> **Nota:** Si mueves la carpeta a otra ubicación, es necesario volver a ejecutar `registrar_com.bat` para actualizar la ruta en el registro de Windows.

---

### Des-registro

Para eliminar el objeto COM del registro de Windows, ejecutar `desregistrar_com.bat` como Administrador.

---

### Uso desde Visual FoxPro

#### Crear el objeto

```foxpro
oExtractor = CREATEOBJECT("PDFExtractor.Application")
```

#### Abrir un PDF y consultar propiedades

```foxpro
lExito = oExtractor.AbrirPDF("C:\documentos\factura.pdf")

IF lExito
    ? "Páginas:", oExtractor.TotalPaginas
    ? "Nombre:", oExtractor.NombreBase
    ? "Ruta:", oExtractor.RutaPDF
ELSE
    ? "Error:", oExtractor.UltimoError()
ENDIF
```

#### Extraer texto de todas las páginas

```foxpro
*!* Devuelve JSON: {"1": "texto pág 1", "2": "texto pág 2", ...}
cTextoJSON = oExtractor.ObtenerTexto("")
```

#### Extraer texto de una sola página

```foxpro
*!* Devuelve texto plano directamente
cTexto = oExtractor.ObtenerTextoPagina(1)
? cTexto
```

#### Extraer texto de páginas específicas

```foxpro
*!* Páginas separadas por comas
cTextoJSON = oExtractor.ObtenerTexto("1,3,5")
```

#### Obtener metadatos

```foxpro
*!* JSON: {"titulo": "...", "autor": "...", "total_paginas": N, ...}
cMeta = oExtractor.ObtenerMetadatos()
```

#### Listar imágenes

```foxpro
*!* JSON: {"1": ["Im0", "Im1"], "3": ["Im0"], ...}
cImagenes = oExtractor.ObtenerImagenes()
```

#### Detectar tablas

```foxpro
*!* Primero obtener texto, luego detectar tablas
oExtractor.ObtenerTexto("")
cTablas = oExtractor.DetectarTablas()
```

#### Extracción completa en una sola llamada

```foxpro
cResultado = oExtractor.ExtraerTodo( ;
    "C:\documentos\factura.pdf", ;
    "C:\salida", ;
    "", ;
    "ambos", ;
    1, ;
    1, ;
    1  ;
)
```

Parámetros de `ExtraerTodo`:

| # | Parámetro | Tipo | Descripción |
| :--- | :--- | :--- | :--- |
| 1 | `ruta_pdf` | Cadena | Ruta completa al archivo PDF. |
| 2 | `salida_dir` | Cadena | Directorio donde se guardan los archivos generados. |
| 3 | `paginas_csv` | Cadena | Páginas separadas por comas (`"1,3,5"`) o `""` para todas. |
| 4 | `formato` | Cadena | `"txt"`, `"json"` o `"ambos"`. |
| 5 | `metadatos` | Entero | `1` = extraer metadatos, `0` = omitir. |
| 6 | `imagenes` | Entero | `1` = listar imágenes, `0` = omitir. |
| 7 | `tablas` | Entero | `1` = detectar tablas, `0` = omitir. |

#### Manejo de errores

Todos los métodos capturan excepciones internamente. Si un método falla:
- Devuelve `False` (`.F.`) para métodos booleanos, o `"{}"` / `""` para métodos que devuelven cadenas.
- El mensaje de error queda disponible llamando a `UltimoError()`:

```foxpro
lExito = oExtractor.AbrirPDF("C:\no_existe.pdf")
IF !lExito
    MESSAGEBOX(oExtractor.UltimoError(), 16, "Error")
ENDIF
```

#### Cerrar y liberar

```foxpro
oExtractor.Cerrar()
RELEASE oExtractor
```

---

### Referencia Completa de la Interfaz COM

#### Propiedades (solo lectura)

| Propiedad | Tipo | Descripción |
| :--- | :--- | :--- |
| `TotalPaginas` | Entero | Número total de páginas del PDF abierto (0 si no hay PDF). |
| `NombreBase` | Cadena | Nombre del archivo PDF sin extensión ni directorios. |
| `RutaPDF` | Cadena | Ruta completa del PDF actualmente abierto. |

#### Métodos

| Método | Parámetros | Retorno | Descripción |
| :--- | :--- | :--- | :--- |
| `AbrirPDF(ruta)` | `ruta`: Cadena | Booleano | Abre un archivo PDF para procesamiento. |
| `Cerrar()` | Ninguno | Booleano | Cierra el PDF y reinicia el extractor. |
| `ObtenerTexto(paginas_csv)` | `paginas_csv`: Cadena (`"1,3"` o `""`) | Cadena JSON | Extrae texto de las páginas indicadas. |
| `ObtenerTextoPagina(pagina)` | `pagina`: Entero (base 1) | Cadena | Extrae texto plano de una sola página. |
| `ObtenerMetadatos()` | Ninguno | Cadena JSON | Devuelve metadatos del PDF. |
| `ObtenerImagenes()` | Ninguno | Cadena JSON | Lista las imágenes XObject por página. |
| `DetectarTablas()` | Ninguno | Cadena JSON | Detecta tablas heurísticas (requiere `ObtenerTexto` previo). |
| `ExtraerTodo(...)` | Ver tabla arriba | Cadena JSON | Extracción completa con guardado automático en disco. |
| `UltimoError()` | Ninguno | Cadena | Devuelve el mensaje del último error. |

---

### Cómo funciona internamente

```
FoxPro / VBA / VBScript
    │
    │  CREATEOBJECT("PDFExtractor.Application")
    ▼
┌──────────────────┐     ┌──────────────────┐     ┌─────────────┐
│  COM / IDispatch │────▶│  com_server.py   │────▶│ extractor.py │
│  (pywin32)       │     │  PDFExtractorCOM │     │ PDFExtractor │
└──────────────────┘     └──────────────────┘     └──────┬──────┘
                                                         │
                                                         ▼
                                                    ┌─────────┐
                                                    │  pypdf  │
                                                    └─────────┘
```

1. FoxPro llama a `CREATEOBJECT("PDFExtractor.Application")`.
2. Windows busca el ProgID en el registro y lanza el proceso Python (`com_server.py`).
3. `PDFExtractorCOM` recibe las llamadas via IDispatch y las traduce a llamadas al `PDFExtractor` original.
4. Los resultados complejos (diccionarios, listas) se serializan a **JSON** antes de devolverlos, ya que COM/FoxPro solo maneja tipos simples (cadenas, enteros, booleanos).
5. FoxPro recibe cadenas JSON que puede parsear con `STREXTRACT()` o con una librería JSON para VFP como [nfJson](https://github.com/pctolmern/foxjson).

---

### Notas importantes para FoxPro

- **Tipos de datos:** FoxPro no tiene tipos nativos para diccionarios ni listas. Por eso todos los resultados complejos se devuelven como **cadenas JSON**. Se recomienda usar una librería JSON para FoxPro para parsearlos cómodamente.
- **Booleanos:** En los parámetros donde se espera un booleano, se usan enteros: `1` = verdadero, `0` = falso.
- **Rutas de archivos:** Usar siempre rutas completas con backslash (`C:\carpeta\archivo.pdf`).
- **Codificación:** Los textos se devuelven en UTF-8. Si el PDF contiene caracteres especiales (acentos, ñ), FoxPro debería manejarlos correctamente en versiones recientes.
- **Rendimiento:** El primer `CREATEOBJECT` puede tardar un par de segundos en inicializar Python. Las llamadas posteriores son rápidas.
- **Servidor Out-of-Process:** El objeto COM se ejecuta en un proceso Python separado. Esto significa que FoxPro no se congela durante operaciones largas, pero también que el objeto no comparte memoria con FoxPro.
