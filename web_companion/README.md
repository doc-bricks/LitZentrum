# LitZentrum Web/PWA Companion

Stand: 2026-06-01

Der Companion ist jetzt als statischer Offline-Reader für `litzentrum-library-v1.json` umgesetzt. Er ist bewusst read-only und ergänzt die Desktop-App für Recherche unterwegs.

## Enthalten

- Import per Datei-Dialog und Drag-and-drop
- Demo-Modus über Button oder `?demo=1`
- Projekt- und Quellenansicht mit Suche
- Detailansicht für Metadaten, Notizen, Zitate, Aufgaben, Zusammenfassungen und Dateihinweise
- Zitierkopie für BibTeX-Key, Kurzverweis und einzelne Zitate
- Lokale Wiederherstellung der zuletzt geladenen Bibliothek
- Web App Manifest und Service Worker für Offline-Nutzung

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
node --check web_companion/app.js
node --check web_companion/library.js
```

## Nicht-Ziele

- Kein PDF-Upload auf einen Server
- Keine direkte Bearbeitung der Desktop-Projektordner
- Keine Ollama-Funktionen im Browser
- Kein nativer Mobile-Vollklon
