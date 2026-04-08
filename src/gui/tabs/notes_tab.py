"""
LitZentrum - Notizen Tab
"""
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QTextEdit, QSpinBox, QLabel, QDialog, QDialogButtonBox,
    QLineEdit, QMessageBox, QSplitter
)

from core import LitSource, SourceManager
from formats import LiNote, Note
from ..widgets.latex_preview import LatexPreviewWidget, contains_latex


class NotesTab(QWidget):
    """Tab für Notizen"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notes: Optional[LiNote] = None
        self.source: Optional[LitSource] = None
        self.source_manager: Optional[SourceManager] = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        add_btn = QPushButton("➕ Neue Notiz")
        add_btn.clicked.connect(self._add_note)
        toolbar.addWidget(add_btn)
        
        toolbar.addStretch()
        
        self.count_label = QLabel("0 Notizen")
        toolbar.addWidget(self.count_label)
        
        layout.addLayout(toolbar)
        
        # Liste
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.itemDoubleClicked.connect(self._edit_note)
        layout.addWidget(self.list_widget)
    
    def set_data(self, notes: LiNote, source: LitSource, manager: SourceManager):
        """Setzt die Daten"""
        self.notes = notes
        self.source = source
        self.source_manager = manager
        self._refresh()
    
    def _refresh(self):
        """Aktualisiert die Anzeige"""
        self.list_widget.clear()
        
        if not self.notes:
            self.count_label.setText("0 Notizen")
            return
        
        for note in self.notes.notes:
            page_str = f"[S. {note.page}] " if note.page else ""
            preview = note.content[:100].replace("\n", " ")
            if len(note.content) > 100:
                preview += "..."
            
            item = QListWidgetItem(f"{page_str}{preview}")
            item.setData(Qt.ItemDataRole.UserRole, note)
            item.setToolTip(note.content)
            self.list_widget.addItem(item)
        
        self.count_label.setText(f"{len(self.notes)} Notizen")
    
    def _add_note(self):
        """Neue Notiz hinzufügen"""
        if not self.notes or not self.source_manager:
            return
        
        dialog = NoteDialog(self)
        if dialog.exec():
            content, page, tags = dialog.get_data()
            self.notes.add(content, page, tags)
            self.source_manager.save_notes(self.source, self.notes)
            self._refresh()
    
    def _edit_note(self, item: QListWidgetItem):
        """Notiz bearbeiten"""
        note = item.data(Qt.ItemDataRole.UserRole)
        if not note:
            return
        
        dialog = NoteDialog(self, note)
        if dialog.exec():
            content, page, tags = dialog.get_data()
            note.content = content
            note.page = page
            note.tags = tags
            from formats.base import now_iso
            note.updated_at = now_iso()
            self.source_manager.save_notes(self.source, self.notes)
            self._refresh()
    
    def clear(self):
        """Leert die Anzeige"""
        self.notes = None
        self.source = None
        self.list_widget.clear()
        self.count_label.setText("0 Notizen")


class NoteDialog(QDialog):
    """Dialog zum Erstellen/Bearbeiten einer Notiz"""
    
    def __init__(self, parent=None, note: Note = None):
        super().__init__(parent)
        self.note = note
        self.setWindowTitle("Notiz bearbeiten" if note else "Neue Notiz")
        self.setMinimumSize(500, 400)
        self._setup_ui()
        
        if note:
            self._load_note()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Seite
        page_layout = QHBoxLayout()
        page_layout.addWidget(QLabel("Seite:"))
        self.page_spin = QSpinBox()
        self.page_spin.setRange(0, 9999)
        self.page_spin.setSpecialValueText("Keine")
        page_layout.addWidget(self.page_spin)
        page_layout.addStretch()
        layout.addLayout(page_layout)
        
        # Tags
        tags_layout = QHBoxLayout()
        tags_layout.addWidget(QLabel("Tags:"))
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("tag1, tag2, tag3")
        tags_layout.addWidget(self.tags_input)
        layout.addLayout(tags_layout)
        
        # Inhalt + LaTeX-Preview (Splitter)
        layout.addWidget(QLabel("Notiz (LaTeX-Formeln mit $..$ oder $$..$$):"))

        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("Notiz eingeben... LaTeX-Formeln: $E=mc^2$ oder $$\\int f(x) dx$$")

        # LaTeX-Preview (erscheint automatisch wenn Formeln erkannt werden)
        self._latex_preview = LatexPreviewWidget()
        self._latex_preview.setVisible(False)

        self._preview_label = QLabel("Formel-Vorschau:")
        self._preview_label.setStyleSheet("color: #555; font-size: 11px; margin-top: 4px;")
        self._preview_label.setVisible(False)

        # Splitter: Editor oben, Preview unten
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.content_edit)

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
        self.content_edit.textChanged.connect(self._on_text_changed)

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
        text = self.content_edit.toPlainText()
        has_latex = contains_latex(text)

        self._preview_label.setVisible(has_latex)
        self._latex_preview.setVisible(has_latex)

        if has_latex:
            self._latex_preview.update_content(text)

    def _load_note(self):
        """Laedt bestehende Notiz"""
        if self.note:
            self.content_edit.setText(self.note.content)
            self.page_spin.setValue(self.note.page or 0)
            self.tags_input.setText(", ".join(self.note.tags))
            # Trigger LaTeX-Preview fuer bestehende Notizen
            self._on_text_changed()

    def get_data(self):
        """Gibt die Eingabedaten zurück"""
        content = self.content_edit.toPlainText()
        page = self.page_spin.value() if self.page_spin.value() > 0 else None
        tags_text = self.tags_input.text()
        tags = [t.strip() for t in tags_text.split(",") if t.strip()]
        return content, page, tags
