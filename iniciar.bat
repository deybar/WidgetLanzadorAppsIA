@echo off
set "APP_DIR=%~dp0"
if "%APP_DIR:~-1%"=="\" set "APP_DIR=%APP_DIR:~0,-1%"
cd /d "%APP_DIR%"

set "PYTHONW=C:\Users\%USERNAME%\.audio_translator_venv\Scripts\pythonw.exe"
if not exist "%PYTHONW%" (
    set "PYTHONW=%APP_DIR%\.venv\Scripts\pythonw.exe"
)
if not exist "%PYTHONW%" (
    set "PYTHONW=pythonw.exe"
)

start "" "%PYTHONW%" "%APP_DIR%\main.py"
exit
