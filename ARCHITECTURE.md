# 🏗️ LitZentrum - Architektur-Skizze

> Stand: 2026-07-22. Die aktuelle Desktop-GUI nutzt PySide6. Die frühere PyQt6-Basis wurde am 2026-03-15 migriert; PyQt6-Nennungen beschreiben ausschließlich diese Historie.

## Hauptfenster-Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              LitZentrum                                     │
│                      Literaturverwaltung & Wissensmanagement               │
├─────────────────────────────────────────────────────────────────────────────┤
│  [Datei] [Bearbeiten] [Ansicht] [Quellen] [Export] [KI] [Hilfe]            │
├─────────────────────────────────────────────────────────────────────────────┤
│  [📂 Neues Projekt] [➕ Quelle] [🔍 Suche] [📖 Bibliografie] [⚙️]          │
├───────────────┬─────────────────────────────┬───────────────────────────────┤
│               │                             │                               │
│  PROJEKTBAUM  │      QUELLEN-LISTE          │       DETAIL-PANEL            │
│               │                             │                               │
│  📚 Projekte  │  ┌─────────────────────┐    │  ┌─────────────────────────┐ │
│  ├─📁 Master- │  │Quelle     │Status  │    │  │      METADATEN          │ │
│  │  arbeit    │  ├───────────┼────────┤    │  │                         │ │
│  │  ├─📄Smith │  │Smith2023  │ ✅ Done│    │  │  Titel: Understanding.. │ │
│  │  ├─📄Müller│  │Müller2022 │ ⏳ Read│    │  │  Autor: Smith, John     │ │
│  │  └─📄Weber │  │Weber2021  │ 📝 Note│    │  │  Jahr:  2023            │ │
│  │            │  └───────────┴────────┘    │  │  DOI:   10.1234/...     │ │
│  ├─📁 Haus-   │                             │  │  Tags:  [AI] [Methodik] │ │
│  │  arbeit    │  Filter: [Alle ▼]          │  │                         │ │
│  │            │  Sortierung: [Name ▼]      │  │  [Bearbeiten] [Öffnen]  │ │
│  └─📁 Seminar │                             │  └─────────────────────────┘ │
│               │                             │                               │
│  ─────────────│                             │  ┌─────────────────────────┐ │
│  ⭐ Favoriten │                             │  │ [Notizen][Zitate]       │ │
│  🏷️ Tags      │                             │  │ [Aufgaben][Summaries]   │ │
│  📊 Statistik │                             │  ├─────────────────────────┤ │
│               │                             │  │                         │ │
│               │                             │  │  📝 Notizen (3)         │ │
│               │                             │  │  ├─ n001: Wichtige...   │ │
│               │                             │  │  ├─ n002: Vergleich...  │ │
│               │                             │  │  └─ n003: TODO: ...     │ │
│               │                             │  │                         │ │
│               │                             │  │  [+ Neue Notiz]         │ │
│               │                             │  └─────────────────────────┘ │
├───────────────┴─────────────────────────────┴───────────────────────────────┤
│  Status: 📚 3 Projekte │ 📄 12 Quellen │ 📝 45 Zitate │ KI: 🟢 Bereit       │
└─────────────────────────────────────────────────────────────────────────────┘
```

## System-Architektur

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              LitZentrum                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                           GUI LAYER                                   │ │
│  │                                                                       │ │
│  │   MainWindow ─┬─ ProjectTree ────── QTreeWidget                      │ │
│  │               │                                                       │ │
│  │               ├─ SourceList ─────── QTableWidget                     │ │
│  │               │                                                       │ │
│  │               └─ DetailPanel ─┬─── MetadataWidget                    │ │
│  │                               ├─── NotesTab                          │ │
│  │                               ├─── QuotesTab                         │ │
│  │                               ├─── TasksTab                          │ │
│  │                               └─── SummariesTab                      │ │
│  │                                                                       │ │
│  │   Dialogs ────┬─ SourceDialog (Quelle hinzufügen/bearbeiten)        │ │
│  │               ├─ QuoteDialog (Zitat erstellen)                       │ │
│  │               ├─ BibliographyDialog (Export)                         │ │
│  │               └─ AIQueueDialog (KI-Warteschlange)                    │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                        │                                    │
│  ┌─────────────────────────────────────┴────────────────────────────────┐  │
│  │                          CORE LAYER                                  │  │
│  │                                                                      │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────────┐    │  │
│  │  │ ProjectManager  │  │  SourceManager  │  │   FormatHandler   │    │  │
│  │  │                 │  │                 │  │                   │    │  │
│  │  │ • create()      │  │ • addSource()   │  │ • .limeta         │    │  │
│  │  │ • open()        │  │ • getMetadata() │  │ • .linote         │    │  │
│  │  │ • listProjects()│  │ • updateStatus()│  │ • .litask         │    │  │
│  │  └─────────────────┘  └─────────────────┘  │ • .lisum          │    │  │
│  │                                            │ • .liquote        │    │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  └───────────────────┘    │  │
│  │  │ ProfilerBridge  │  │BibliographyGen  │                           │  │
│  │  │   (Index)       │  │                 │  ┌───────────────────┐    │  │
│  │  │                 │  │ • toBibTeX()    │  │   SyncManager     │    │  │
│  │  │ • index()       │  │ • toAPA()       │  │   (ProSync)       │    │  │
│  │  │ • search()      │  │ • toMLA()       │  │                   │    │  │
│  │  │ • hash()        │  │ • toDIN()       │  │ • backup()        │    │  │
│  │  └─────────────────┘  └─────────────────┘  │ • restore()       │    │  │
│  │                                            └───────────────────┘    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                        │                                    │
│  ┌─────────────────────────────────────┴────────────────────────────────┐  │
│  │                       MODULE LAYER                                   │  │
│  │                                                                      │  │
│  │  ┌───────────────────────────────────────────────────────────────┐  │  │
│  │  │                    PDF-WERKSTATT                               │  │  │
│  │  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────────┐  │  │  │
│  │  │  │PDFSchwärzer│ │pdfmarker  │ │ PDFtoOCR  │ │  PDFunlock    │  │  │  │
│  │  │  │   Pro     │ │  2000     │ │           │ │               │  │  │  │
│  │  │  │           │ │           │ │           │ │               │  │  │  │
│  │  │  │• Redaction│ │• Markieren│ │• OCR      │ │• Entsperren   │  │  │  │
│  │  │  │• Fuzzy    │ │• Auszüge  │ │• Tesseract│ │• Passwort     │  │  │  │
│  │  │  └───────────┘ └───────────┘ └───────────┘ └───────────────┘  │  │  │
│  │  └───────────────────────────────────────────────────────────────┘  │  │
│  │                                                                      │  │
│  │  ┌───────────────────────────────────────────────────────────────┐  │  │
│  │  │                    KI-ASSISTANT (Optional)                    │  │  │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │  │  │
│  │  │  │OllamaQueue  │  │ Summarizer  │  │   MetadataLookup    │   │  │  │
│  │  │  │             │  │             │  │                     │   │  │  │
│  │  │  │• Job Queue  │  │• Mistral    │  │• ISBN → OpenLibrary │   │  │  │
│  │  │  │• Background │  │• Claude     │  │• DOI → CrossRef     │   │  │  │
│  │  │  │• Priority   │  │• Summary    │  │• Auto-Fill          │   │  │  │
│  │  │  └─────────────┘  └─────────────┘  └─────────────────────┘   │  │  │
│  │  └───────────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                        │                                    │
│  ┌─────────────────────────────────────┴────────────────────────────────┐  │
│  │                        DATA LAYER                                    │  │
│  │                                                                      │  │
│  │   Projekt_A/                                                        │  │
│  │   ├── Quellen/                                                      │  │
│  │   │   └── Smith2023_AI/                                             │  │
│  │   │       ├── source.pdf        # Original                          │  │
│  │   │       ├── meta.limeta       # {"title": "...", "authors": [...]}│  │
│  │   │       ├── notes.linote      # [{"id": "n001", "text": "..."}]   │  │
│  │   │       ├── tasks.litask      # [{"id": "t001", "status": "open"}]│  │
│  │   │       ├── summaries.lisum   # [{"id": "s001", "source": "ai"}]  │  │
│  │   │       └── quotes.liquote    # [{"id": "q001", "type": "direct"}]│  │
│  │   │                                                                  │  │
│  │   ├── projekt_biblio.bib        # Generiertes Literaturverzeichnis  │  │
│  │   ├── projekt_tasks.litask      # Projektweite Aufgaben             │  │
│  │   └── projekt_config.liproj     # Projekteinstellungen              │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Markierung-zu-Zitat Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│              MARKIERUNG → ZITAT WORKFLOW                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌────────────────┐                                           │
│   │  PDF öffnen    │                                           │
│   │  (pdfmarker)   │                                           │
│   └───────┬────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│   ┌────────────────┐                                           │
│   │  Text markieren│                                           │
│   │  (Highlight)   │                                           │
│   └───────┬────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│   ┌────────────────┐     ┌────────────────┐                   │
│   │ Rechtsklick:   │────▶│  QuoteDialog   │                   │
│   │ "Als Zitat     │     │                │                   │
│   │  übernehmen"   │     │ • Text (auto)  │                   │
│   └────────────────┘     │ • Seite (auto) │                   │
│                          │ • Typ wählen   │                   │
│                          │ • Tags         │                   │
│                          │ • Kommentar    │                   │
│                          └───────┬────────┘                   │
│                                  │                             │
│                                  ▼                             │
│                          ┌────────────────┐                   │
│                          │ quotes.liquote │                   │
│                          │   aktualisiert │                   │
│                          └────────────────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## KI-Queue System

```
┌─────────────────────────────────────────────────────────────────┐
│                    OLLAMA QUEUE SYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐   │
│  │   User      │   │  AI Queue   │   │   Ollama Server     │   │
│  │  Request    │──▶│   Worker    │──▶│   (Local)           │   │
│  └─────────────┘   └──────┬──────┘   └──────────┬──────────┘   │
│                           │                      │              │
│  Jobs:                    ▼                      ▼              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Queue: [Job1: Summarize] [Job2: Extract] [Job3: ...]   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  summaries.lisum ← Ergebnis einfügen                    │   │
│  │  {                                                       │   │
│  │    "id": "s002",                                         │   │
│  │    "source": "ai_ollama_mistral",                       │   │
│  │    "scope": "section_2.3",                              │   │
│  │    "text": "- Punkt 1...\n- Punkt 2...",               │   │
│  │    "model": "mistral:latest"                            │   │
│  │  }                                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Technologie-Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                    TECHNOLOGIE-STACK                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  GUI:        PySide6 (Widgets, Dialogs, Panels)                │
│                                                                 │
│  PDF:        PyMuPDF (fitz), pikepdf, pdf2image               │
│                                                                 │
│  OCR:        pytesseract + Tesseract Portable                  │
│                                                                 │
│  Datenbank:  SQLite3 (ProFiler Index) + JSON (Quellen-Daten)  │
│                                                                 │
│  Bibliografie: bibtexparser, citeproc-py                       │
│                                                                 │
│  KI:         ollama (lokal), anthropic (optional)              │
│                                                                 │
│  Export:     python-docx (Word), ReportLab (PDF)               │
│                                                                 │
│  Sync:       shutil, hashlib (ProSync)                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```


---

## 📦 IMPLEMENTIERUNG (Stand: 03.01.2026)

### Erstellte Dateien (~50 Dateien, ~5700 Zeilen)

```
LitZentrum/
├── README.md                       # Dokumentation
├── requirements.txt                # Abhängigkeiten
├── setup.py                        # Installation
├── start.bat                       # Windows-Starter
│
├── schemas/                        # JSON-Schemas
│   ├── limeta.schema.json
│   ├── linote.schema.json
│   ├── liquote.schema.json
│   ├── litask.schema.json
│   ├── lisum.schema.json
│   └── liproj.schema.json
│
├── src/
│   ├── main.py                     # Einstiegspunkt
│   │
│   ├── core/                       # Kernlogik
│   │   ├── __init__.py
│   │   ├── project_manager.py      # Projektverwaltung
│   │   ├── source_manager.py       # Quellenverwaltung
│   │   ├── event_bus.py            # Event-System
│   │   └── settings_manager.py     # Einstellungen
│   │
│   ├── formats/                    # Datei-Formate
│   │   ├── __init__.py
│   │   ├── base.py                 # Basisklasse
│   │   ├── limeta.py               # Metadaten
│   │   ├── linote.py               # Notizen
│   │   ├── liquote.py              # Zitate
│   │   ├── litask.py               # Aufgaben
│   │   ├── lisum.py                # Zusammenfassungen
│   │   └── liproj.py               # Projekt-Config
│   │
│   ├── models/                     # Datenmodelle
│   │   └── __init__.py             # SearchResult, Statistics, etc.
│   │
│   ├── gui/                        # Benutzeroberfläche
│   │   ├── __init__.py
│   │   ├── main_window.py          # Hauptfenster
│   │   │
│   │   ├── panels/                 # 3-Panel-Layout
│   │   │   ├── __init__.py
│   │   │   ├── project_tree.py     # Links: Projektbaum
│   │   │   ├── source_list.py      # Mitte: Quellenliste
│   │   │   └── detail_panel.py     # Rechts: Details+Tabs
│   │   │
│   │   ├── tabs/                   # Detail-Tabs
│   │   │   ├── __init__.py
│   │   │   ├── pdf_tab.py          # PDF-Viewer
│   │   │   ├── notes_tab.py        # Notizen
│   │   │   ├── quotes_tab.py       # Zitate
│   │   │   ├── tasks_tab.py        # Aufgaben
│   │   │   └── summaries_tab.py    # Zusammenfassungen
│   │   │
│   │   ├── dialogs/                # Dialoge
│   │   │   ├── __init__.py
│   │   │   ├── new_project_dialog.py
│   │   │   ├── source_dialog.py
│   │   │   └── settings_dialog.py
│   │   │
│   │   └── widgets/                # Wiederverwendbare Widgets
│   │       ├── __init__.py
│   │       └── pdf_viewer.py       # PDF-Betrachter
│   │
│   └── modules/                    # Erweiterungen
│       ├── __init__.py
│       │
│       ├── bibliography/           # Bibliografie
│       │   ├── __init__.py
│       │   ├── bibtex.py           # BibTeX Generator/Parser
│       │   └── styles.py           # Zitationsstile
│       │
│       ├── pdf_workshop/           # PDF-Verarbeitung
│       │   ├── __init__.py
│       │   └── extractor.py        # Text-Extraktion
│       │
│       ├── ai/                     # KI-Integration
│       │   ├── __init__.py
│       │   └── ollama_queue.py     # Ollama Job-Queue
│       │
│       └── sync/                   # Synchronisation
│           └── __init__.py         # Git + Backup
│
├── tests/
│   └── test_formats.py             # Unit-Tests
│
└── resources/icons/                # Icons (Platzhalter)
```

### Status: MVP READY ✅

Die Grundstruktur ist vollständig implementiert. 
Zum Starten: `python src/main.py` oder `start.bat`
