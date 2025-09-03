@echo off
echo ========================================
echo    BDPA Los Encinos - Iniciando App
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
    echo [INFO] Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Error al crear el entorno virtual
        pause
        exit /b 1
    )
)

echo [INFO] Activando entorno virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Error al activar el entorno virtual
    pause
    exit /b 1
)

REM Verificar si existen las dependencias
echo [INFO] Verificando dependencias...
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo [INFO] Instalando dependencias...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Error al instalar dependencias
        pause
        exit /b 1
    )
)

REM Verificar si existe el archivo .env
if not exist ".env" (
    echo [WARNING] No se encontro el archivo .env
    echo [INFO] Creando .env desde .env.example...
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo [WARNING] Archivo .env creado. Configurar variables antes de continuar.
    ) else (
        echo [ERROR] No se encontro .env.example
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo    Iniciando Backend (FastAPI)
echo ========================================
echo.

REM Iniciar el backend en segundo plano
echo [INFO] Iniciando servidor FastAPI en puerto 8000...
start "BDPA Backend" /min python main.py

REM Esperar un poco para que el backend inicie
echo [INFO] Esperando que el backend inicie...
timeout /t 5 /nobreak >nul

REM Verificar si el backend esta corriendo
echo [INFO] Verificando conexion al backend...
python -c "import requests; requests.get('http://localhost:8000', timeout=5)" 2>nul
if errorlevel 1 (
    echo [WARNING] El backend podria no haber iniciado correctamente
    echo [INFO] Esperando un poco mas...
    timeout /t 10 /nobreak >nul
)

echo.
echo ========================================
echo    Iniciando Frontend (Tkinter)
echo ========================================
echo.

REM Iniciar el frontend
echo [INFO] Iniciando aplicacion Tkinter...
python -m frontend.run
if errorlevel 1 (
    echo [ERROR] Error al iniciar la aplicacion frontend
    pause
    exit /b 1
)

echo.
echo [INFO] Aplicacion cerrada correctamente.
echo.

REM Cerrar el backend si aun esta corriendo
echo [INFO] Cerrando procesos del backend...
taskkill /f /im python.exe /fi "WINDOWTITLE eq BDPA Backend*" 2>nul

echo [INFO] ¡Hasta luego!
pause