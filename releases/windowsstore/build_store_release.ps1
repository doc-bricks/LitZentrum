param(
    [string]$BuildRoot = "C:\_Local_DEV\codex_build\litzentrum-store",
    [switch]$SkipPretest,
    [switch]$SkipMsix,
    [switch]$SkipWack
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$SoftwareRoot = Split-Path -Parent (Split-Path -Parent $ProjectRoot)
$StoreTools = Join-Path $SoftwareRoot "_STORE"
$Version = ([regex]::Match((Get-Content (Join-Path $ProjectRoot "src\main.py") -Raw), 'setApplicationVersion\("([^"]+)"\)')).Groups[1].Value
if (-not $Version) {
    throw "Konnte Anwendungsversion aus src/main.py nicht lesen."
}

$DistRoot = Join-Path $BuildRoot "dist"
$WorkRoot = Join-Path $BuildRoot "build"
$SpecRoot = Join-Path $BuildRoot "spec"
$PretestRoot = Join-Path $BuildRoot "pretest_root"
$ExeDir = Join-Path $DistRoot "LitZentrum"
$ExePath = Join-Path $ExeDir "LitZentrum.exe"
$MsixPath = Join-Path $BuildRoot "LitZentrum-$Version.msix"
$HashFile = Join-Path $ScriptDir "SHA256SUMS.txt"

New-Item -ItemType Directory -Force -Path $BuildRoot,$DistRoot,$WorkRoot,$SpecRoot | Out-Null

Write-Host "==> Store-Assets erzeugen"
python (Join-Path $ProjectRoot "generate_store_assets.py")

Write-Host "==> PyInstaller-Build"
pyinstaller `
    --noconfirm `
    --clean `
    --windowed `
    --name LitZentrum `
    --icon (Join-Path $ProjectRoot "resources\icons\litzentrum.ico") `
    --distpath $DistRoot `
    --workpath $WorkRoot `
    --specpath $SpecRoot `
    --add-data ((Join-Path $ProjectRoot "resources") + ";resources") `
    --add-data ((Join-Path $ProjectRoot "schemas") + ";schemas") `
    --add-data ((Join-Path $ProjectRoot "locales") + ";locales") `
    (Join-Path $ProjectRoot "src\main.py")

if (-not (Test-Path $ExePath)) {
    throw "PyInstaller-Build hat $ExePath nicht erzeugt."
}

if (-not $SkipPretest) {
    Write-Host "==> Store-Pretest"
    if (Test-Path $PretestRoot) {
        Remove-Item $PretestRoot -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path $PretestRoot | Out-Null
    Copy-Item (Join-Path $ProjectRoot "store_package.json") $PretestRoot
    Copy-Item (Join-Path $ProjectRoot "store_assets") (Join-Path $PretestRoot "store_assets") -Recurse
    Copy-Item (Join-Path $ProjectRoot "PRIVACY_POLICY.md") $PretestRoot
    Copy-Item (Join-Path $ProjectRoot "SUPPORT.md") $PretestRoot
    Copy-Item (Join-Path $ProjectRoot "LICENSE") $PretestRoot
    Copy-Item (Join-Path $ProjectRoot "THIRD_PARTY_LICENSES.txt") $PretestRoot

    & (Join-Path $StoreTools "msstore_pretest.ps1") `
        -ExePath $ExePath `
        -ProjectRoot $PretestRoot `
        -PrivacyUrl "https://github.com/doc-bricks/LitZentrum/blob/master/PRIVACY_POLICY.md" `
        -SupportUrl "https://github.com/doc-bricks/LitZentrum/blob/master/SUPPORT.md" `
        -StartWait 8
}

if (-not $SkipMsix) {
    Write-Host "==> MSIX bauen"
    $extraFiles = @(
        (Join-Path $ExeDir "_internal"),
        (Join-Path $ProjectRoot "LICENSE"),
        (Join-Path $ProjectRoot "THIRD_PARTY_LICENSES.txt")
    )

    & (Join-Path $StoreTools "msstore_build_msix.ps1") `
        -ProjectRoot $ProjectRoot `
        -ExePath $ExePath `
        -OutputMsix $MsixPath `
        -ExtraFiles $extraFiles

    if (Test-Path $MsixPath) {
        $exeHash = (Get-FileHash -Algorithm SHA256 -Path $ExePath).Hash
        $msixHash = (Get-FileHash -Algorithm SHA256 -Path $MsixPath).Hash
        @(
            "SHA256  LitZentrum.exe  $exeHash"
            "SHA256  LitZentrum-$Version.msix  $msixHash"
        ) | Set-Content -Path $HashFile -Encoding utf8
    }
}

if (-not $SkipWack -and (Test-Path $MsixPath)) {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if ($isAdmin) {
        Write-Host "==> WACK"
        & (Join-Path $StoreTools "msstore_wack.ps1") -MsixPath $MsixPath
    } else {
        Write-Host "WACK wurde nicht automatisch ausgeführt, weil diese Session keine Admin-Rechte hat."
        Write-Host "Manueller Schritt:"
        Write-Host "  Start-Process powershell -Verb RunAs -ArgumentList '-ExecutionPolicy Bypass -File ""$(Join-Path $StoreTools "msstore_wack.ps1")"" -MsixPath ""$MsixPath""'"
    }
}

Write-Host ""
Write-Host "Fertig."
Write-Host "EXE : $ExePath"
if (Test-Path $MsixPath) {
    Write-Host "MSIX: $MsixPath"
}
