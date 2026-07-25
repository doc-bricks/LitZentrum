# Windows Store Prep - LitZentrum

Stand: 2026-07-25

## Ziel dieses Dokuments

Dieses Dokument hält die aktuell vorhandene Windows-Store-Basis für LitZentrum
fest. Es ersetzt noch keine echte Einreichung, bündelt aber die öffentlichen
Artefakte und die nächsten Blocker für den Store-Pfad.

## Bereits vorhanden

- `store_package.json` mit App-Name, Identity (`Geiger.LitZentrum`), Publisher DN (`CN=52596601-BAB4-4F3F-B182-E8F3F273B202`), Publisher Display Name (`Lukas Geiger`), Version (`1.0.0.0`), Kategorie (`Productivity`), Pricing (`Free`), Sprachen (`de-DE`, `en-US`), Logo-Verweis und öffentlichen URLs
- `STORE_LISTING.md` mit DE/EN-Storetexten
- `PRIVACY_POLICY.md` als öffentliche Datenschutzseite
- `SUPPORT.md` als öffentliche Supportseite
- `THIRD_PARTY_LICENSES.txt` für die Drittanbieter-Lizenzdokumentation
- `README/screenshots/main.png` als vorhandener Basis-Screenshot
- reproduzierbares Store-Screenshot-Set unter `README/screenshots/store/`
- `generate_store_screenshots.py` als Generator für anonymisierte Store-Bilder
- `generate_store_assets.py` als Generator für die benötigten Store-Logo-PNGs
- `store_assets/` mit `Square44x44Logo.png`, `Square150x150Logo.png`, `Wide310x150Logo.png` und `Square310x310Logo.png`
- `README/screenshots/store/README.md` als Inventar für das erzeugte Store-Screenshot-Set
- `tests/test_store_materials.py` als Regressionstest für Metadaten, Partner-Center-Publisher, Links, Sprachabdeckung und Screenshot-Hinweise (100% grün)
- `releases/windowsstore/build_store_release.ps1` als reproduzierbarer EXE-/MSIX-Buildpfad
- `releases/windowsstore/BUILD.md`, `releases/windowsstore/WACK_PROTOCOL.md` und `releases/windowsstore/SHA256SUMS.txt`

## Geplanter Pretest-Ablauf

1. `THIRD_PARTY_LICENSES.txt` für die Store- und Lizenzdokumentation ergänzen (erledigt).
2. Reproduzierbaren Windows-Buildpfad für `LitZentrum.exe` ausführen.
3. `_STORE/msstore_pretest.ps1` mit LitZentrum-spezifischen Pfaden ausführen.
4. MSIX bauen.
5. WACK als Administrator gegen das MSIX ausführen.
6. Partner-Center-Eintrag mit den Texten aus `STORE_LISTING.md` und den vorhandenen Screenshots befüllen.

## Noch offene Blocker

- Ein echter erhöhter WACK-Lauf mit XML-Report fehlt noch (erfordert Admin-Rechte).
- Manuelle Einreichung im Partner-Center (erfordert menschliche Autorisation).

## Hinweise zu Store-Claims

- LitZentrum ist eine lokale Desktop-App und kein Cloud-Literaturdienst.
- Es gibt keine Pflichtregistrierung und keinen Serverzwang.
- Der mobile Pfad läuft über einen read-only Companion-Export, nicht über vollständige Cloud-Synchronisierung.
- Wegen `runFullTrust` ist ein klassischer Desktop-Bridge-/MSIX-Pfad zu erwarten.
