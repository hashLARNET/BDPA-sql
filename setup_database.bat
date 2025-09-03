@echo off
echo ========================================
echo    BDPA - Configurar Base de Datos
echo ========================================
echo.

REM Obtener la ruta del directorio actual
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo [INFO] Directorio actual: %CD%
echo.

REM Verificar si existe el entorno virtual
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] No se encontro el entorno virtual en 'venv'
    echo [INFO] Primero ejecuta 'iniciar_bdpa.bat' para crear el entorno
    pause
    exit /b 1
)

echo [INFO] Activando entorno virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Error al activar el entorno virtual
    pause
    exit /b 1
)

echo [INFO] Configurando base de datos...
echo.

python setup_database.py

echo.
echo [INFO] Configuracion completada.
pause