@echo off
echo ========================================
echo    LitZentrum - Literaturverwaltung
echo ========================================
echo.

REM Prüfe ob Python installiert ist
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python ist nicht installiert oder nicht im PATH.
    echo Bitte Python 3.10+ installieren: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Wechsle zum Projektverzeichnis
cd /d "%~dp0"

REM Prüfe ob Abhängigkeiten installiert sind
python -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installiere Abhängigkeiten...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [FEHLER] Konnte Abhängigkeiten nicht installieren.
        pause
        exit /b 1
    )
)

echo [INFO] Starte LitZentrum...
echo.
python src/main.py

if errorlevel 1 (
    echo.
    echo [FEHLER] LitZentrum wurde mit Fehler beendet.
    pause
)
