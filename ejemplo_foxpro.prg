*!* ============================================================
*!* ejemplo_foxpro.prg
*!* Ejemplo de uso de PDFExtractor desde Visual FoxPro
*!* ============================================================
*!*
*!* Requisitos previos:
*!*   1. Python 3.10+ instalado en Windows con PATH configurado
*!*   2. Ejecutar registrar_com.bat como Administrador
*!*

LOCAL oExtractor, cRuta, cTexto, cMeta, cTablas, cError
LOCAL nPaginas, nExito

*!* ---- Crear el objeto COM ----
oExtractor = CREATEOBJECT("PDFExtractor.Application")

IF ISNULL(oExtractor)
    MESSAGEBOX("No se pudo crear PDFExtractor.Application." + CHR(13) + ;
               "Verifica que el servidor COM esté registrado.", 16, "Error")
    RETURN
ENDIF


*!* ============================================================
*!* EJEMPLO 1: Uso paso a paso
*!* ============================================================

*!* 1. Abrir un PDF
cRuta = "C:\ruta\a\tu\documento.pdf"
nExito = oExtractor.AbrirPDF(cRuta)

IF !nExito
    cError = oExtractor.UltimoError()
    MESSAGEBOX("Error al abrir PDF: " + cError, 16, "Error")
    RETURN
ENDIF

*!* 2. Consultar propiedades
nPaginas = oExtractor.TotalPaginas
? "Total de páginas:", nPaginas
? "Nombre base:", oExtractor.NombreBase
? "Ruta:", oExtractor.RutaPDF

*!* 3. Obtener metadatos (devuelve JSON)
cMeta = oExtractor.ObtenerMetadatos()
? "Metadatos (JSON):", cMeta

*!* 4. Obtener texto de TODAS las páginas (devuelve JSON)
cTexto = oExtractor.ObtenerTexto("")
? "Texto completo (JSON):", LEFT(cTexto, 500)

*!* 5. Obtener texto de una sola página (devuelve texto plano)
cTexto = oExtractor.ObtenerTextoPagina(1)
? "Texto página 1:", LEFT(cTexto, 500)

*!* 6. Obtener texto de páginas específicas (devuelve JSON)
cTexto = oExtractor.ObtenerTexto("1,3,5")
? "Texto páginas 1,3,5 (JSON):", LEFT(cTexto, 500)

*!* 7. Listar imágenes (devuelve JSON)
cImagenes = oExtractor.ObtenerImagenes()
? "Imágenes (JSON):", cImagenes

*!* 8. Detectar tablas (requiere ObtenerTexto previo)
cTablas = oExtractor.DetectarTablas()
? "Tablas (JSON):", LEFT(cTablas, 500)

*!* 9. Cerrar / liberar
oExtractor.Cerrar()


*!* ============================================================
*!* EJEMPLO 2: Extracción completa de una sola vez
*!* ============================================================

*!* ExtraerTodo abre el PDF, extrae todo y guarda archivos en disco
LOCAL cResultado
cResultado = oExtractor.ExtraerTodo( ;
    "C:\ruta\a\tu\documento.pdf", ;
    "C:\ruta\salida", ;
    "", ;
    "ambos", ;
    1, ;
    1, ;
    1  ;
)

? "Resultado completo (JSON):", LEFT(cResultado, 500)


*!* ============================================================
*!* EJEMPLO 3: Manejo de errores
*!* ============================================================

*!* Si cualquier método falla, devuelve un valor vacío/falso.
*!* El error se puede consultar con UltimoError().

nExito = oExtractor.AbrirPDF("C:\archivo\que\no\existe.pdf")
IF !nExito
    ? "Error:", oExtractor.UltimoError()
ENDIF


*!* ============================================================
*!* EJEMPLO 4: Parsear JSON en FoxPro (manual con STREXTRACT)
*!* ============================================================

*!* Para parsear el JSON devuelto puedes usar:
*!*   - STREXTRACT() para campos simples
*!*   - Una librería JSON para FoxPro (recomendado):
*!*     https://github.com/pctolmern/foxjson
*!*     https://github.com/vfp9/json-vfp

*!* Ejemplo básico con STREXTRACT:
cMeta = oExtractor.ObtenerMetadatos()
LOCAL cTitulo
cTitulo = STREXTRACT(cMeta, [titulo": "], ["])
? "Título del PDF:", cTitulo


*!* ---- Liberar el objeto ----
RELEASE oExtractor

? ""
? "=== Ejemplo completado ==="
