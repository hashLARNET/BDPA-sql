@echo off
echo ========================================
echo    BDPA - Crear Usuarios (Simple)
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

echo [INFO] Ejecutando script simple de creacion de usuarios...
echo.

python crear_usuarios_simple.py

echo.
echo [INFO] Script completado.
pause