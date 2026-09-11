@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if %errorlevel%==0 (
  py app_pro.py
) else (
  python app_pro.py
)
endlocal
