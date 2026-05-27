# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Hinzugefügt / Added
- Smoke-Tests für Core-Module (tests/test_smoke.py, 10 Tests: EventType, SearchResult, ExportOptions, ImportResult, PDFSelection, Statistics)
- Ollama-Modellauswahl: ComboBox wird automatisch mit verfügbaren Modellen befüllt (_fetch_ollama_models, _populate_model_combo)
- "Modelle laden" Button neben "Verbindung testen" im Einstellungen-Dialog

### Geändert / Changed
- Verbindungstest aktualisiert ComboBox automatisch bei Erfolg (Ollama)

### Behoben / Fixed
- Bare except in settings_manager.py, project_tree.py, ollama_queue.py, bibtex.py, extractor.py, sync/__init__.py durch spezifische Exceptions ersetzt
- TODO-Stellen in detail_panel.py und summaries_tab.py aufgeräumt
- BibTeX-Export legt Zielordner jetzt an und ergänzt fehlende `.bib`-Suffixe

## [1.0.0] - 2026-01-01

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release
- Ordnerbasiertes Literaturverwaltungssystem
- Eigene Dateiformate: .liproj, .limeta, .linote, .liquote, .litask, .lisum
- PDF-Integration (PyMuPDF), BibTeX-Export, Ollama KI-Integration (optional)
