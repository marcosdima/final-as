@echo off
chcp 65001 >nul
title ISFT 189 - Deteniendo stack
echo Deteniendo servicios...

REM Backend FastAPI (8000) y servidor HTML (8899)
for %%P in (8000 8899) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr /r ":%%P .*LISTENING"') do (
        taskkill /f /pid %%a >nul 2>&1
    )
)

REM PostgreSQL en Docker
docker stop tpi-isft189 >nul 2>&1

echo Listo. Servicios detenidos (la BD queda detenida, no borrada).
pause
