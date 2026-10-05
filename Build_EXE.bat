@echo off
setlocal
cd /d "%~dp0"

echo Installazione/Aggiornamento PyInstaller...
py -m pip install --upgrade pyinstaller
if errorlevel 1 goto :error

echo.
echo Creazione build Windows 11 compatibile...
py -m PyInstaller --noconfirm --clean --onedir --windowed --noupx --version-file "version_info.txt" --manifest "app.manifest" --name "Obsidian-Vault-Backup" "ObsidianVaultBackup.pyw"
if errorlevel 1 goto :error

echo.
echo Creazione ZIP portatile...
powershell -NoProfile -ExecutionPolicy Bypass -Command "if (Test-Path 'dist\Obsidian-Vault-Backup-v1.0.1-Windows.zip') { Remove-Item 'dist\Obsidian-Vault-Backup-v1.0.1-Windows.zip' -Force }; Compress-Archive -Path 'dist\Obsidian-Vault-Backup\*' -DestinationPath 'dist\Obsidian-Vault-Backup-v1.0.1-Windows.zip' -CompressionLevel Optimal"
if errorlevel 1 goto :error

echo.
echo Fatto.
echo Avvio diretto:
echo %CD%\dist\Obsidian-Vault-Backup\Obsidian-Vault-Backup.exe
echo.
echo Pacchetto da distribuire:
echo %CD%\dist\Obsidian-Vault-Backup-v1.0.1-Windows.zip
pause
exit /b 0

:error
echo.
echo ERRORE durante la compilazione.
pause
exit /b 1
