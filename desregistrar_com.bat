@echo off
REM ============================================================
REM  desregistrar_com.bat – Elimina PDFExtractor del registro COM
REM  ** EJECUTAR COMO ADMINISTRADOR **
REM ============================================================

echo.
echo ========================================================
echo    Des-registro de PDFExtractor.Application
echo ========================================================
echo.

cd /d "%~dp0"
python com_server.py --unregister

if errorlevel 1 (
    echo.
    echo [ERROR] No se pudo des-registrar.
    echo         Ejecuta como Administrador.
    pause
    exit /b 1
)

echo.
echo [OK] PDFExtractor.Application fue eliminado del registro COM.
echo.
pause
