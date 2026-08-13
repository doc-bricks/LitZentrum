from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_SCALE_FACTOR", "1.25")

from PySide6 import QtCore, QtWidgets


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import fitz

from core import LibraryExporter, ProjectManager, SourceManager
from formats import LiMeta, LiNote, LiQuote, LiSum, LiTask
from gui.main_window import MainWindow
from modules.bibliography.bibtex import BibTeXGenerator


SCREENSHOT_FILES = {
    "main": "main.png",
    "quotes": "quotes-workflow.png",
    "bibtex": "bibtex-export.png",
    "companion": "companion-export.png",
}

SUMMARY_FILE = "summary.json"


@dataclass
class DemoContext:
    project_manager: ProjectManager
    source_manager: SourceManager
    project_path: Path
    primary_title: str
    bibtex_path: Path
    bundle_path: Path
    bundle_data: dict


class StorePreviewWidget(QtWidgets.QWidget):
    def __init__(
        self,
        title: str,
        subtitle: str,
        cards: list[tuple[str, str]],
        section_title: str,
        body_text: str,
        footer: str,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.resize(1520, 920)
        self.setStyleSheet(
            """
            QWidget { background: #f4f6f9; color: #17212b; font-family: Segoe UI; }
            QFrame#hero { background: #17324d; border-radius: 18px; }
            QLabel#heroTitle { color: white; font-size: 28px; font-weight: 700; }
            QLabel#heroSubtitle { color: #d7e4f1; font-size: 14px; }
            QFrame#card { background: white; border: 1px solid #d7dfe7; border-radius: 14px; }
            QLabel#cardValue { font-size: 24px; font-weight: 700; color: #17324d; }
            QLabel#cardLabel { font-size: 12px; color: #4d5d6c; }
            QLabel#sectionTitle { font-size: 18px; font-weight: 700; color: #17324d; }
            QPlainTextEdit {
                background: #0e1620;
                color: #dce9f5;
                border: 1px solid #213547;
                border-radius: 14px;
                padding: 12px;
                font-family: Consolas;
                font-size: 11px;
            }
            QLabel#footer { color: #455564; font-size: 12px; }
            """
        )

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(18)

        hero = QtWidgets.QFrame()
        hero.setObjectName("hero")
        hero_layout = QtWidgets.QVBoxLayout(hero)
        hero_layout.setContentsMargins(24, 20, 24, 20)
        hero_title = QtWidgets.QLabel(title)
        hero_title.setObjectName("heroTitle")
        hero_subtitle = QtWidgets.QLabel(subtitle)
        hero_subtitle.setObjectName("heroSubtitle")
        hero_subtitle.setWordWrap(True)
        hero_layout.addWidget(hero_title)
        hero_layout.addWidget(hero_subtitle)
        root.addWidget(hero)

        cards_layout = QtWidgets.QHBoxLayout()
        cards_layout.setSpacing(14)
        for label, value in cards:
            card = QtWidgets.QFrame()
            card.setObjectName("card")
            card_layout = QtWidgets.QVBoxLayout(card)
            card_layout.setContentsMargins(18, 16, 18, 16)
            value_label = QtWidgets.QLabel(value)
            value_label.setObjectName("cardValue")
            label_label = QtWidgets.QLabel(label)
            label_label.setObjectName("cardLabel")
            card_layout.addWidget(value_label)
            card_layout.addWidget(label_label)
            cards_layout.addWidget(card, 1)
        root.addLayout(cards_layout)

        section = QtWidgets.QFrame()
        section.setObjectName("card")
        section_layout = QtWidgets.QVBoxLayout(section)
        section_layout.setContentsMargins(20, 18, 20, 18)
        section_label = QtWidgets.QLabel(section_title)
        section_label.setObjectName("sectionTitle")
        section_layout.addWidget(section_label)
        editor = QtWidgets.QPlainTextEdit()
        editor.setReadOnly(True)
        editor.setPlainText(body_text)
        section_layout.addWidget(editor, 1)
        footer_label = QtWidgets.QLabel(footer)
        footer_label.setObjectName("footer")
        footer_label.setWordWrap(True)
        section_layout.addWidget(footer_label)
        root.addWidget(section, 1)


def _process_events(app: QtWidgets.QApplication, duration: float = 0.05) -> None:
    deadline = time.monotonic() + duration
    while time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.005)


