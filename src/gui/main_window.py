"""
LitZentrum - Hauptfenster
3-Panel Layout: Projektbaum | Quellenliste | Detailansicht
"""
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QMenuBar, QMenu, QToolBar, QStatusBar,
    QFileDialog, QMessageBox, QLabel
)

from core import (
    ProjectManager, SourceManager, LitProject, LitSource, LibraryExporter,
    EventBus, EventType, get_event_bus, get_settings
)
from .panels.project_tree import ProjectTreePanel
from .panels.source_list import SourceListPanel
from .panels.detail_panel import DetailPanel


class MainWindow(QMainWindow):
    """LitZentrum Hauptfenster"""
    
    def __init__(self):
        super().__init__()
        
        self.project_manager = ProjectManager()
        self.source_manager: Optional[SourceManager] = None
        self.current_source: Optional[LitSource] = None
        
        self.event_bus = get_event_bus()
        self.settings = get_settings()
        
        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_statusbar()
        self._connect_signals()
        self._restore_state()
        
        # Letztes Projekt öffnen
        self._open_last_project()
    
    def _setup_ui(self):
        """Initialisiert die UI"""
        self.setWindowTitle("LitZentrum - Literaturverwaltung")
        self.setMinimumSize(1200, 800)
        
        # Central Widget
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Haupt-Splitter (3 Panels)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel 1: Projektbaum
        self.project_tree = ProjectTreePanel()
        self.main_splitter.addWidget(self.project_tree)
        
        # Panel 2: Quellenliste
        self.source_list = SourceListPanel()
        self.main_splitter.addWidget(self.source_list)
        
        # Panel 3: Detailansicht
        self.detail_panel = DetailPanel()
        self.main_splitter.addWidget(self.detail_panel)
        
        # Splitter-Größen
        sizes = self.settings.get("splitter_sizes", [200, 300, 500])
        self.main_splitter.setSizes(sizes)
        
        layout.addWidget(self.main_splitter)
    
    def _setup_menu(self):
        """Erstellt das Menü"""
        menubar = self.menuBar()
        
        # Datei-Menü
        file_menu = menubar.addMenu("&Datei")
        
        new_project = QAction("&Neues Projekt...", self)
        new_project.setShortcut(QKeySequence.StandardKey.New)
        new_project.triggered.connect(self._on_new_project)
        file_menu.addAction(new_project)
        
        open_project = QAction("Projekt &öffnen...", self)
        open_project.setShortcut(QKeySequence.StandardKey.Open)
        open_project.triggered.connect(self._on_open_project)
        file_menu.addAction(open_project)
        
        # Recent Projects Submenu
        self.recent_menu = file_menu.addMenu("Zuletzt geöffnet")
        self._update_recent_menu()
        
        file_menu.addSeparator()
        
        close_project = QAction("Projekt schließen", self)
        close_project.triggered.connect(self._on_close_project)
        file_menu.addAction(close_project)
        
        file_menu.addSeparator()
        
        quit_action = QAction("&Beenden", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Quellen-Menü
        source_menu = menubar.addMenu("&Quellen")
        
        add_source = QAction("Quelle &hinzufügen...", self)
        add_source.setShortcut("Ctrl+Shift+N")
        add_source.triggered.connect(self._on_add_source)
        source_menu.addAction(add_source)
        
        import_pdf = QAction("PDF &importieren...", self)
        import_pdf.setShortcut("Ctrl+I")
        import_pdf.triggered.connect(self._on_import_pdf)
        source_menu.addAction(import_pdf)
        
        source_menu.addSeparator()
        
        import_bibtex = QAction("BibTeX importieren...", self)
        import_bibtex.triggered.connect(self._on_import_bibtex)
        source_menu.addAction(import_bibtex)
        
        # Ansicht-Menü
        view_menu = menubar.addMenu("&Ansicht")
        
        refresh = QAction("&Aktualisieren", self)
        refresh.setShortcut(QKeySequence.StandardKey.Refresh)
        refresh.triggered.connect(self._on_refresh)
        view_menu.addAction(refresh)
        
        # Extras-Menü
        extras_menu = menubar.addMenu("&Extras")
        
        export_bib = QAction("Bibliografie &exportieren...", self)
        export_bib.triggered.connect(self._on_export_bibliography)
        extras_menu.addAction(export_bib)

        export_library = QAction("Bibliothek für &Companion exportieren...", self)
        export_library.triggered.connect(self._on_export_library)
        extras_menu.addAction(export_library)
        
        extras_menu.addSeparator()
        
        settings = QAction("&Einstellungen...", self)
        settings.setShortcut("Ctrl+,")
        settings.triggered.connect(self._on_settings)
        extras_menu.addAction(settings)
        
        # Hilfe-Menü
        help_menu = menubar.addMenu("&Hilfe")
        
        about = QAction("Über &LitZentrum", self)
        about.triggered.connect(self._on_about)
        help_menu.addAction(about)
    
    def _setup_toolbar(self):
        """Erstellt die Toolbar"""
        toolbar = QToolBar("Hauptwerkzeugleiste")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Neue Quelle
        add_source_btn = QAction("➕ Quelle", self)
        add_source_btn.setToolTip("Neue Quelle hinzufügen")
        add_source_btn.triggered.connect(self._on_add_source)
        toolbar.addAction(add_source_btn)
        
        # PDF importieren
        import_btn = QAction("📄 PDF", self)
        import_btn.setToolTip("PDF importieren")
        import_btn.triggered.connect(self._on_import_pdf)
        toolbar.addAction(import_btn)
        
        toolbar.addSeparator()
        
        # Aktualisieren
        refresh_btn = QAction("🔄", self)
        refresh_btn.setToolTip("Aktualisieren")
        refresh_btn.triggered.connect(self._on_refresh)
        toolbar.addAction(refresh_btn)
    
    def _setup_statusbar(self):
        """Erstellt die Statusleiste"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # Projekt-Label
        self.project_label = QLabel("Kein Projekt geöffnet")
        self.statusbar.addWidget(self.project_label)
        
        # Quellen-Zähler
        self.sources_label = QLabel("")
        self.statusbar.addPermanentWidget(self.sources_label)
    
    def _connect_signals(self):
        """Verbindet Signals"""
        # Panel-Signale
        self.project_tree.source_selected.connect(self._on_source_selected)
        self.source_list.source_selected.connect(self._on_source_selected)
        
        # EventBus
        self.event_bus.subscribe(EventType.SOURCE_CREATED, self._on_source_changed)
        self.event_bus.subscribe(EventType.SOURCE_DELETED, self._on_source_changed)
        self.event_bus.subscribe(EventType.STATUS_MESSAGE, self._show_status)
    
    def _restore_state(self):
        """Stellt Fensterposition wieder her"""
        geometry = self.settings.get("window_geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        state = self.settings.get("window_state")
        if state:
            self.restoreState(state)
    
    def _save_state(self):
        """Speichert Fensterposition"""
        self.settings.set("window_geometry", self.saveGeometry())
        self.settings.set("window_state", self.saveState())
        self.settings.set("splitter_sizes", self.main_splitter.sizes())
    
    def _open_last_project(self):
        """Öffnet das zuletzt geöffnete Projekt"""
        last = self.settings.get("last_project")
        if last and Path(last).exists():
            self._load_project(Path(last))
    
    def _load_project(self, path: Path):
        """Lädt ein Projekt"""
        try:
            project = self.project_manager.open_project(path)
            self.source_manager = SourceManager(
                project.path, 
                project.config.sources_folder
            )
            
            self.settings.add_recent_project(path)
            self._update_recent_menu()
            
            # UI aktualisieren
            self.project_tree.set_project(project)
            self._refresh_sources()
            
            self.project_label.setText(f"📚 {project.name}")
            self._show_status(f"Projekt geöffnet: {project.name}")
            
            self.event_bus.emit(EventType.PROJECT_OPENED, project)
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Projekt konnte nicht geöffnet werden:\n{e}")
    
    def _refresh_sources(self):
        """Aktualisiert die Quellenliste"""
        if not self.source_manager:
            return
        
        sources = self.source_manager.get_all_sources()
        self.source_list.set_sources(sources)
        self.sources_label.setText(f"{len(sources)} Quellen")
    
    def _update_recent_menu(self):
        """Aktualisiert das Recent-Menü"""
        self.recent_menu.clear()
        
        for path in self.settings.get_recent_projects():
            action = QAction(path.name, self)
            action.setData(path)
            action.triggered.connect(lambda checked, p=path: self._load_project(p))
            self.recent_menu.addAction(action)
        
        if self.recent_menu.isEmpty():
            self.recent_menu.addAction("(keine)").setEnabled(False)
    
    # --- Event Handler ---
    
    def _on_new_project(self):
        """Neues Projekt erstellen"""
        from .dialogs.new_project_dialog import NewProjectDialog
        dialog = NewProjectDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            project = self.project_manager.create_project(
                data["path"], data["name"], data["description"], data["style"]
            )
            self._load_project(project.path)
    
    def _on_open_project(self):
        """Projekt öffnen"""
        path = QFileDialog.getExistingDirectory(
            self, "Projekt öffnen", str(Path.home())
        )
        if path:
            self._load_project(Path(path))
    
    def _on_close_project(self):
        """Projekt schließen"""
        self.project_manager.close_project()
        self.source_manager = None
        self.current_source = None
        
        self.project_tree.clear()
        self.source_list.clear()
        self.detail_panel.clear()
        
        self.project_label.setText("Kein Projekt geöffnet")
        self.sources_label.setText("")
        
        self.event_bus.emit(EventType.PROJECT_CLOSED)
    
    def _on_add_source(self):
        """Neue Quelle hinzufügen"""
        if not self.source_manager:
            QMessageBox.warning(self, "Hinweis", "Bitte zuerst ein Projekt öffnen.")
            return
        
        from .dialogs.source_dialog import SourceDialog
        dialog = SourceDialog(self)
        if dialog.exec():
            meta = dialog.get_meta()
            pdf_path = dialog.get_pdf_path()
            source = self.source_manager.create_source(meta, pdf_path)
            self._refresh_sources()
            self.event_bus.emit(EventType.SOURCE_CREATED, source)
    
    def _on_import_pdf(self):
        """PDF importieren"""
        if not self.source_manager:
            QMessageBox.warning(self, "Hinweis", "Bitte zuerst ein Projekt öffnen.")
            return
        
        paths, _ = QFileDialog.getOpenFileNames(
            self, "PDF importieren", str(Path.home()),
            "PDF-Dateien (*.pdf)"
        )
        
        for pdf_path in paths:
            from formats import LiMeta
            # Einfache Metadaten aus Dateiname
            name = Path(pdf_path).stem
            meta = LiMeta(title=name)
            self.source_manager.create_source(meta, Path(pdf_path))
        
        if paths:
            self._refresh_sources()
            self._show_status(f"{len(paths)} PDF(s) importiert")
    
    def _on_import_bibtex(self):
        """BibTeX importieren"""
        self._show_status("BibTeX-Import noch nicht implementiert")
    
    def _on_export_bibliography(self):
        """Export bibliography as BibTeX (.bib) file."""
        if not self.source_manager:
            QMessageBox.warning(self, "Hinweis", "Bitte zuerst ein Projekt öffnen.")
            return

        sources = self.source_manager.get_all_sources()
        if not sources:
            QMessageBox.information(self, "Export", "Das Projekt enthält keine Quellen.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Bibliografie exportieren",
            str(Path.home() / "bibliography.bib"),
            "BibTeX-Dateien (*.bib);;Alle Dateien (*)",
        )
        if not path:
            return

        try:
            from modules.bibliography.bibtex import BibTeXGenerator
            generator = BibTeXGenerator()
            metas = [src.meta for src in sources]
            generator.save_bibliography(metas, Path(path))
            self._show_status(f"Bibliografie exportiert: {Path(path).name} ({len(metas)} Einträge)")
        except Exception as exc:
            QMessageBox.critical(self, "Export-Fehler", f"Export fehlgeschlagen:\n{exc}")

    def _on_export_library(self):
        """Export the current project as a portable read-only JSON bundle."""
        project = self.project_manager.current_project
        if not project or not self.source_manager:
            QMessageBox.warning(self, "Hinweis", "Bitte zuerst ein Projekt öffnen.")
            return

        default_name = f"{project.path.name}-library-v1.json"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Bibliothek exportieren",
            str(project.path / default_name),
            "JSON-Dateien (*.json);;Alle Dateien (*)",
        )
        if not path:
            return

        try:
            exporter = LibraryExporter(self.project_manager, self.source_manager)
            output_path = exporter.export_project(project, Path(path))
            source_count = len(self.source_manager.get_all_sources())
            self._show_status(
                f"Bibliothek exportiert: {output_path.name} ({source_count} Quellen)"
            )
        except Exception as exc:
            QMessageBox.critical(self, "Export-Fehler", f"Export fehlgeschlagen:\n{exc}")
    
    def _on_source_selected(self, source: LitSource):
        """Quelle wurde ausgewählt"""
        self.current_source = source
        self.detail_panel.set_source(source, self.source_manager)
        self.event_bus.emit(EventType.SOURCE_SELECTED, source)
    
    def _on_source_changed(self, data=None):
        """Quelle wurde geändert"""
        self._refresh_sources()
    
    def _on_refresh(self):
        """Ansicht aktualisieren"""
        self._refresh_sources()
        if self.current_source:
            self.detail_panel.refresh()
        self.event_bus.emit(EventType.REFRESH_VIEW)
    
    def _on_settings(self):
        """Einstellungen öffnen"""
        from .dialogs.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def _on_about(self):
        """Über-Dialog"""
        QMessageBox.about(
            self,
            "Über LitZentrum",
            "<h3>LitZentrum</h3>"
            "<p>Ordnerbasierte Literaturverwaltung</p>"
            "<p>Version 1.0.0</p>"
            "<p>© 2026</p>"
        )
    
    def _show_status(self, message: str):
        """Zeigt Statusmeldung"""
        self.statusbar.showMessage(message, 5000)
    
    def closeEvent(self, event):
        """Beim Schließen"""
        self._save_state()
        event.accept()
