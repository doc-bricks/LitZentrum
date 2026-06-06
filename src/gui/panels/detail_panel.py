"""
LitZentrum - Detail Panel
Zeigt Details zur ausgewählten Quelle mit Tabs
"""
from typing import Optional

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QScrollArea, QFrame, QPushButton, QTextEdit,
    QApplication
)

from core import LitSource, SourceManager
from formats import LiMeta
from ..tabs.notes_tab import NotesTab
from ..tabs.quotes_tab import QuotesTab
from ..tabs.tasks_tab import TasksTab
from ..tabs.summaries_tab import SummariesTab
from ..tabs.pdf_tab import PDFTab


class DetailPanel(QWidget):
    """Panel mit Quellen-Details"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.source: Optional[LitSource] = None
        self.source_manager: Optional[SourceManager] = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header mit Metadaten
        self.header_frame = QFrame()
        self.header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_layout = QVBoxLayout(self.header_frame)
        
        self.title_label = QLabel("Keine Quelle ausgewählt")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.title_label.setWordWrap(True)
        header_layout.addWidget(self.title_label)
        
        self.authors_label = QLabel("")
        self.authors_label.setStyleSheet("color: #555;")
        header_layout.addWidget(self.authors_label)
        
        self.meta_label = QLabel("")
        self.meta_label.setStyleSheet("color: #777; font-size: 11px;")
        self.meta_label.setWordWrap(True)
        header_layout.addWidget(self.meta_label)
        
        # Tags
        self.tags_label = QLabel("")
        self.tags_label.setStyleSheet("color: #0066cc; font-size: 10px;")
        header_layout.addWidget(self.tags_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.pdf_btn = QPushButton("📄 PDF extern öffnen")
        self.pdf_btn.clicked.connect(self._open_pdf_external)
        self.pdf_btn.setEnabled(False)
        btn_layout.addWidget(self.pdf_btn)
        
        self.edit_btn = QPushButton("✏️ Bearbeiten")
        self.edit_btn.clicked.connect(self._edit_source)
        self.edit_btn.setEnabled(False)
        btn_layout.addWidget(self.edit_btn)

        self.cite_btn = QPushButton("📋 Als \\cite{} kopieren")
        self.cite_btn.setToolTip("BibTeX-Zitierbefehl in die Zwischenablage kopieren")
        self.cite_btn.clicked.connect(self._copy_cite_to_clipboard)
        self.cite_btn.setEnabled(False)
        btn_layout.addWidget(self.cite_btn)

        btn_layout.addStretch()
        header_layout.addLayout(btn_layout)
        
        layout.addWidget(self.header_frame)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # PDF-Tab als erstes (wenn vorhanden)
        self.pdf_tab = PDFTab()
        self.pdf_tab.quote_requested.connect(self._on_quote_requested)
        self.pdf_tab.note_requested.connect(self._on_note_requested)
        self.tabs.addTab(self.pdf_tab, "📄 PDF")
        
        self.notes_tab = NotesTab()
        self.tabs.addTab(self.notes_tab, "📝 Notizen")
        
        self.quotes_tab = QuotesTab()
        self.tabs.addTab(self.quotes_tab, "💬 Zitate")
        
        self.tasks_tab = TasksTab()
        self.tabs.addTab(self.tasks_tab, "✅ Aufgaben")
        
        self.summaries_tab = SummariesTab()
        self.tabs.addTab(self.summaries_tab, "📋 Zusammenfassungen")
        
        layout.addWidget(self.tabs)
    
    def set_source(self, source: LitSource, source_manager: SourceManager):
        """Setzt die anzuzeigende Quelle"""
        self.source = source
        self.source_manager = source_manager
        self._update_display()
    
    def _update_display(self):
        """Aktualisiert die Anzeige"""
        if not self.source:
            self.clear()
            return
        
        meta = self.source.meta
        
        # Header
        self.title_label.setText(meta.title)
        
        # Autoren
        authors = ", ".join(meta.authors) if meta.authors else "Unbekannt"
        self.authors_label.setText(authors)
        
        # Meta-Info
        parts = []
        if meta.year:
            parts.append(str(meta.year))
        if meta.publisher:
            parts.append(meta.publisher)
        if meta.journal:
            parts.append(f"in: {meta.journal}")
        if meta.doi:
            parts.append(f"DOI: {meta.doi}")
        if meta.isbn:
            parts.append(f"ISBN: {meta.isbn}")
        self.meta_label.setText(" | ".join(parts))
        
        # Tags
        if meta.tags:
            tags_text = " ".join([f"#{tag}" for tag in meta.tags])
            self.tags_label.setText(tags_text)
        else:
            self.tags_label.setText("")
        
        # Buttons
        self.pdf_btn.setEnabled(self.source.has_pdf)
        self.edit_btn.setEnabled(True)
        self.cite_btn.setEnabled(True)
        
        # Tabs laden
        self._load_tabs()
        
        # PDF-Tab aktivieren wenn PDF vorhanden
        if self.source.has_pdf:
            self.tabs.setCurrentWidget(self.pdf_tab)
    
    def _load_tabs(self):
        """Lädt die Tab-Inhalte"""
        if not self.source or not self.source_manager:
            return
        
        # PDF
        self.pdf_tab.set_data(self.source, self.source_manager)
        
        # Notizen
        notes = self.source_manager.get_notes(self.source)
        self.notes_tab.set_data(notes, self.source, self.source_manager)
        
        # Zitate
        quotes = self.source_manager.get_quotes(self.source)
        self.quotes_tab.set_data(quotes, self.source, self.source_manager)
        
        # Aufgaben
        tasks = self.source_manager.get_tasks(self.source)
        self.tasks_tab.set_data(tasks, self.source, self.source_manager)
        
        # Zusammenfassungen
        summaries = self.source_manager.get_summaries(self.source)
        self.summaries_tab.set_data(summaries, self.source, self.source_manager)
    
    def refresh(self):
        """Aktualisiert die Anzeige"""
        self._load_tabs()
    
    def clear(self):
        """Leert die Anzeige"""
        self.source = None
        self.source_manager = None
        
        self.title_label.setText("Keine Quelle ausgewählt")
        self.authors_label.setText("")
        self.meta_label.setText("")
        self.tags_label.setText("")
        
        self.pdf_btn.setEnabled(False)
        self.edit_btn.setEnabled(False)
        self.cite_btn.setEnabled(False)

        self.pdf_tab.clear()
        self.notes_tab.clear()
        self.quotes_tab.clear()
        self.tasks_tab.clear()
        self.summaries_tab.clear()
    
    def _open_pdf_external(self):
        """Öffnet die PDF extern"""
        if self.source and self.source.has_pdf:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.source.pdf_path)))
    
    def _copy_cite_to_clipboard(self):
        """Kopiert \\cite{bibtex_key} in die Zwischenablage"""
        if not self.source:
            return
        key = self.source.meta.bibtex_key
        cite_cmd = f"\\cite{{{key}}}"
        clipboard = QApplication.clipboard()
        clipboard.setText(cite_cmd)
        # Statusmeldung ueber das Hauptfenster
        window = self.window()
        if hasattr(window, "statusBar"):
            window.statusBar().showMessage(
                f"Kopiert: {cite_cmd}", 3000
            )

    def _edit_source(self):
        """Bearbeitet die Quelle"""
        if not self.source:
            return
        
        from ..dialogs.source_dialog import SourceDialog
        dialog = SourceDialog(self, self.source.meta)
        if dialog.exec():
            new_meta = dialog.get_meta()
            new_meta.created_at = self.source.meta.created_at
            new_meta.update()
            new_meta.save(self.source.path / "meta.limeta")
            self.source.meta = new_meta
            self._update_display()
    
    def _on_quote_requested(self, text: str, page: int):
        """Zitat angefordert vom PDF-Tab"""
        # Wechsle zu Zitate-Tab und öffne Dialog
        self.tabs.setCurrentWidget(self.quotes_tab)
        # Feature geplant: Zitat-Dialog mit vorausgefülltem Text und Seite automatisch öffnen
        # Aktuell: Manuelles Hinzufügen über Tab-Interface
    
    def _on_note_requested(self, text: str, page: int):
        """Notiz angefordert vom PDF-Tab"""
        # Wechsle zu Notizen-Tab und öffne Dialog
        self.tabs.setCurrentWidget(self.notes_tab)
        # Feature geplant: Notiz-Dialog mit vorausgefülltem Text und Seite automatisch öffnen
        # Aktuell: Manuelles Hinzufügen über Tab-Interface
