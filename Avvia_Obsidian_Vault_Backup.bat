@echo off
setlocal
cd /d "%~dp0"

where pyw >nul 2>nul
if %errorlevel%==0 (
    start "" pyw "ObsidianVaultBackup.pyw"
    exit /b 0
)

where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw "ObsidianVaultBackup.pyw"
    exit /b 0
)

where py >nul 2>nul
if %errorlevel%==0 (
    py "ObsidianVaultBackup.pyw"
    exit /b 0
)

where python >nul 2>nul
if %errorlevel%==0 (
    python "ObsidianVaultBackup.pyw"
    exit /b 0
)

echo Python non risulta installato o non e' nel PATH.
echo Installa Python 3 da https://www.python.org/downloads/windows/
pause
