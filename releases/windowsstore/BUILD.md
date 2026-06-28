# Windows-Store-Buildpfad - LitZentrum

Stand: 2026-06-23

## Ziel

Dieses Dokument hält den reproduzierbaren lokalen Windows-EXE-/MSIX-Pfad für
LitZentrum fest. Die Store-Artefakte werden bewusst außerhalb des Repos gebaut;
im Projekt bleiben nur Skript, Store-Assets, Hashes und Protokolle versioniert.

## Einstieg

```powershell
powershell -ExecutionPolicy Bypass -File .\releases\windowsstore\build_store_release.ps1
```

Das Skript erledigt in dieser Reihenfolge:

1. `generate_store_assets.py` erzeugt `store_assets/` aus `LitZentrum.ico`.
2. PyInstaller baut einen frischen onedir-Desktop-Build mit `resources/`,
   `schemas/` und `locales/`.
3. `_STORE/msstore_pretest.ps1` prüft den frischen Build gegen ein sauberes
   Pretest-Root ohne historische Release-Bundles.
4. `_STORE/msstore_build_msix.ps1` erzeugt ein lokales MSIX mit `_internal/`,
   `LICENSE` und `THIRD_PARTY_LICENSES.txt`.
5. `SHA256SUMS.txt` wird mit den Hashes des aktuellen EXE- und MSIX-Artefakts
   aktualisiert.
6. WACK wird nur automatisch ausgeführt, wenn die PowerShell bereits mit
   Administratorrechten läuft; sonst gibt das Skript den erhöhten Folgeaufruf
   aus.

## Voraussetzungen

- Python 3.12
- `pyinstaller` im aktiven Python
- Windows SDK mit `makeappx.exe`
- Windows App Certification Kit für den späteren erhöhten WACK-Lauf

## Lokale Artefakte des verifizierten Laufs

- EXE: `C:\_Local_DEV\codex_build\litzentrum-store\dist\LitZentrum\LitZentrum.exe`
- MSIX: `C:\_Local_DEV\codex_build\litzentrum-store\LitZentrum-1.0.0.msix`
- Hashes: `releases/windowsstore/SHA256SUMS.txt`
- Temporäres Pretest-Root: `C:\_Local_DEV\codex_build\litzentrum-store\pretest_root`
- Temporäres MSIX-Staging: `_WARTUNG/msix_staging/`

## Verifiziert am 2026-06-23

- PyInstaller-Build erfolgreich, EXE startet auch aus `C:\Windows\System32`.
- Store-Pretest: `10 PASS | 0 FAIL | 0 WARN`.
- MSIX erfolgreich gebaut.

## Aktuelle Hashes

Siehe `releases/windowsstore/SHA256SUMS.txt`.
