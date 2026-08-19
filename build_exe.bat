@echo off
setlocal
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set "PROJECT_ROOT=%CD%"
set "BUILD_ROOT=C:\_Local_DEV\codex_build\litzentrum"
set "SCANNER=C:\Users\User\OneDrive\.TOPICS\.SOFTWARE\_tools\build_exclude_scanner.py"
REM Absoluter Pfad statt relativ: LitZentrum liegt als Plan-D-Klon unter
REM C:\_Local_DEV\repos\, nicht unter OneDrive\.TOPICS\.SOFTWARE\<Kategorie>\ wie
REM die Projekte, aus denen dieses Skript-Muster kopiert wurde -- ein relativer
REM "..\..\_tools"-Pfad zeigt von hier aus ins Leere und liess den Scanner beim
REM ersten Versuch (2026-08-19) ungenutzt, PyInstaller zog daraufhin ungewollt
REM torch/transformers/sklearn/tensorflow/boto3/uvicorn (>900 MB RSS) mit.

echo Baue LitZentrum.exe...
if not exist "%BUILD_ROOT%" mkdir "%BUILD_ROOT%"
set "EXCLUDES="
if exist "%SCANNER%" (
    for /f "delims=" %%E in ('python "%SCANNER%" --project "%PROJECT_ROOT%" --emit pyinstaller') do set "EXCLUDES=%%E"
)

REM schemas/ (litzentrum-library-v1.schema.json u.a., zur Laufzeit von
REM core/library_export.py und formats/base.py geladen) UND
REM resources/icons/ (Fenster-Icon aus main.py) sind echte Laufzeit-
REM Abhaengigkeiten und werden mitgebuendelt. locales/translations.json ist
REM NUR ein Entwicklungswerkzeug (manage_translations.py/translator.py,
REM von keinem src/-Modul importiert) und wird bewusst NICHT gebuendelt.
python -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name LitZentrum ^
  --icon "%PROJECT_ROOT%\resources\icons\litzentrum.ico" ^
  --paths "%PROJECT_ROOT%\src" ^
  --add-data "%PROJECT_ROOT%\schemas;schemas" ^
  --add-data "%PROJECT_ROOT%\resources;resources" ^
  %EXCLUDES% ^
  --distpath "%BUILD_ROOT%\dist" ^
  --workpath "%BUILD_ROOT%\build" ^
  --specpath "%BUILD_ROOT%" ^
  "%PROJECT_ROOT%\src\main.py"
if errorlevel 1 ( exit /b 1 )
if not exist "dist" mkdir "dist"
copy /Y "%BUILD_ROOT%\dist\LitZentrum.exe" "dist\LitZentrum.exe" >nul
copy /Y "%BUILD_ROOT%\dist\LitZentrum.exe" "LitZentrum.exe" >nul
echo Fertig: dist\LitZentrum.exe
