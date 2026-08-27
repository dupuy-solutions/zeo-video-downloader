$ErrorActionPreference = "Stop"
$appDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$launcher = Join-Path $appDir "ABRIR_ZEO_VIDEO_DOWNLOADER.bat"
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Zeo Video Downloader.lnk"
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $launcher
$shortcut.WorkingDirectory = $appDir
$shortcut.Description = "Descargador de videos con enlace"
$shortcut.Save()
Write-Host "Acceso directo creado: $shortcutPath"
