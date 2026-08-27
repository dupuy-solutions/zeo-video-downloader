@echo off
chcp 65001 >nul
title Instalador - Zeo Video Downloader
echo Instalando componentes oficiales necesarios...
echo.

where winget >nul 2>&1
if errorlevel 1 (
  echo No se encontro winget. Instala "App Installer" desde Microsoft Store y vuelve a intentarlo.
  pause
  exit /b 1
)

winget install --id Python.Python.3.13 -e --accept-package-agreements --accept-source-agreements
winget upgrade --id yt-dlp.yt-dlp -e --accept-package-agreements --accept-source-agreements
if errorlevel 1 winget install --id yt-dlp.yt-dlp -e --accept-package-agreements --accept-source-agreements
winget install --id Gyan.FFmpeg -e --accept-package-agreements --accept-source-agreements
winget install --id DenoLand.Deno -e --accept-package-agreements --accept-source-agreements

echo.
echo Creando acceso directo en el escritorio...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0crear_acceso_directo.ps1"

echo.
echo Instalacion terminada. Si Windows instalo algo nuevo, cierra esta ventana y abre la aplicacion desde el escritorio.
pause
