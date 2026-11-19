@echo off
chcp 65001 >nul
set "APP_DIR=%~dp0"
if "%APP_DIR:~-1%"=="\" set "APP_DIR=%APP_DIR:~0,-1%"
cd /d "%APP_DIR%"

echo ========================================================
echo   Iniciando Lanzador Suite IA Local (Modo Consola)
echo ========================================================

set "PYTHON_EXE=C:\Users\%USERNAME%\.audio_translator_venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=%APP_DIR%\.venv\Scripts\python.exe"
)
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python.exe"
)

"%PYTHON_EXE%" "%APP_DIR%\main.py"

pause
