"""
LitZentrum - Zitate Tab
"""
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QTextEdit, QSpinBox, QLabel, QDialog, QDialogButtonBox,
    QLineEdit, QComboBox, QCheckBox, QApplication, QSplitter
)

from core import LitSource, SourceManager
from formats import LiQuote, Quote
from ..widgets.latex_preview import LatexPreviewWidget, contains_latex


class QuotesTab(QWidget):
    """Tab für Zitate"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.quotes: Optional[LiQuote] = None
        self.source: Optional[LitSource] = None
        self.source_manager: Optional[SourceManager] = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        add_btn = QPushButton("➕ Neues Zitat")
        add_btn.clicked.connect(self._add_quote)
        toolbar.addWidget(add_btn)

        self.cite_btn = QPushButton("📋 \\cite{} kopieren")
        self.cite_btn.setToolTip("BibTeX-Zitierbefehl in die Zwischenablage kopieren")
        self.cite_btn.clicked.connect(self._copy_cite_to_clipboard)
        self.cite_btn.setEnabled(False)
        toolbar.addWidget(self.cite_btn)

        toolbar.addStretch()
        
        # Filter
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Alle", "Direkt", "Indirekt", "Paraphrase"])
        self.type_filter.currentIndexChanged.connect(self._refresh)
        toolbar.addWidget(self.type_filter)
        
        self.count_label = QLabel("0 Zitate")
        toolbar.addWidget(self.count_label)
        
        layout.addLayout(toolbar)
        
        # Liste
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.itemDoubleClicked.connect(self._edit_quote)
        layout.addWidget(self.list_widget)
    
    def set_data(self, quotes: LiQuote, source: LitSource, manager: SourceManager):
        """Setzt die Daten"""
        self.quotes = quotes
        self.source = source
        self.source_manager = manager
        self.cite_btn.setEnabled(True)
        self._refresh()
    
    def _refresh(self):
        """Aktualisiert die Anzeige"""
        self.list_widget.clear()
        
        if not self.quotes:
            self.count_label.setText("0 Zitate")
            return
        
        # Filter
        filter_type = self.type_filter.currentText()
        type_map = {"Direkt": "direct", "Indirekt": "indirect", "Paraphrase": "paraphrase"}
        
        filtered = self.quotes.quotes
        if filter_type in type_map:
            filtered = [q for q in filtered if q.type == type_map[filter_type]]
        
        for quote in filtered:
            # Icon nach Typ
            icons = {"direct": "📌", "indirect": "📎", "paraphrase": "📝"}
            icon = icons.get(quote.type, "💬")
            
            page_str = f"[S. {quote.page_range}] " if quote.page else ""
            preview = quote.text[:80].replace("\n", " ")
            if len(quote.text) > 80:
                preview += "..."
            
            text = f'{icon} {page_str}"{preview}"'
            
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, quote)
            item.setToolTip(f"{quote.text}\n\nKommentar: {quote.comment or '-'}")
            self.list_widget.addItem(item)
        
        self.count_label.setText(f"{len(filtered)} von {len(self.quotes)} Zitaten")
    
    def _add_quote(self):
        """Neues Zitat hinzufügen"""
        if not self.quotes or not self.source_manager:
            return
        
        dialog = QuoteDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            self.quotes.add(
                text=data["text"],
                page=data["page"],
                quote_type=data["type"],
                comment=data["comment"],
                tags=data["tags"]
            )
            self.source_manager.save_quotes(self.source, self.quotes)
            self._refresh()
    
    def _edit_quote(self, item: QListWidgetItem):
        """Zitat bearbeiten"""
        quote = item.data(Qt.ItemDataRole.UserRole)
        if not quote:
            return
        
        dialog = QuoteDialog(self, quote)
        if dialog.exec():
            data = dialog.get_data()
            quote.text = data["text"]
            quote.type = data["type"]
            quote.page = data["page"]
            quote.page_end = data["page_end"]
            quote.comment = data["comment"]
            quote.tags = data["tags"]
            self.source_manager.save_quotes(self.source, self.quotes)
            self._refresh()
    
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

    def clear(self):
        """Leert die Anzeige"""
        self.quotes = None
        self.source = None
        self.list_widget.clear()
        self.cite_btn.setEnabled(False)
        self.count_label.setText("0 Zitate")


class QuoteDialog(QDialog):
    """Dialog zum Erstellen/Bearbeiten eines Zitats"""
    
    def __init__(self, parent=None, quote: Quote = None):
        super().__init__(parent)
        self.quote = quote
        self.setWindowTitle("Zitat bearbeiten" if quote else "Neues Zitat")
        self.setMinimumSize(600, 500)
        self._setup_ui()
        
        if quote:
            self._load_quote()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Typ
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Typ:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Direktes Zitat", "Indirektes Zitat", "Paraphrase"])
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()
        layout.addLayout(type_layout)
        
        # Seite
        page_layout = QHBoxLayout()
        page_layout.addWidget(QLabel("Seite:"))
        self.page_spin = QSpinBox()
        self.page_spin.setRange(0, 9999)
        self.page_spin.setSpecialValueText("Keine")
        page_layout.addWidget(self.page_spin)
        
        page_layout.addWidget(QLabel("bis:"))
        self.page_end_spin = QSpinBox()
        self.page_end_spin.setRange(0, 9999)
        self.page_end_spin.setSpecialValueText("-")
        page_layout.addWidget(self.page_end_spin)
        page_layout.addStretch()
        layout.addLayout(page_layout)
        
        # Zitat-Text mit LaTeX-Preview
        layout.addWidget(QLabel("Zitat (LaTeX-Formeln mit $..$ oder $$..$$):"))

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Zitat eingeben... LaTeX-Formeln werden automatisch gerendert.")

        # LaTeX-Preview
        self._latex_preview = LatexPreviewWidget()
        self._latex_preview.setVisible(False)

        self._preview_label = QLabel("Formel-Vorschau:")
        self._preview_label.setStyleSheet("color: #555; font-size: 11px; margin-top: 4px;")
        self._preview_label.setVisible(False)

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.text_edit)

        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.addWidget(self._preview_label)
        preview_layout.addWidget(self._latex_preview)
        splitter.addWidget(preview_container)

        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)

        # Live-Preview bei Textaenderung
        self.text_edit.textChanged.connect(self._on_text_changed)

        # Kommentar
        layout.addWidget(QLabel("Kommentar:"))
        self.comment_edit = QTextEdit()
        self.comment_edit.setMaximumHeight(80)
        self.comment_edit.setPlaceholderText("Eigener Kommentar zum Zitat...")
        layout.addWidget(self.comment_edit)
        
        # Tags
        tags_layout = QHBoxLayout()
        tags_layout.addWidget(QLabel("Tags:"))
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("tag1, tag2, tag3")
        tags_layout.addWidget(self.tags_input)
        layout.addLayout(tags_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _on_text_changed(self):
        """Aktualisiert LaTeX-Preview bei Textaenderung."""
        text = self.text_edit.toPlainText()
        has_latex = contains_latex(text)

        self._preview_label.setVisible(has_latex)
        self._latex_preview.setVisible(has_latex)

        if has_latex:
            self._latex_preview.update_content(text)

    def _load_quote(self):
        """Laedt bestehendes Zitat"""
        if self.quote:
            self.text_edit.setText(self.quote.text)

            type_map = {"direct": 0, "indirect": 1, "paraphrase": 2}
            self.type_combo.setCurrentIndex(type_map.get(self.quote.type, 0))

            self.page_spin.setValue(self.quote.page or 0)
            self.page_end_spin.setValue(self.quote.page_end or 0)
            self.comment_edit.setText(self.quote.comment or "")
            self.tags_input.setText(", ".join(self.quote.tags))
            # Trigger LaTeX-Preview fuer bestehende Zitate
            self._on_text_changed()
    
    def get_data(self) -> dict:
        """Gibt die Eingabedaten zurück"""
        type_map = {0: "direct", 1: "indirect", 2: "paraphrase"}
        tags_text = self.tags_input.text()
        
        return {
            "text": self.text_edit.toPlainText(),
            "type": type_map[self.type_combo.currentIndex()],
            "page": self.page_spin.value() if self.page_spin.value() > 0 else None,
            "page_end": self.page_end_spin.value() if self.page_end_spin.value() > 0 else None,
            "comment": self.comment_edit.toPlainText() or None,
            "tags": [t.strip() for t in tags_text.split(",") if t.strip()]
        }
