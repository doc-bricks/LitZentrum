# Datenschutz - LitZen

Stand: 2026-06-04

## Kurzfassung

LitZen arbeitet lokal auf dem Gerät. Die App lädt Literaturprojekte, PDFs,
Notizen, Zitate, Aufgaben oder Zusammenfassungen nicht in einen eigenen
Cloud-Dienst hoch und betreibt keinen zentralen Sync-Server.

## Welche Daten verarbeitet die App lokal?

- Projektordner, Quelldateien und zugehörige Metadaten
- lokale Notizen, Zitate, Aufgaben und Zusammenfassungen
- PDF-Verweise, Vorschaudaten und BibTeX-Exporte
- App-Einstellungen über Qt `QSettings`
- optional redigierte Companion-Exporte als `litzentrum-library-v1.json`

Diese Daten bleiben standardmäßig im vom Nutzer gewählten Projektordner oder in
den lokalen Anwendungseinstellungen.

## Welche Daten werden nicht standardmäßig übertragen?

- PDF-Inhalte oder komplette Literaturordner an einen LitZen-Server
- persönliche Forschungsdaten an eine Pflicht-Cloud
- Konten, Tracker, Telemetrie oder Werbe-IDs
- absolute lokale Pfade im Companion-Standardexport

Der Standardexport `litzentrum-library-v1.json` ist bewusst read-only und enthält
keine eingebetteten PDF-Binärdaten.

## Optionale Netzwerkzugriffe

Die Kern-App benötigt keinen eigenen Online-Dienst. Optionale Netzwerkzugriffe
entstehen nur, wenn Nutzer selbst externe Ziele verwenden, zum Beispiel:

- GitHub-Seiten aus README-, Support- oder Lizenzlinks
- eine lokale oder entfernte Ollama-Instanz für KI-gestützte Funktionen

Wenn Ollama nicht konfiguriert ist, bleibt LitZen vollständig lokal nutzbar.

## Open-Source- und Lizenzhinweis

LitZen steht unter AGPL-3.0. Die PDF-Verarbeitung kann PyMuPDF nutzen, das
ebenfalls im AGPL-Kontext steht. Weitere Lizenzhinweise für Drittkomponenten
werden vor dem finalen Windows-Store-Schritt zusätzlich in
`THIRD_PARTY_LICENSES.txt` gesammelt.

## Support und Rückfragen

Support- und Kontaktwege stehen in `SUPPORT.md`.
