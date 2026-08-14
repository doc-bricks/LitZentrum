# Store-Screenshots - LitZen

Stand: 2026-08-14

## Vorhandenes Set

- `main.png` - Hauptfenster mit Projektbaum, Quellenliste, PDF-Vorschau und Detailbereich
- `quotes-workflow.png` - Zitat-Workflow mit Seitenbezug, Kommentar und Zitierhilfe
- `bibtex-export.png` - BibTeX-Exportvorschau mit lokalem Forschungs-Workflow
- `companion-export.png` - Companion-Exportvorschau für `litzentrum-library-v1.json`
- `summary.json` - Maschinelles Inventar der erzeugten Store-Screenshots

## Windows-Store-Set

1. `main.png`
   Hauptfenster mit Projektüberblick, Quellenliste und Detailansicht.
2. `quotes-workflow.png`
   Zitat- und Notizworkflow mit Seitenbezug und wissenschaftlichem Kontext.
3. `bibtex-export.png`
   BibTeX-Export oder Aufgaben-/Zusammenfassungsansicht mit produktivem Schreibworkflow.
4. `companion-export.png`
   Companion-Export oder Web/PWA-Reader mit `litzentrum-library-v1.json`.

## Reproduktion

Die Bilder werden reproduzierbar mit `python generate_store_screenshots.py`
aus anonymisierten Demo-Daten erzeugt. Der Generator nutzt den realen Qt-Pfad
für das Hauptfenster und Exportartefakte aus einem temporären Projekt ohne
private PDFs oder Nutzerpfade.
