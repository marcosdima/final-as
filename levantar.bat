@echo off
chcp 65001 >nul
title ISFT 189 - Sistema + Asistente Virtual
cd /d "%~dp0"

echo ============================================================
echo   ISFT 189 - Levantando stack completo
echo ============================================================

REM --- 1. PostgreSQL (pgvector) en el puerto 55432 ---
echo [1/3] PostgreSQL...
docker start tpi-isft189 >nul 2>&1
if errorlevel 1 (
    echo       Contenedor inexistente, creandolo...
    docker run -d --name tpi-isft189 ^
        -e POSTGRES_USER=tpi ^
        -e POSTGRES_PASSWORD=tpi123 ^
        -e POSTGRES_DB=isft189 ^
        -p 55432:5432 ^
        pgvector/pgvector:pg16 >nul
)
echo       OK - puerto 55432

REM --- 2. Backend FastAPI (RAG + tools + JWT) en el puerto 8000 ---
echo [2/3] Backend FastAPI...
start "ISFT189-API" cmd /k "cd /d db\bot && app\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
echo       OK - Swagger: http://127.0.0.1:8000/docs

REM --- 3. Documento interactivo (HTML) en el puerto 8899 ---
echo [3/3] Documento HTML...
start "ISFT189-HTML" cmd /k "cd /d docs && ..\db\bot\app\.venv\Scripts\python.exe -m http.server 8899 --bind 127.0.0.1"
echo       OK - http://127.0.0.1:8899/casos_de_uso.html

ping -n 5 127.0.0.1 >nul
start "" "http://127.0.0.1:8899/casos_de_uso.html"

echo.
echo ============================================================
echo   Stack arriba. Cada servicio se abre en su propia ventana.
echo   Cerralas para detener. Para apagar todo: detener.bat
echo ============================================================
pause