def _configure_runtime_dirs(temp_root: Path) -> None:
    home_dir = temp_root / "home"
    home_dir.mkdir(parents=True, exist_ok=True)

    os.environ["HOME"] = str(home_dir)
    os.environ["USERPROFILE"] = str(home_dir)
    os.environ["APPDATA"] = str(home_dir / "AppData" / "Roaming")
    os.environ["LOCALAPPDATA"] = str(home_dir / "AppData" / "Local")
    os.environ["XDG_CONFIG_HOME"] = str(home_dir / ".config")
    os.environ["XDG_DATA_HOME"] = str(home_dir / ".local" / "share")

    settings_root = temp_root / "qsettings"
    settings_root.mkdir(parents=True, exist_ok=True)
    QtCore.QSettings.setDefaultFormat(QtCore.QSettings.IniFormat)
    QtCore.QSettings.setPath(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope, str(settings_root))
    QtCore.QSettings.setPath(QtCore.QSettings.IniFormat, QtCore.QSettings.SystemScope, str(settings_root))
    QtCore.QStandardPaths.setTestModeEnabled(True)

    import core.settings_manager as settings_module

    settings_module._settings_instance = None


def _create_demo_pdf(target: Path, title: str, paragraphs: list[str]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    document = fitz.open()
    page = document.new_page(width=595, height=842)
    y = 72
    page.insert_text((72, y), title, fontsize=20, fontname="helv")
    y += 36
    for paragraph in paragraphs:
        page.insert_textbox(fitz.Rect(72, y, 523, y + 120), paragraph, fontsize=12, fontname="helv", lineheight=1.35)
        y += 110
    document.save(target)
    document.close()


def _build_demo_project(workspace: Path) -> DemoContext:
    project_manager = ProjectManager()
    project = project_manager.create_project(
        path=workspace / "Überblick Studie",
        name="Überblick Studie",
        description="Store-Screenshot-Demo mit lokalen Literaturdaten.",
        citation_style="apa",
    )
    source_manager = SourceManager(project.path, project.config.sources_folder)

    pdf_path = workspace / "artikel-mobilitaet.pdf"
    _create_demo_pdf(
        pdf_path,
        "Ärztliche Übersicht zur Mobilität",
        [
            "Lokale Literaturarbeit braucht klare Zitate, Notizen und Aufgaben mit echten Umlauten.",
            "Dieser Demo-Text zeigt LitZen mit PDF-Vorschau, BibTeX-Export und Companion-Bundle.",
            "Wissenschaftliche Workflows bleiben lokal, ohne Cloud-Zwang und ohne öffentliche Uploads.",
        ],
    )

    primary_meta = LiMeta(
        title="Ärztliche Übersicht zur Mobilität",
        authors=["Müller, Jörg", "Öztürk, Selin"],
        year=2026,
        journal="Journal für Reproduzierbarkeit",
        pages="12-18",
        abstract="Kurze Übersicht mit echten Umlauten und lokalem PDF-Workflow.",
        tags=["review", "mobilität", "lokal"],
        source_type="article",
        verified=True,
        doi="10.1234/litzentrum.demo",
    )
    primary_source = source_manager.create_source(primary_meta, pdf_path)

    notes = LiNote()
    notes.add("Notiz zur Quellenanzeige mit Überblick über lokale Exportpfade.", page=2, tags=["prüfung"])
    notes.notes[0].updated_at = notes.notes[0].created_at
    source_manager.save_notes(primary_source, notes)

    quotes = LiQuote()
    quotes.add(
        "Direktes Zitat mit Umlaut äöü zur lokalen Literaturarbeit.",
        page=3,
        quote_type="direct",
        comment="Relevante Passage für Store-Screenshot und BibTeX-Kontext.",
        tags=["zitat", "store"],
    )
    quotes.quotes[0].page_end = 4
    source_manager.save_quotes(primary_source, quotes)

    tasks = LiTask()
    tasks.add(
        "BibTeX-Export vor Abgabe prüfen",
        description="APA-Stil, DOI und Seitenangaben vor dem finalen Export validieren.",
        priority="high",
        due_date="2026-06-20",
        page=4,
        tags=["export", "abgabe"],
    )
    source_manager.save_tasks(primary_source, tasks)

    summaries = LiSum()
    summaries.add(
        "Kurzüberblick",
        "Zusammenfassung mit Größe, Überblick und lokaler Companion-Strategie.",
        summary_type="full",
        source="manual",
        pages="1-4",
        tags=["summary", "mobil"],
    )
    summaries.summaries[0].updated_at = summaries.summaries[0].created_at
    source_manager.save_summaries(primary_source, summaries)

    secondary_meta = LiMeta(
        title="Lokale Zitationssysteme ohne Cloud-Silo",
        authors=["Schäfer, Anne"],
        year=2025,
        journal="Offline Research Notes",
        pages="44-52",
        abstract="Vergleich lokaler Literaturverwaltungen mit Fokus auf Datenschutz.",
        tags=["privacy", "workflow"],
        source_type="other",
        verified=True,
    )
    secondary_source = source_manager.create_source(secondary_meta)

    secondary_notes = LiNote()
    secondary_notes.add("Kurznotiz zum Datenschutzvergleich und zu Exportverträgen.", page=1, tags=["privacy"])
    secondary_notes.notes[0].updated_at = secondary_notes.notes[0].created_at
    source_manager.save_notes(secondary_source, secondary_notes)

    project_tasks = LiTask()
    project_tasks.add(
        "Companion-Export gegen Mobil-Smoke halten",
        description="Import, Suche und Zitierkopie auf Android/iOS testen.",
        priority="urgent",
        due_date="2026-06-18",
        tags=["pwa", "smoke"],
    )
    project_tasks.add(
        "Store-Screenshots mit Demo-Daten nachziehen",
        description="Anonymisierte Projekt- und Quelldaten für den Windows Store nutzen.",
        priority="high",
        tags=["store"],
    )
    project_manager.save_project_tasks(project_tasks, project)

    exporter = LibraryExporter(project_manager, source_manager)
    export_dir = workspace / "exports"
    bibtex_path = export_dir / "literatur.bib"
    BibTeXGenerator().save_bibliography([source.meta for source in source_manager.get_all_sources()], bibtex_path)
    bundle_path = exporter.export_project(project, export_dir / "litzentrum-library-v1.json")
    bundle_data = json.loads(bundle_path.read_text(encoding="utf-8"))

    return DemoContext(
        project_manager=project_manager,
        source_manager=source_manager,
        project_path=project.path,
        primary_title=primary_source.meta.title,
        bibtex_path=bibtex_path,
        bundle_path=bundle_path,
        bundle_data=bundle_data,
    )


def _save_widget(widget: QtWidgets.QWidget, target: Path) -> None:
    widget.show()
    widget.raise_()
    widget.activateWindow()
    app = QtWidgets.QApplication.instance()
    if app is not None:
        _process_events(app, 0.12)
    pixmap = widget.grab()
    if pixmap.isNull():
        raise RuntimeError(f"Screenshot für {target.name} konnte nicht erzeugt werden")
    target.parent.mkdir(parents=True, exist_ok=True)
    if not pixmap.save(str(target)):
        raise RuntimeError(f"Screenshot {target} konnte nicht gespeichert werden")


def _highlight_primary_source(window: MainWindow, title: str) -> None:
    for index in range(window.source_list.list_widget.count()):
        item = window.source_list.list_widget.item(index)
        source = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if source and source.meta.title == title:
            window.source_list.list_widget.setCurrentItem(item)
            window._on_source_selected(source)
            break

    root = window.project_tree.tree.topLevelItem(0)
    if root is not None and root.childCount() > 0:
        sources_root = root.child(0)
        if sources_root is not None and sources_root.childCount() > 0:
            window.project_tree.tree.setCurrentItem(sources_root.child(0))


def _build_bibtex_preview(context: DemoContext) -> StorePreviewWidget:
    cards = [
        ("Quellen", str(len(context.source_manager.get_all_sources()))),
        ("Stil", context.project_manager.current_project.config.citation_style.upper() if context.project_manager.current_project else "APA"),
        ("Export", context.bibtex_path.name),
        ("Projekt", context.project_path.name),
    ]
    return StorePreviewWidget(
        title="LitZen - BibTeX-Export",
        subtitle="Reproduzierbarer Export aus lokalen Projektordnern mit echten Zitationsdaten und ohne Cloud-Abhängigkeit.",
        cards=cards,
        section_title="Exportvorschau",
        body_text=context.bibtex_path.read_text(encoding="utf-8"),
        footer="Der BibTeX-Export bleibt lokal im Projektordner und ist für wissenschaftliche Schreibworkflows gedacht.",
    )


def _build_companion_preview(context: DemoContext) -> StorePreviewWidget:
    project = context.bundle_data["projects"][0]
    compact = {
        "schema": context.bundle_data["schema"],
        "schema_version": context.bundle_data["schema_version"],
        "project": project["name"],
        "source_titles": [source["metadata"]["title"] for source in project["sources"]],
        "project_tasks": [task["title"] for task in project["project_tasks"]],
    }
    cards = [
        ("Bundle", context.bundle_path.name),
        ("Quellen", str(len(project["sources"]))),
        ("Projekt-Tasks", str(len(project["project_tasks"]))),
        ("PDF-Inhalte", "nein"),
    ]
    return StorePreviewWidget(
        title="LitZen - Companion-Export",
        subtitle="Read-only Exportbündel für Web/PWA-Nutzung auf mobilen Geräten mit anonymisierten, lokalen Forschungsdaten.",
        cards=cards,
        section_title="Exportvertrag `litzentrum-library-v1.json`",
        body_text=json.dumps(compact, ensure_ascii=False, indent=2),
        footer="Der Companion-Export liefert Metadaten, Notizen, Zitate, Aufgaben und BibTeX, aber keine eingebetteten PDFs.",
    )


def _write_summary(output_dir: Path, targets: list[Path]) -> None:
    summary = {
        "generated_at": QtCore.QDateTime.currentDateTimeUtc().toString(QtCore.Qt.DateFormat.ISODate),
        "files": [{"name": target.name, "path": str(target.resolve())} for target in targets],
    }
    (output_dir / SUMMARY_FILE).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def generate_store_screenshots(output_dir: Path) -> list[Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="litzentrum-store-shots-") as temp_dir:
        temp_root = Path(temp_dir)
        _configure_runtime_dirs(temp_root)
        context = _build_demo_project(temp_root)

        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        app.setApplicationName("LitZentrum")
        app.setOrganizationName("LitZentrum")
        app.setApplicationVersion("1.0.0")
        app.setStyle("Fusion")

        window = MainWindow()
        window.resize(1520, 920)
        targets = [
            output_dir / SCREENSHOT_FILES["main"],
            output_dir / SCREENSHOT_FILES["quotes"],
            output_dir / SCREENSHOT_FILES["bibtex"],
            output_dir / SCREENSHOT_FILES["companion"],
        ]

        try:
            window._load_project(context.project_path)
            _highlight_primary_source(window, context.primary_title)
            window.source_list.search_input.setText("Müller")
            _process_events(app, 0.12)
            window.detail_panel.tabs.setCurrentWidget(window.detail_panel.pdf_tab)
            window.statusBar().showMessage("Lokales Literaturprojekt mit PDF-Vorschau geöffnet", 0)
            _save_widget(window, targets[0])

            window.source_list.search_input.clear()
            window.detail_panel.tabs.setCurrentWidget(window.detail_panel.quotes_tab)
            window.detail_panel.quotes_tab.type_filter.setCurrentText("Direkt")
            if window.detail_panel.quotes_tab.list_widget.count() > 0:
                window.detail_panel.quotes_tab.list_widget.setCurrentRow(0)
            window.statusBar().showMessage("Zitierworkflow mit Seitenbezug und Kommentar", 0)
            _save_widget(window, targets[1])
        finally:
            window.detail_panel.pdf_tab.pdf_viewer.close_pdf()
            window.close()
            window.deleteLater()
            _process_events(app, 0.05)

        bibtex_preview = _build_bibtex_preview(context)
        try:
            _save_widget(bibtex_preview, targets[2])
        finally:
            bibtex_preview.close()
            _process_events(app, 0.05)

        companion_preview = _build_companion_preview(context)
        try:
            _save_widget(companion_preview, targets[3])
        finally:
            companion_preview.close()
            _process_events(app, 0.05)

        _write_summary(output_dir, targets)

    return targets


def main() -> None:
    targets = generate_store_screenshots(PROJECT_ROOT / "README" / "screenshots" / "store")
    for target in targets:
        print(target.name)


if __name__ == "__main__":
    main()
