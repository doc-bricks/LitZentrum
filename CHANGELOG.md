# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Hinzugefügt / Added
- Smoke-Tests für Core-Module (tests/test_smoke.py, 10 Tests: EventType, SearchResult, ExportOptions, ImportResult, PDFSelection, Statistics)
- Ollama-Modellauswahl: ComboBox wird automatisch mit verfügbaren Modellen befüllt (_fetch_ollama_models, _populate_model_combo)
- "Modelle laden" Button neben "Verbindung testen" im Einstellungen-Dialog
- Read-only-Desktop-Export `litzentrum-library-v1.json` mit JSON-Schema, GUI-Aktion und Regressionstests für UTF-8, relative Pfade, fehlende PDFs und leere Projekte
- English-first `README.md`, separate `README_de.md` und `llms.txt` für maschinenlesbaren Projektkontext
- Statischer `web_companion/`-Offline-Reader für `litzentrum-library-v1.json` mit Import, Suche, Zitierkopie, lokaler Wiederherstellung, Manifest, Service Worker und Node-Regressionstests
- Mobile-PWA-Preflight für Android/iOS: Statusanzeige, Touch-Ziele, Safe-Area-CSS, Offline-Navigation und statische Node-Smokes
- Automatisierter macOS-/Linux-Source-Smoke für Projektstart, Projektöffnung, Quellenanzeige, BibTeX-Export und `litzentrum-library-v1.json`; GitHub Actions ergänzt eine Ubuntu-/macOS-Matrix

### Geändert / Changed
- Verbindungstest aktualisiert ComboBox automatisch bei Erfolg (Ollama)
- Portierungsstatus aktualisiert: Der Web/PWA-Companion hat jetzt einen automatisierten mobilen Preflight; der Desktop-Source-Smoke-Pfad ist für Ubuntu/macOS vorbereitet; echte Android-/iOS-Geräte-Smokes bleiben separat offen
- Community-Workflows auf aktuelle Actions-Versionen und Input-Namen aktualisiert
- Lokale `*-library-v1.json`-Exportdateien werden ignoriert

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
