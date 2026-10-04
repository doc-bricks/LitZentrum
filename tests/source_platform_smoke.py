#!/usr/bin/env python3
"""Cross-platform source smoke for LitZentrum.

The smoke exercises the source install path used on macOS and Linux:
create a project, reopen it, display one source in the GUI, export BibTeX,
and write the read-only companion bundle.
"""
from __future__ import annotations

import json
import os
import platform
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from core import LibraryExporter, ProjectManager, SourceManager
from formats import LiMeta, LiNote, LiQuote, LiSum, LiTask
from modules.bibliography.bibtex import BibTeXGenerator


def _build_sample_project(workspace: Path):
    project_manager = ProjectManager()
    project = project_manager.create_project(
        path=workspace / "Überblick Studie",
        name="Überblick Studie",
        description="Source-Smoke für macOS und Linux",
        citation_style="apa",
    )
    source_manager = SourceManager(project.path, project.config.sources_folder)

    source = source_manager.create_source(
        LiMeta(
            title="Ärztliche Übersicht zur Mobilität",
            authors=["Müller, Jörg"],
            year=2026,
            journal="Journal für Reproduzierbarkeit",
            pages="12-18",
            abstract="Kurze Übersicht mit echten Umlauten.",
            tags=["größer", "mobilität", "smoke"],
            source_type="article",
            verified=True,
        )
    )

    notes = LiNote()
    notes.add("Notiz zur Quellenanzeige mit Übung", page=2, tags=["prüfung"])
    notes.notes[0].updated_at = notes.notes[0].created_at
    source_manager.save_notes(source, notes)

    quotes = LiQuote()
    quotes.add("Direktes Zitat mit Umlaut äöü", page=3, tags=["zitat"])
    source_manager.save_quotes(source, quotes)

    tasks = LiTask()
    tasks.add("BibTeX-Export prüfen", priority="high", page=4)
    source_manager.save_tasks(source, tasks)

    summaries = LiSum()
    summaries.add("Kurzüberblick", "Zusammenfassung mit Größe und Überblick", tags=["smoke"])
    summaries.summaries[0].updated_at = summaries.summaries[0].created_at
    source_manager.save_summaries(source, summaries)

    return project_manager, project, source_manager, source


def _exercise_gui(project_path: Path, workspace: Path) -> str:
    from PySide6.QtCore import QSettings
    from PySide6.QtWidgets import QApplication

    import core.settings_manager as settings_module

    settings_dir = workspace / "qt-settings"
    settings_dir.mkdir(parents=True, exist_ok=True)
    QSettings.setDefaultFormat(QSettings.Format.IniFormat)
    QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, str(settings_dir))
    settings_module._settings_instance = None

    from gui.main_window import MainWindow

    app = QApplication.instance() or QApplication(["litzentrum-source-platform-smoke"])
    window = MainWindow()
    try:
        window._load_project(project_path)
        assert window.project_manager.current_project is not None
        assert window.project_label.text().endswith("Überblick Studie")
        assert window.source_manager is not None

        sources = window.source_manager.get_all_sources()
        assert len(sources) == 1
        window._on_source_selected(sources[0])

        assert window.detail_panel.title_label.text() == "Ärztliche Übersicht zur Mobilität"
        assert window.sources_label.text() == "1 Quellen"
        return window.detail_panel.title_label.text()
    finally:
        window.deleteLater()
        app.processEvents()


def run_source_platform_smoke() -> dict:
    with tempfile.TemporaryDirectory(prefix="litzentrum-platform-") as tmpdir:
        workspace = Path(tmpdir)
        _build_sample_project(workspace)

        reopened_manager = ProjectManager()
        reopened_project = reopened_manager.open_project(workspace / "Überblick Studie")
        reopened_sources = SourceManager(
            reopened_project.path,
            reopened_project.config.sources_folder,
        )

        sources = reopened_sources.get_all_sources()
        assert len(sources) == 1
        assert reopened_sources.search_sources("mobilität")
        assert sources[0].meta.title == "Ärztliche Übersicht zur Mobilität"

        export_dir = workspace / "exports"
        bib_path = export_dir / "literatur"
        BibTeXGenerator().save_bibliography([source.meta for source in sources], bib_path)
        bib_file = bib_path.with_suffix(".bib")
        bib_text = bib_file.read_text(encoding="utf-8")
        assert "@article{mueller_2026_aerztliche," in bib_text
        assert "title = {Ärztliche Übersicht zur Mobilität}" in bib_text
        assert "author = {Müller, Jörg}" in bib_text

        bundle_path = LibraryExporter(reopened_manager, reopened_sources).export_project(
            reopened_project,
            export_dir / "litzentrum-library-v1.json",
        )
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        dumped_bundle = json.dumps(bundle, ensure_ascii=False)
        exported_source = bundle["projects"][0]["sources"][0]
        assert exported_source["metadata"]["title"] == "Ärztliche Übersicht zur Mobilität"
        assert exported_source["notes"][0]["content"] == "Notiz zur Quellenanzeige mit Übung"
        assert "Ärztliche Übersicht zur Mobilität" in bundle["bibliography"]["bibtex"]
        assert str(workspace) not in dumped_bundle

        gui_title = _exercise_gui(reopened_project.path, workspace)

        return {
            "platform": platform.system(),
            "source_count": len(sources),
            "gui_title": gui_title,
            "bibtex_bytes": len(bib_file.read_bytes()),
            "bundle_bytes": len(bundle_path.read_bytes()),
        }


def test_source_platform_smoke():
    result = run_source_platform_smoke()
    assert result["source_count"] == 1
    assert result["gui_title"] == "Ärztliche Übersicht zur Mobilität"
    assert result["bibtex_bytes"] > 100
    assert result["bundle_bytes"] > 1000


if __name__ == "__main__":
    print(json.dumps(run_source_platform_smoke(), ensure_ascii=False, indent=2))
