"""
LitZentrum - Quellenliste Panel
Zeigt alle Quellen mit Filterung
"""
from typing import List, Optional

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QLineEdit, QComboBox, QPushButton
)

from core import LitSource


class SourceListPanel(QWidget):
    """Panel mit Quellenliste"""
    
    source_selected = Signal(object)  # LitSource
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sources: List[LitSource] = []
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header
        header = QLabel("📑 Quellen")
        header.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(header)
        
        # Suchleiste
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Suchen...")
        self.search_input.textChanged.connect(self._on_search)
        search_layout.addWidget(self.search_input)
        
        layout.addLayout(search_layout)
        
        # Filter
        filter_layout = QHBoxLayout()
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Nach Autor", "Nach Jahr", "Nach Titel", "Nach Datum"])
        self.sort_combo.currentIndexChanged.connect(self._on_sort_changed)
        filter_layout.addWidget(self.sort_combo)
        
        self.tag_combo = QComboBox()
        self.tag_combo.addItem("Alle Tags")
        self.tag_combo.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.tag_combo)
        
        layout.addLayout(filter_layout)
        
        # Liste
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.list_widget)
        
        # Statuszeile
        self.status_label = QLabel("0 Quellen")
        self.status_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(self.status_label)
    
    def set_sources(self, sources: List[LitSource]):
        """Setzt die Quellenliste"""
        self.sources = sources
        self._update_tags()
        self._refresh_list()
    
    def _update_tags(self):
        """Aktualisiert Tag-Filter"""
        tags = set()
        for source in self.sources:
            tags.update(source.meta.tags)
        
        self.tag_combo.clear()
        self.tag_combo.addItem("Alle Tags")
        for tag in sorted(tags):
            self.tag_combo.addItem(tag)
    
    def _refresh_list(self):
        """Aktualisiert die Listendarstellung"""
        self.list_widget.clear()
        
        # Filter anwenden
        search_text = self.search_input.text().lower()
        selected_tag = self.tag_combo.currentText()
        
        filtered = []
        for source in self.sources:
            # Textfilter
            if search_text:
                searchable = (
                    source.meta.title.lower() +
                    " ".join(source.meta.authors).lower() +
                    " ".join(source.meta.tags).lower()
                )
                if search_text not in searchable:
                    continue
            
            # Tag-Filter
            if selected_tag != "Alle Tags":
                if selected_tag not in source.meta.tags:
                    continue
            
            filtered.append(source)
        
        # Sortieren
        sort_index = self.sort_combo.currentIndex()
        if sort_index == 0:  # Nach Autor
            filtered.sort(key=lambda s: s.meta.first_author.lower())
        elif sort_index == 1:  # Nach Jahr
            filtered.sort(key=lambda s: s.meta.year or 0, reverse=True)
        elif sort_index == 2:  # Nach Titel
            filtered.sort(key=lambda s: s.meta.title.lower())
        elif sort_index == 3:  # Nach Datum
            filtered.sort(key=lambda s: s.meta.created_at, reverse=True)
        
        # Liste füllen
        for source in filtered:
            item = self._create_list_item(source)
            self.list_widget.addItem(item)
        
        self.status_label.setText(f"{len(filtered)} von {len(self.sources)} Quellen")
    
    def _create_list_item(self, source: LitSource) -> QListWidgetItem:
        """Erstellt ein Listenelement"""
        meta = source.meta
        
        # Icon
        icon = "📄" if source.has_pdf else "📝"
        verified = "✓" if meta.verified else ""
        
        # Text
        authors = meta.first_author
        if len(meta.authors) > 1:
            authors += " et al."
        year = f"({meta.year})" if meta.year else ""
        
        text = f"{icon} {authors} {year} {verified}\n   {meta.title[:60]}{'...' if len(meta.title) > 60 else ''}"
        
        item = QListWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, source)
        item.setToolTip(f"{meta.title}\n\nTags: {', '.join(meta.tags)}")
        
        return item
    
    def _on_item_clicked(self, item: QListWidgetItem):
        """Item wurde angeklickt"""
        source = item.data(Qt.ItemDataRole.UserRole)
        if source:
            self.source_selected.emit(source)
    
    def _on_item_double_clicked(self, item: QListWidgetItem):
        """Item wurde doppelt angeklickt"""
        source = item.data(Qt.ItemDataRole.UserRole)
        if source and source.has_pdf:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(source.pdf_path)))
    
    def _on_search(self, text: str):
        """Suche geändert"""
        self._refresh_list()
    
    def _on_sort_changed(self, index: int):
        """Sortierung geändert"""
        self._refresh_list()
    
    def _on_filter_changed(self, index: int):
        """Filter geändert"""
        self._refresh_list()
    
    def clear(self):
        """Leert die Liste"""
        self.sources = []
        self.list_widget.clear()
        self.tag_combo.clear()
        self.tag_combo.addItem("Alle Tags")
        self.status_label.setText("0 Quellen")
