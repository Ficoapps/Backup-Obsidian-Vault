@echo off
setlocal
cd /d "%~dp0"

echo Installazione/Aggiornamento PyInstaller...
py -m pip install --upgrade pyinstaller
if errorlevel 1 goto :error

echo.
echo Creazione EXE...
py -m PyInstaller --noconfirm --clean --onefile --windowed --name "Obsidian-Vault-Backup" "ObsidianVaultBackup.pyw"
if errorlevel 1 goto :error

echo.
echo Fatto.
echo EXE creato in:
echo %CD%\dist\Obsidian-Vault-Backup.exe
pause
exit /b 0

:error
echo.
echo ERRORE durante la compilazione.
pause
exit /b 1
