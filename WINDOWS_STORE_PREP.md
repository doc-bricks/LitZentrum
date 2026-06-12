# Windows Store Prep - LitZentrum

Stand: 2026-06-12

## Ziel dieses Dokuments

Dieses Dokument hält die aktuell vorhandene Windows-Store-Basis für LitZentrum
fest. Es ersetzt noch keine echte Einreichung, bündelt aber die öffentlichen
Artefakte und die nächsten Blocker für den Store-Pfad.

## Bereits vorhanden

- `store_package.json` mit App-Name, Identity, Version, Kategorie und öffentlichen URLs
- `STORE_LISTING.md` mit DE/EN-Storetexten
- `PRIVACY_POLICY.md` als öffentliche Datenschutzseite
- `SUPPORT.md` als öffentliche Supportseite
- `README/screenshots/main.png` als vorhandener Basis-Screenshot
- reproduzierbares Store-Screenshot-Set unter `README/screenshots/store/`
- `generate_store_screenshots.py` als Generator für anonymisierte Store-Bilder
- `README/screenshots/store/README.md` als Inventar für das erzeugte Store-Screenshot-Set
- `tests/test_store_materials.py` als Regressionstest für Metadaten, Links und Screenshot-Hinweise

## Geplanter Pretest-Ablauf

1. `THIRD_PARTY_LICENSES.txt` für die Store- und Lizenzdokumentation ergänzen.
2. Reproduzierbaren Windows-Buildpfad für `LitZentrum.exe` festziehen und dokumentieren.
3. `_STORE/msstore_pretest.ps1` mit LitZentrum-spezifischen Pfaden ausführen.
4. MSIX bauen.
5. WACK als Administrator gegen das MSIX ausführen.
6. Partner-Center-Eintrag mit den Texten aus `STORE_LISTING.md` und den vorhandenen Screenshots befüllen.

## Noch offene Blocker

- Ein dokumentierter EXE-/MSIX-Buildpfad fehlt noch.
- WACK-Protokoll fehlt noch.

## Hinweise zu Store-Claims

- LitZentrum ist eine lokale Desktop-App und kein Cloud-Literaturdienst.
- Es gibt keine Pflichtregistrierung und keinen Serverzwang.
- Der mobile Pfad läuft über einen read-only Companion-Export, nicht über
  vollständige Cloud-Synchronisierung.
- Wegen `runFullTrust` ist ein klassischer Desktop-Bridge-/MSIX-Pfad zu erwarten.
