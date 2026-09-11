@echo off
chcp 65001 >nul
setlocal
title Instalador - ZEO Downloader 2.0 PRO
cd /d "%~dp0"

echo ==========================================
echo   ZEO Downloader 2.0 PRO - Instalacion
echo ==========================================
echo.
echo Se instalaran/actualizaran los componentes necesarios.
echo.

where winget >nul 2>&1
if errorlevel 1 (
  echo No se encontro winget.
  echo Instala "App Installer" desde Microsoft Store y vuelve a intentarlo.
  pause
  exit /b 1
)

winget install --id Python.Python.3.13 -e --accept-package-agreements --accept-source-agreements
winget upgrade --id yt-dlp.yt-dlp -e --accept-package-agreements --accept-source-agreements
if errorlevel 1 winget install --id yt-dlp.yt-dlp -e --accept-package-agreements --accept-source-agreements
winget install --id Gyan.FFmpeg -e --accept-package-agreements --accept-source-agreements
winget install --id DenoLand.Deno -e --accept-package-agreements --accept-source-agreements
winget install --id Microsoft.Edge -e --accept-package-agreements --accept-source-agreements

echo.
echo Instalando automatizacion oficial de navegador para Suno...
where py >nul 2>&1
if %errorlevel%==0 (
  py -m pip install --upgrade pip selenium
) else (
  python -m pip install --upgrade pip selenium
)
if errorlevel 1 (
  echo.
  echo ERROR: No se pudo instalar Selenium.
  echo Cierra esta ventana, reinicia Windows si Python se acaba de instalar y ejecuta este archivo nuevamente.
  pause
  exit /b 1
)

echo.
echo Instalacion ZEO 2.0 PRO terminada.
echo.
echo Para abrirlo ejecuta:
echo   ABRIR_ZEO_2_PRO.bat
echo.
echo IMPORTANTE SUNO:
echo - La primera descarga abrira una ventana de Edge controlada por ZEO.
echo - Inicia sesion en Suno alli una sola vez.
echo - ZEO usa el menu oficial Download de Suno y respeta sus limites de descarga.
echo.
pause
endlocal
