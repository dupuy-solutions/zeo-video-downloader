@echo off
cd /d "%~dp0"
where pyw >nul 2>&1
if not errorlevel 1 (
  start "" pyw app.py
  exit /b
)
where pythonw >nul 2>&1
if not errorlevel 1 (
  start "" pythonw app.py
  exit /b
)
echo Python no esta instalado. Ejecuta primero INSTALAR_EN_WINDOWS.bat
pause
