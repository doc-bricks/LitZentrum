@echo off
setlocal
cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python nicht gefunden.
    pause
    exit /b 1
)

set "PROJECT_ROOT=%CD%"
set "BUILD_ROOT=C:\_Local_DEV\codex_build\litzentrum"
set "VENV_DIR=%BUILD_ROOT%\.venv"
set "BUILD_PY=%VENV_DIR%\Scripts\python.exe"
set "DIST_DIR=%BUILD_ROOT%\dist"
set "WORK_DIR=%BUILD_ROOT%\work"
set "SPEC_DIR=%BUILD_ROOT%\spec"
set "ROOT_DIST_DIR=%PROJECT_ROOT%\dist"
set "SCANNER=%PROJECT_ROOT%\..\..\_tools\build_exclude_scanner.py"
set "EXCLUDES_FILE=%BUILD_ROOT%\pyinstaller-excludes.txt"
set "APP_NAME=LitZentrum"
set "VERSION=1.0.0"

set "PYTHONIOENCODING=utf-8"
set "PYTHONPATH="

if not exist "%BUILD_PY%" (
    echo [build] Erstelle lokales Build-venv: %VENV_DIR%
    py -3 -m venv "%VENV_DIR%"
    if errorlevel 1 (
        pause
        exit /b 1
    )
)

echo [build] Installiere Build-Abhaengigkeiten...
"%BUILD_PY%" -m pip install --disable-pip-version-check --upgrade pip
if errorlevel 1 (
    pause
    exit /b 1
)
"%BUILD_PY%" -m pip install --disable-pip-version-check -r "%PROJECT_ROOT%\requirements.txt" pyinstaller
if errorlevel 1 (
    pause
    exit /b 1
)

echo [build] Syntax-Check
"%BUILD_PY%" -m py_compile "%PROJECT_ROOT%\src\main.py" "%PROJECT_ROOT%\src\core\library_export.py" "%PROJECT_ROOT%\src\formats\base.py"
if errorlevel 1 (
    pause
    exit /b 1
)

set "RELEASE_DIR=%PROJECT_ROOT%\releases\v%VERSION%"
set "RELEASE_EXE=%RELEASE_DIR%\%APP_NAME%-%VERSION%-win64.exe"
set "RELEASE_HASH=%RELEASE_DIR%\SHA256SUMS.txt"

if not exist "%BUILD_ROOT%" mkdir "%BUILD_ROOT%"
if not exist "%ROOT_DIST_DIR%" mkdir "%ROOT_DIST_DIR%"
if not exist "%RELEASE_DIR%" mkdir "%RELEASE_DIR%"

if not exist "%SCANNER%" (
    echo [FEHLER] Exclude-Scanner fehlt: %SCANNER%
    pause
    exit /b 1
)

set "EXCLUDES="
"%BUILD_PY%" "%SCANNER%" --project "%PROJECT_ROOT%" --emit pyinstaller > "%EXCLUDES_FILE%"
if errorlevel 1 (
    pause
    exit /b 1
)
set /p EXCLUDES=<"%EXCLUDES_FILE%"
echo [build] Auto-Excludes: %EXCLUDES%

echo [build] PyInstaller
"%BUILD_PY%" -m PyInstaller --noconfirm --clean --windowed --onefile --noupx ^
  --name "%APP_NAME%" ^
  --icon "%PROJECT_ROOT%\resources\icons\litzentrum.ico" ^
  --add-data "%PROJECT_ROOT%\resources;resources" ^
  --add-data "%PROJECT_ROOT%\schemas;schemas" ^
  --add-data "%PROJECT_ROOT%\locales;locales" ^
  %EXCLUDES% ^
  --distpath "%DIST_DIR%" ^
  --workpath "%WORK_DIR%" ^
  --specpath "%SPEC_DIR%" ^
  "%PROJECT_ROOT%\src\main.py"
if errorlevel 1 (
    pause
    exit /b 1
)

copy /Y "%DIST_DIR%\%APP_NAME%.exe" "%ROOT_DIST_DIR%\%APP_NAME%.exe" >nul
if errorlevel 1 (
    echo [FEHLER] EXE konnte nicht nach dist kopiert werden.
    pause
    exit /b 1
)
copy /Y "%DIST_DIR%\%APP_NAME%.exe" "%RELEASE_EXE%" >nul
if errorlevel 1 (
    echo [FEHLER] Release-EXE konnte nicht aktualisiert werden.
    pause
    exit /b 1
)

"%BUILD_PY%" -c "import hashlib, pathlib; exe = pathlib.Path(r'%RELEASE_EXE%'); out = pathlib.Path(r'%RELEASE_HASH%'); out.write_text(hashlib.sha256(exe.read_bytes()).hexdigest() + ' *' + exe.name + '\n', encoding='ascii')"
if errorlevel 1 (
    pause
    exit /b 1
)

echo.
echo [build] OK -- dist\%APP_NAME%.exe
echo [build] Release-EXE: %RELEASE_EXE%
echo [build] SHA256: %RELEASE_HASH%
endlocal
