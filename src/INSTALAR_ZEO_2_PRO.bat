@echo off
chcp 65001 >nul
setlocal
title Instalador - ZEO Downloader 2.0 PRO
cd /d "%~dp0"

echo ==========================================
echo   ZEO Downloader 2.0 PRO.4 - Instalacion
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

echo.
echo Instalando Playwright para el soporte Suno...
where py >nul 2>&1
if %errorlevel%==0 (
  py -m pip install --upgrade pip playwright
  if errorlevel 1 goto :playwright_error
  echo.
  echo Descargando Chromium integrado de ZEO...
  py -m playwright install chromium
  if errorlevel 1 goto :chromium_error
) else (
  python -m pip install --upgrade pip playwright
  if errorlevel 1 goto :playwright_error
  echo.
  echo Descargando Chromium integrado de ZEO...
  python -m playwright install chromium
  if errorlevel 1 goto :chromium_error
)

echo.
echo ==========================================
echo   INSTALACION COMPLETADA
 echo ==========================================
echo.
echo Para abrir ZEO ejecuta:
echo   ABRIR_ZEO_2_PRO.bat
echo.
echo SUNO:
echo - ZEO abre un Chromium limpio en cada descarga.
echo - La primera vez inicia sesion en Suno alli.
echo - ZEO guarda cookies/sesion sin reutilizar un perfil bloqueable del navegador.
echo - ZEO usa el flujo oficial Download y respeta el cupo de Suno.
echo.
pause
exit /b 0

:playwright_error
echo.
echo ERROR: No se pudo instalar Playwright.
echo Reinicia Windows si Python se acaba de instalar y ejecuta este instalador nuevamente.
pause
exit /b 1

:chromium_error
echo.
echo ERROR: No se pudo descargar Chromium.
echo Revisa tu conexion a Internet y ejecuta este instalador nuevamente.
pause
exit /b 1
