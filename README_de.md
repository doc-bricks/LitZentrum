# LitZentrum

[English](README.md)

**Ordnerbasierte Literaturverwaltung für wissenschaftliches Schreiben.**

LitZentrum ist eine Desktop-Anwendung zur Verwaltung akademischer Literatur in lokalen Projektordnern. Die Anwendung verbindet UTF-8-JSON-Speicherformate, PDF-Workflows, Notizen, Zitate, Aufgaben, Zusammenfassungen, BibTeX-Export und optionale lokale KI-Unterstützung über Ollama.

## Funktionen

- Ordnerbasiertes System: jede Quelle liegt in einem eigenen Ordner.
- PDF-Integration: Import, Vorschau, Textextraktion und Volltext-Workflows.
- Notizen und Zitate: Seitenverweise, Tags und Kategorien.
- Aufgabenverwaltung: projektweit und pro Quelle.
- Zusammenfassungen: manuell oder optional KI-gestützt.
- Bibliografie: BibTeX-Export und mehrere Zitierstile.
- Companion-Export: `litzentrum-library-v1.json` für read-only Web/PWA-Reader ohne PDF-Binärdaten.
- Optionale KI-Integration: lokale Verarbeitung mit Ollama.
- Git-freundliches Projektlayout für versionierte Forschungsarbeit.

## Screenshots

![Hauptfenster](README/screenshots/main.png)

## Installation

```bash
git clone https://github.com/doc-bricks/LitZentrum.git
cd LitZentrum
pip install -r requirements.txt
python src/main.py
```

## Voraussetzungen

- Python 3.10+
- PySide6
- PyMuPDF
- bibtexparser
- jsonschema
- requests, nur für die optionale Ollama-Integration

## Projektstruktur

```text
LitZentrum/
+-- src/
|   +-- main.py                 # Einstiegspunkt
|   +-- core/                   # Projekt-, Quellen- und Exportlogik
|   +-- formats/                # .li*-JSON-Dateiformate
|   +-- gui/                    # PySide6-Oberfläche
|   +-- modules/                # Bibliografie, PDF, KI und Sync
+-- schemas/                    # JSON-Schemas
+-- tests/                      # Regressionstests
+-- resources/                  # Icons und statische Assets
```

## Dateiformate

Alle Projektdaten werden als UTF-8-JSON gespeichert:

| Format | Beschreibung |
|---|---|
| `.liproj` | Projektkonfiguration |
| `.limeta` | Quellenmetadaten |
| `.linote` | Notizen |
| `.liquote` | Zitate |
| `.litask` | Aufgaben |
| `.lisum` | Zusammenfassungen |
| `litzentrum-library-v1.json` | Read-only Companion-Exportbündel |

Der Companion-Export enthält Projekte, Quellen, Metadaten, Notizen, Zitate, Aufgaben, Zusammenfassungen und BibTeX. Er enthält keine PDF-Dateien, keine PDF-Binärdaten und keine absoluten lokalen Pfade.

## Projektlayout

```text
MeinProjekt/
+-- projekt_config.liproj
+-- projekt_tasks.litask
+-- projekt_notes.linote
+-- Quellen/
|   +-- Smith2023_Understanding_AI/
|   |   +-- meta.limeta
|   |   +-- notes.linote
|   |   +-- quotes.liquote
|   |   +-- tasks.litask
|   |   +-- summaries.lisum
|   |   +-- source.pdf
|   +-- Doe2024_Machine_Learning/
|       +-- ...
```

## Zitierstile

- APA 7
- MLA 9
- Chicago
- DIN 1505-2
- Harvard

## Optionale KI-Integration

LitZentrum kann eine lokale Ollama-Installation für optionale KI-gestützte Zusammenfassungen, Zitatextraktion und Metadatenunterstützung verwenden.

```bash
ollama run mistral
```

## Entwicklung

```bash
pip install -r requirements.txt
python -m pytest -q
python -m py_compile src/main.py
```

## Lizenz

AGPL v3. Siehe [LICENSE](LICENSE).

Dieses Projekt verwendet PySide6 (LGPL) und PyMuPDF (AGPL).

## Haftung

Dieses Projekt ist eine unentgeltliche Open-Source-Schenkung im Sinne der §§ 516 ff. BGB. Die Haftung des Urhebers ist gemäß § 521 BGB auf Vorsatz und grobe Fahrlässigkeit beschränkt.

Nutzung auf eigenes Risiko. Keine Wartungszusage, keine Verfügbarkeitsgarantie, keine Gewähr für Fehlerfreiheit oder Eignung für einen bestimmten Zweck.
