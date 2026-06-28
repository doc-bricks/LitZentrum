# WACK-Protokoll - LitZentrum

Stand: 2026-06-23

## Artefakt

- MSIX: `C:\_Local_DEV\codex_build\litzentrum-store\LitZentrum-1.0.0.msix`
- SHA256: `71C0FB13A9B84478A3258A0487A4D8D499A99EE8C955796925E3C2249D16D080`

## Vorstufe

- Store-Pretest gegen den frischen Build bestanden: `10 PASS | 0 FAIL | 0 WARN`.
- MSIX lokal erfolgreich mit `_STORE/msstore_build_msix.ps1` erzeugt.

## Nicht erhöhter WACK-Aufruf

Verwendeter Befehl:

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\User\OneDrive\.TOPICS\.SOFTWARE\_STORE\msstore_wack.ps1 -MsixPath C:\_Local_DEV\codex_build\litzentrum-store\LitZentrum-1.0.0.msix
```

Ergebnis:

- WACK ist installiert.
- Der Lauf bricht ohne Administratorrechte erwartungsgemäß vor dem eigentlichen
  Test mit dem Hinweis auf `Start-Process -Verb RunAs` ab.

## Nächster Pflichtschritt

Den echten erhöhten WACK-Lauf mit Administratorrechten ausführen:

```powershell
Start-Process powershell -Verb RunAs -ArgumentList '-ExecutionPolicy Bypass -File "C:\Users\User\OneDrive\.TOPICS\.SOFTWARE\_STORE\msstore_wack.ps1" -MsixPath "C:\_Local_DEV\codex_build\litzentrum-store\LitZentrum-1.0.0.msix"'
```

Danach den XML-Reportpfad und das Gesamtergebnis in dieses Dokument ergänzen.
