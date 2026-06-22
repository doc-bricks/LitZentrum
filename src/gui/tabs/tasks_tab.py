"""
LitZentrum - Aufgaben Tab
"""
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QTextEdit, QSpinBox, QLabel, QDialog, QDialogButtonBox,
    QLineEdit, QComboBox, QDateEdit, QCheckBox
)
from PySide6.QtCore import QDate

from core import LitSource, SourceManager
from formats import LiTask, Task


class TasksTab(QWidget):
    """Tab für Aufgaben"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks: Optional[LiTask] = None
        self.source: Optional[LitSource] = None
        self.source_manager: Optional[SourceManager] = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        add_btn = QPushButton("➕ Neue Aufgabe")
        add_btn.clicked.connect(self._add_task)
        toolbar.addWidget(add_btn)
        
        toolbar.addStretch()
        
        # Filter
        self.show_done = QCheckBox("Erledigte zeigen")
        self.show_done.stateChanged.connect(self._refresh)
        toolbar.addWidget(self.show_done)
        
        self.count_label = QLabel("0 Aufgaben")
        toolbar.addWidget(self.count_label)
        
        layout.addLayout(toolbar)
        
        # Liste
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.itemDoubleClicked.connect(self._edit_task)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)
    
    def set_data(self, tasks: LiTask, source: LitSource, manager: SourceManager):
        """Setzt die Daten"""
        self.tasks = tasks
        self.source = source
        self.source_manager = manager
        self._refresh()
    
    def _refresh(self):
        """Aktualisiert die Anzeige"""
        self.list_widget.clear()
        
        if not self.tasks:
            self.count_label.setText("0 Aufgaben")
            return
        
        show_done = self.show_done.isChecked()
        
        for task in self.tasks.tasks:
            if not show_done and task.status == "done":
                continue
            
            # Icon nach Status/Priorität
            if task.status == "done":
                icon = "✅"
            elif task.is_overdue:
                icon = "🔴"
            elif task.priority == "urgent":
                icon = "🔥"
            elif task.priority == "high":
                icon = "⚠️"
            else:
                icon = "○"
            
            page_str = f"[S. {task.page}] " if task.page else ""
            due_str = f" (bis {task.due_date})" if task.due_date else ""
            
            text = f"{icon} {page_str}{task.title}{due_str}"
            
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, task)
            
            if task.status == "done":
                item.setForeground(Qt.GlobalColor.gray)
            elif task.is_overdue:
                item.setForeground(Qt.GlobalColor.red)
            
            item.setToolTip(task.description or task.title)
            self.list_widget.addItem(item)
        
        open_count = self.tasks.open_count
        self.count_label.setText(f"{open_count} offen / {len(self.tasks)} gesamt")
    
    def _on_item_clicked(self, item: QListWidgetItem):
        """Einfacher Klick - Aufgabe erledigen"""
        task = item.data(Qt.ItemDataRole.UserRole)
        if not task:
            return
        
        # Rechtsklick oder Doppelklick zum Bearbeiten, hier nur Toggle
        pass
    
    def _add_task(self):
        """Neue Aufgabe hinzufügen"""
        if not self.tasks or not self.source_manager:
            return
        
        dialog = TaskDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            self.tasks.add(
                title=data["title"],
                description=data["description"],
                priority=data["priority"],
                due_date=data["due_date"],
                page=data["page"],
                tags=data["tags"]
            )
            self.source_manager.save_tasks(self.source, self.tasks)
            self._refresh()
    
    def _edit_task(self, item: QListWidgetItem):
        """Aufgabe bearbeiten"""
        task = item.data(Qt.ItemDataRole.UserRole)
        if not task:
            return
        
        dialog = TaskDialog(self, task)
        if dialog.exec():
            data = dialog.get_data()
            task.title = data["title"]
            task.description = data["description"]
            task.priority = data["priority"]
            task.due_date = data["due_date"]
            task.page = data["page"]
            task.tags = data["tags"]
            task.status = data["status"]
            
            if data["status"] == "done" and not task.completed_at:
                task.complete()
            
            self.source_manager.save_tasks(self.source, self.tasks)
            self._refresh()
    
    def clear(self):
        """Leert die Anzeige"""
        self.tasks = None
        self.source = None
        self.list_widget.clear()
        self.count_label.setText("0 Aufgaben")


class TaskDialog(QDialog):
    """Dialog zum Erstellen/Bearbeiten einer Aufgabe"""
    
    def __init__(self, parent=None, task: Task = None):
        super().__init__(parent)
        self.task = task
        self.setWindowTitle("Aufgabe bearbeiten" if task else "Neue Aufgabe")
        self.setMinimumSize(500, 400)
        self._setup_ui()
        
        if task:
            self._load_task()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Titel
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Titel:"))
        self.title_input = QLineEdit()
        title_layout.addWidget(self.title_input)
        layout.addLayout(title_layout)
        
        # Priorität & Status
        row_layout = QHBoxLayout()
        
        row_layout.addWidget(QLabel("Priorität:"))
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Normal", "Niedrig", "Hoch", "Dringend"])
        row_layout.addWidget(self.priority_combo)
        
        row_layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Offen", "In Arbeit", "Erledigt", "Abgebrochen"])
        row_layout.addWidget(self.status_combo)
        
        row_layout.addStretch()
        layout.addLayout(row_layout)
        
        # Fällig & Seite
        row2_layout = QHBoxLayout()
        
        row2_layout.addWidget(QLabel("Fällig:"))
        self.due_date = QDateEdit()
        self.due_date.setCalendarPopup(True)
        self.due_date.setSpecialValueText("Kein Datum")
        self.due_date.setMinimumDate(QDate(2000, 1, 1))
        row2_layout.addWidget(self.due_date)
        
        self.clear_date_btn = QPushButton("×")
        self.clear_date_btn.setFixedWidth(25)
        self.clear_date_btn.clicked.connect(lambda: self.due_date.setDate(QDate(2000, 1, 1)))
        row2_layout.addWidget(self.clear_date_btn)
        
        row2_layout.addWidget(QLabel("Seite:"))
        self.page_spin = QSpinBox()
        self.page_spin.setRange(0, 9999)
        self.page_spin.setSpecialValueText("Keine")
        row2_layout.addWidget(self.page_spin)
        
        row2_layout.addStretch()
        layout.addLayout(row2_layout)
        
        # Beschreibung
        layout.addWidget(QLabel("Beschreibung:"))
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(120)
        layout.addWidget(self.desc_edit)
        
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
    
    def _load_task(self):
        """Lädt bestehende Aufgabe"""
        if self.task:
            self.title_input.setText(self.task.title)
            self.desc_edit.setText(self.task.description or "")
            
            priority_map = {"normal": 0, "low": 1, "high": 2, "urgent": 3}
            self.priority_combo.setCurrentIndex(priority_map.get(self.task.priority, 0))
            
            status_map = {"open": 0, "in_progress": 1, "done": 2, "cancelled": 3}
            self.status_combo.setCurrentIndex(status_map.get(self.task.status, 0))
            
            if self.task.due_date:
                from datetime import datetime
                try:
                    date = datetime.fromisoformat(self.task.due_date)
                    self.due_date.setDate(QDate(date.year, date.month, date.day))
                except (ValueError, TypeError):
                    pass  # Ungültiges Datum ignorieren (BUG-U5)
            
            self.page_spin.setValue(self.task.page or 0)
            self.tags_input.setText(", ".join(self.task.tags))
    
    def get_data(self) -> dict:
        """Gibt die Eingabedaten zurück"""
        priority_map = {0: "normal", 1: "low", 2: "high", 3: "urgent"}
        status_map = {0: "open", 1: "in_progress", 2: "done", 3: "cancelled"}
        
        due_date = None
        if self.due_date.date().year() > 2000:
            due_date = self.due_date.date().toString("yyyy-MM-dd")
        
        tags_text = self.tags_input.text()
        
        return {
            "title": self.title_input.text(),
            "description": self.desc_edit.toPlainText() or None,
            "priority": priority_map[self.priority_combo.currentIndex()],
            "status": status_map[self.status_combo.currentIndex()],
            "due_date": due_date,
            "page": self.page_spin.value() if self.page_spin.value() > 0 else None,
            "tags": [t.strip() for t in tags_text.split(",") if t.strip()]
        }
