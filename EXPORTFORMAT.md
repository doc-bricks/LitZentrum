# Exportformat LitZen

Stand: 2026-05-29

## Ziel

`litzentrum-library-v1.json` ist das implementierte Austauschformat zwischen der Desktop-Vollversion und einem Web/PWA-Companion. Es soll Bibliotheken mobil lesbar machen, ohne PDF-Dateien oder lokale absolute Pfade in eine Webumgebung zu übertragen.

## Grundregeln

- UTF-8, JSON, stabile Schema-Version.
- Keine absoluten lokalen Pfade wie `C:\Users\...`.
- Keine PDF-Binärdaten im Standardexport.
- Personen- und Projektdaten bleiben lokal; der Nutzer entscheidet aktiv, welche Bibliothek exportiert wird.
- Importierende Clients müssen unbekannte Felder ignorieren.

## Geplante Struktur

```json
{
  "schema": "litzentrum-library",
  "schema_version": "1.0",
  "app": {
    "name": "LitZentrum",
    "version": "1.0.0"
  },
  "exported_at": "2026-05-27T00:00:00+02:00",
  "capabilities": {
    "contains_pdf_files": false,
    "contains_pdf_text": false,
    "read_only_companion": true
  },
  "projects": [
    {
      "id": "project-001",
      "name": "Masterarbeit",
      "project_notes": [],
      "project_tasks": [],
      "sources": [
        {
          "id": "source-001",
          "folder_name": "Smith2023_AI",
          "metadata": {},
          "notes": [],
          "quotes": [],
          "tasks": [],
          "summaries": [],
          "files": [
            {
              "role": "source_pdf",
              "name": "source.pdf",
              "relative_path": "Quellen/Smith2023_AI/source.pdf",
              "sha256": "…optional…",
              "included": false,
              "exists": true
            }
          ]
        }
      ]
    }
  ],
  "bibliography": {
    "bibtex": "",
    "styles": ["apa", "mla", "chicago", "din", "harvard"]
  }
}
```

## Datenschutz und Grenzen

Der Standardexport ist ein Lesebündel. Er enthält Metadaten, projektweite Notizen und Aufgaben, quellenbezogene Notizen, Zitate, Aufgaben, Zusammenfassungen sowie BibTeX, aber keine PDF-Dateien und keinen vollständigen extrahierten PDF-Text. Für spätere Schreib- oder Sync-Funktionen ist ein separates Roundtrip-Format nötig.
