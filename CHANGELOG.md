# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Hinzugefügt / Added
- `build_exe.bat` für den direkten Windows-Desktop-Build mit lokalem Build-Venv, gemeinsamem Exclude-Scanner, `dist\LitZentrum.exe` und versionierter Release-EXE `releases\v1.0.0\LitZentrum-1.0.0-win64.exe`
- Regressionstest `tests/test_release_materials.py` für `build_exe.bat`, README-Hinweise und den Ignore-Schutz für interne Aufgabenvarianten
- Reproduzierbarer Windows-Store-Buildpfad `releases/windowsstore/build_store_release.ps1` mit PyInstaller-Build, Store-Pretest, MSIX-Bau und Hash-Ausgabe
- `generate_store_assets.py` erzeugt `store_assets/` aus `LitZentrum.ico` für den MSIX-/Store-Pfad
- `releases/windowsstore/BUILD.md`, `releases/windowsstore/WACK_PROTOCOL.md` und `releases/windowsstore/SHA256SUMS.txt` dokumentieren den verifizierten Windows-Store-Lauf
- README, README_de and `llms.txt` now include clearer discovery context for local-first literature management, bibliography/citation workflows, PDF-backed academic writing and differentiation from Zotero, Mendeley, JabRef, Calibre and cloud reference platforms
- Reproduzierbarer Windows-Store-Screenshot-Generator `generate_store_screenshots.py`, der aus anonymisierten Demo-Daten vier Store-Bilder (`main.png`, `quotes-workflow.png`, `bibtex-export.png`, `companion-export.png`) plus `summary.json` erzeugt
- Regressionstest `tests/test_store_screenshots.py` für die PNG-Erzeugung und das Screenshot-Inventar
- `web_companion`: `apple-touch-icon` für iOS-Homescreen-Unterstützung hinzugefügt; `purpose: "any"` zu `manifest.webmanifest`-Icons ergänzt; `mobile-pwa.test.mjs` mit strikteren Assertions für Icon-Anzahl, maskable-Icons, apple-touch-icon und theme-color erweitert
- `*.bak` zu `.gitignore` hinzugefügt (Web-Companion-Backup-Dateien)
- `llms.txt` um Docs-Abschnitt, Audience (5 Zielgruppen), Search Phrases (7 Phrasen) und Last-checked: 2026-06-10 ergänzt
- Smoke-Tests für Core-Module (tests/test_smoke.py, 10 Tests: EventType, SearchResult, ExportOptions, ImportResult, PDFSelection, Statistics)
- Ollama-Modellauswahl: ComboBox wird automatisch mit verfügbaren Modellen befüllt (_fetch_ollama_models, _populate_model_combo)
- "Modelle laden" Button neben "Verbindung testen" im Einstellungen-Dialog
- Read-only-Desktop-Export `litzentrum-library-v1.json` mit JSON-Schema, GUI-Aktion und Regressionstests für UTF-8, relative Pfade, fehlende PDFs und leere Projekte
- English-first `README.md`, separate `README_de.md` und `llms.txt` für maschinenlesbaren Projektkontext
- Statischer `web_companion/`-Offline-Reader für `litzentrum-library-v1.json` mit Import, Suche, Zitierkopie, lokaler Wiederherstellung, Manifest, Service Worker und Node-Regressionstests
- Mobile-PWA-Preflight für Android/iOS: Statusanzeige, Touch-Ziele, Safe-Area-CSS, Offline-Navigation und statische Node-Smokes
- Automatisierter macOS-/Linux-Source-Smoke für Projektstart, Projektöffnung, Quellenanzeige, BibTeX-Export und `litzentrum-library-v1.json`; GitHub Actions ergänzt eine Ubuntu-/macOS-Matrix
- Windows-Store-Basisartefakte: `store_package.json`, `STORE_LISTING.md`, `PRIVACY_POLICY.md`, `SUPPORT.md`, `WINDOWS_STORE_PREP.md`, Screenshot-Inventar und `tests/test_store_materials.py`

