@echo off
REM ============================================================
REM  registrar_com.bat – Registra el servidor COM de PDFExtractor
REM  ** EJECUTAR COMO ADMINISTRADOR **
REM ============================================================

echo.
echo ========================================================
echo    Registro de PDFExtractor como objeto COM (OLE)
echo ========================================================
echo.

REM -- Verificar Python -----------------------------------------------
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no se encontro en el PATH del sistema.
    echo         Instala Python 3.10+ y marca "Add to PATH" durante
    echo         la instalacion.
    echo.
    pause
    exit /b 1
)
echo [OK] Python encontrado.

REM -- Instalar dependencias ------------------------------------------
echo.
echo Instalando dependencias de Python...
pip install pypdf pywin32
if errorlevel 1 (
    echo [ERROR] Fallo al instalar dependencias.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas.

REM -- Post-install de pywin32 (necesario la primera vez) -------------
echo.
echo Configurando pywin32...
python -c "import win32com" >nul 2>&1
if errorlevel 1 (
    echo Ejecutando script post-install de pywin32...
    python -m pywin32_postinstall -install 2>nul
)
echo [OK] pywin32 configurado.

REM -- Registrar el servidor COM --------------------------------------
echo.
echo Registrando PDFExtractor.Application en el registro de Windows...
cd /d "%~dp0"
python com_server.py --register

if errorlevel 1 (
    echo.
    echo [ERROR] No se pudo registrar el servidor COM.
    echo         Asegurate de ejecutar este .bat como Administrador
    echo         (clic derecho -^> "Ejecutar como administrador").
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo    Registro exitoso!
echo.
echo    ProgID:  PDFExtractor.Application
echo    CLSID:   {E8A7D5B1-4F3C-4A2E-9B1D-6C8F0E2A3B5D}
echo.
echo    Ya puedes usar CREATEOBJECT("PDFExtractor.Application")
echo    desde FoxPro, VBA, VBScript u otro cliente COM.
echo ========================================================
echo.
pause
