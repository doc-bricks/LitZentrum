# LitZentrum Web/PWA Companion

Stand: 2026-06-02

Der Companion ist jetzt als statischer Offline-Reader für `litzentrum-library-v1.json` umgesetzt. Er ist bewusst read-only und ergänzt die Desktop-App für Recherche unterwegs.

## Enthalten

- Import per Datei-Dialog und Drag-and-drop
- Demo-Modus über Button oder `?demo=1`
- Projekt- und Quellenansicht mit Suche
- Detailansicht für Metadaten, Notizen, Zitate, Aufgaben, Zusammenfassungen und Dateihinweise
- Zitierkopie für BibTeX-Key, Kurzverweis und einzelne Zitate
- Lokale Wiederherstellung der zuletzt geladenen Bibliothek
- Web App Manifest und Service Worker für Offline-Nutzung
- Mobile-PWA-Status für Android, iOS und Offline-Cache
- Automatischer Mobile-PWA-Preflight für Manifest, Service Worker, Markup und Touch-Ziele

## Start lokal

```bash
cd web_companion
python -m http.server 8767
```

Danach im Browser öffnen:

- `http://127.0.0.1:8767/`
- `http://127.0.0.1:8767/?demo=1`

## Tests

```bash
node --test web_companion/tests/library.test.mjs
node --test web_companion/tests/mobile-pwa.test.mjs
node --check web_companion/app.js
node --check web_companion/library.js
node --check web_companion/sw.js
```

Der Preflight ersetzt keinen echten Gerätetest. Für Release-Entscheidungen bleiben Android-Chrome- und iOS-Safari-Smokes mit realem Import, Suche, Zitierkopie und Offline-Start separat zu prüfen.

## Nicht-Ziele

- Kein PDF-Upload auf einen Server
- Keine direkte Bearbeitung der Desktop-Projektordner
- Keine Ollama-Funktionen im Browser
- Kein nativer Mobile-Vollklon