### Geändert / Changed
- Windows-Store Partner-Center-Metadaten in `store_package.json` vervollständigt (Publisher DN `CN=52596601-BAB4-4F3F-B182-E8F3F273B202`, Publisher Display Name `Lukas Geiger`, Price `Free`, Sprachen `de-DE`/`en-US`, Logo-Pfad); `test_store_materials.py` erweitert (99/99 Pytest grün); `WINDOWS_STORE_PREP.md` & `AUFGABEN.txt` (`TW-LITZENTRUM-02`) aktualisiert
- `.gitignore` ignoriert jetzt zusätzlich `AUFGABEN-*.txt`, damit maschinenspezifische Aufgabenvarianten nicht versehentlich in Git landen
- README und README_de dokumentieren jetzt den direkten Windows-EXE-Build getrennt vom Store-spezifischen EXE-/MSIX-Pfad
- `WINDOWS_STORE_PREP.md`, `AUFGABEN.txt`, `PORTIERUNGSPLAN.md`, README und README_de spiegeln jetzt den realen lokalen EXE-/MSIX-Stand; offen bleibt nur noch der erhöhte WACK-Lauf
- Verbindungstest aktualisiert ComboBox automatisch bei Erfolg (Ollama)
- Portierungsstatus aktualisiert: Der Web/PWA-Companion hat jetzt einen automatisierten mobilen Preflight; der Desktop-Source-Smoke-Pfad ist für Ubuntu/macOS vorbereitet; echte Android-/iOS-Geräte-Smokes bleiben separat offen
- Windows-Store-Doku verweist jetzt auf das vorhandene Screenshot-Set statt nur auf einen Planungsplatzhalter
- Community-Workflows auf aktuelle Actions-Versionen und Input-Namen aktualisiert
- Lokale `*-library-v1.json`-Exportdateien werden ignoriert
- README und README_de dokumentieren jetzt zusätzlich den Windows-Store-Basisstand

### Behoben / Fixed
- `web_companion/icons/apple-touch-icon-180.png`: Alphakanal ergänzt (RGB → RGBA, gleiche 180x180-Auflösung) für saubere Transparenz auf iOS-Homescreens
- Unreferenzierte Icon-Duplikate/-Waisen (Root-`assets/*.png`, doppelte `apple-touch-icon`/`favicon`-Kopien außerhalb von `web_companion/icons/`) aus dem Arbeitsbaum nach `_archive/` verschoben statt versehentlich zu committen — kein Code-/Manifest-/HTML-Verweis nutzte sie
- `bibtex_generator.py`: Freitextfelder (Titel, Autoren, Journal/Booktitle, Publisher, Abstract, Keywords) werden jetzt mit `escape_bibtex` aus `bibtex.py` escaped — kein doppelter Implementierungs-Fork; URL/DOI/ISBN bleiben verbatim. Regressions-test: `test_legacy_bibtex_generator_escapes_field_values` (Run 74, 2026-06-28)
- `to_optional_year` in `base.py` eingeführt: konvertiert Float-Strings ("2023.0" → 2023) korrekt; behandelt None, leere Strings und "kein Datum"-Marker ("n.d.", "o.J." usw.) defensiv als None. `limeta.py` nutzt jetzt `to_optional_year` statt `to_optional_int` für das year-Feld; `to_optional_int` für page/page_end bleibt unverändert. Regressionstests: `tests/test_year_coercion.py`.
- BibTeX-Entry-Keys im aktuellen und Legacy-Generator nutzen jetzt den vorhandenen ASCII-`bibtex_key` statt unsanitisiertem `citation_key`, damit Autoren wie `AT&T` oder `O'Brien` keine ungültigen Entry-Keys erzeugen
- `start.bat` prüft die lokale Python-Umgebung jetzt auf `PySide6` statt auf das veraltete `PyQt6`
- Bare except in settings_manager.py, project_tree.py, ollama_queue.py, bibtex.py, extractor.py, sync/__init__.py durch spezifische Exceptions ersetzt
- TODO-Stellen in detail_panel.py und summaries_tab.py aufgeräumt
- BibTeX-Export legt Zielordner jetzt an und ergänzt fehlende `.bib`-Suffixe

## [1.0.0] - 2026-01-01

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release
- Ordnerbasiertes Literaturverwaltungssystem
- Eigene Dateiformate: .liproj, .limeta, .linote, .liquote, .litask, .lisum
- PDF-Integration (PyMuPDF), BibTeX-Export, Ollama KI-Integration (optional)
