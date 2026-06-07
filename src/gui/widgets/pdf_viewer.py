"""
LitZentrum - PDF Viewer Widget
Integrierter PDF-Betrachter mit Textauswahl
"""
from pathlib import Path
from typing import Optional, Callable

from PySide6.QtCore import Qt, Signal, QPoint, QRect
from PySide6.QtGui import QPixmap, QImage, QPainter, QColor, QWheelEvent, QMouseEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel,
    QPushButton, QSpinBox, QComboBox, QToolBar, QFrame,
    QSizePolicy
)

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False


class PDFPageWidget(QLabel):
    """Widget für eine einzelne PDF-Seite"""
    
    text_selected = Signal(str, int, tuple)  # text, page, rect
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: #808080;")
        
        self._selecting = False
        self._selection_start = None
        self._selection_end = None
        self._page_num = 0
        self._zoom = 1.0
    
    def set_page_info(self, page_num: int, zoom: float):
        """Setzt Seiten-Info für Textauswahl"""
        self._page_num = page_num
        self._zoom = zoom


class PDFViewer(QWidget):
    """PDF-Betrachter Widget"""
    
    page_changed = Signal(int)  # Aktuelle Seite
    text_selected = Signal(str, int)  # Text, Seite
    
    ZOOM_LEVELS = [50, 75, 100, 125, 150, 200, 300]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.doc = None
        self.current_page = 0
        self.page_count = 0
        self.zoom_level = 100
        self.pdf_path: Optional[Path] = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        
        # Navigation
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setFixedWidth(30)
        self.prev_btn.clicked.connect(self.previous_page)
        toolbar.addWidget(self.prev_btn)
        
        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.setMaximum(1)
        self.page_spin.valueChanged.connect(self._on_page_changed)
        toolbar.addWidget(self.page_spin)
        
        self.page_label = QLabel(" / 0")
        toolbar.addWidget(self.page_label)
        
        self.next_btn = QPushButton("▶")
        self.next_btn.setFixedWidth(30)
        self.next_btn.clicked.connect(self.next_page)
        toolbar.addWidget(self.next_btn)
        
        toolbar.addSeparator()
        
        # Zoom
        self.zoom_out_btn = QPushButton("−")
        self.zoom_out_btn.setFixedWidth(30)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        toolbar.addWidget(self.zoom_out_btn)
        
        self.zoom_combo = QComboBox()
        self.zoom_combo.setEditable(False)
        for level in self.ZOOM_LEVELS:
            self.zoom_combo.addItem(f"{level}%", level)
        self.zoom_combo.setCurrentText("100%")
        self.zoom_combo.currentIndexChanged.connect(self._on_zoom_changed)
        toolbar.addWidget(self.zoom_combo)
        
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setFixedWidth(30)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        toolbar.addWidget(self.zoom_in_btn)
        
        toolbar.addSeparator()
        
        # Fit-Buttons
        self.fit_width_btn = QPushButton("↔")
        self.fit_width_btn.setToolTip("An Breite anpassen")
        self.fit_width_btn.clicked.connect(self.fit_width)
        toolbar.addWidget(self.fit_width_btn)
        
        self.fit_page_btn = QPushButton("◻")
        self.fit_page_btn.setToolTip("An Seite anpassen")
        self.fit_page_btn.clicked.connect(self.fit_page)
        toolbar.addWidget(self.fit_page_btn)
        
        layout.addWidget(toolbar)
        
        # Scroll-Bereich für PDF
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setStyleSheet("background-color: #606060;")
        
        self.page_widget = PDFPageWidget()
        self.page_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.scroll_area.setWidget(self.page_widget)
        
        layout.addWidget(self.scroll_area)
        
        self._show_placeholder()
    
    def _show_placeholder(self):
        """Zeigt Platzhalter wenn kein PDF geladen"""
        self.page_widget.setText("Kein PDF geladen\n\nWählen Sie eine Quelle mit PDF")
        self.page_widget.setStyleSheet("color: #999; font-size: 14px; background-color: #505050;")
    
    def open_pdf(self, path: Path) -> bool:
        """Öffnet eine PDF-Datei"""
        if not HAS_PYMUPDF:
            self.page_widget.setText("PyMuPDF nicht installiert\n\npip install PyMuPDF")
            return False
        
        path = Path(path)
        if not path.exists():
            return False
        
        try:
            if self.doc:
                self.doc.close()
            
            self.doc = fitz.open(str(path))
            self.pdf_path = path
            self.page_count = len(self.doc)
            self.current_page = 0
            
            self.page_spin.setMaximum(self.page_count)
            self.page_spin.setValue(1)
            self.page_label.setText(f" / {self.page_count}")
            
            self._render_page()
            return True
            
        except Exception as e:
            self.page_widget.setText(f"Fehler beim Öffnen:\n{e}")
            return False
    
    def close_pdf(self):
        """Schließt das aktuelle PDF"""
        if self.doc:
            self.doc.close()
            self.doc = None
        
        self.pdf_path = None
        self.page_count = 0
        self.current_page = 0
        self._show_placeholder()
    
    def _render_page(self):
        """Rendert die aktuelle Seite"""
        if not self.doc or self.current_page >= self.page_count:
            return
        
        page = self.doc[self.current_page]
        zoom = self.zoom_level / 100.0
        mat = fitz.Matrix(zoom * 1.5, zoom * 1.5)
        pix = page.get_pixmap(matrix=mat)
        
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(img)
        
        self.page_widget.setPixmap(pixmap)
        self.page_widget.setStyleSheet("background-color: white;")
        self.page_widget.set_page_info(self.current_page, zoom)
        self.page_widget.adjustSize()
    
    def _on_page_changed(self, page: int):
        self.current_page = page - 1
        self._render_page()
        self.page_changed.emit(self.current_page + 1)
    
    def _on_zoom_changed(self, index: int):
        self.zoom_level = self.zoom_combo.currentData()
        self._render_page()
    
    def next_page(self):
        if self.current_page < self.page_count - 1:
            self.page_spin.setValue(self.current_page + 2)
    
    def previous_page(self):
        if self.current_page > 0:
            self.page_spin.setValue(self.current_page)
    
    def go_to_page(self, page: int):
        if 1 <= page <= self.page_count:
            self.page_spin.setValue(page)
    
    def zoom_in(self):
        idx = self.zoom_combo.currentIndex()
        if idx < len(self.ZOOM_LEVELS) - 1:
            self.zoom_combo.setCurrentIndex(idx + 1)
    
    def zoom_out(self):
        idx = self.zoom_combo.currentIndex()
        if idx > 0:
            self.zoom_combo.setCurrentIndex(idx - 1)
    
    def fit_width(self):
        if not self.doc:
            return
        page = self.doc[self.current_page]
        page_width = page.rect.width
        view_width = self.scroll_area.viewport().width() - 20
        zoom = int((view_width / page_width) * 100 / 1.5)
        zoom = max(50, min(300, zoom))
        for i, level in enumerate(self.ZOOM_LEVELS):
            if level >= zoom:
                self.zoom_combo.setCurrentIndex(max(0, i - 1))
                break
    
    def fit_page(self):
        if not self.doc:
            return
        page = self.doc[self.current_page]
        view_width = self.scroll_area.viewport().width() - 20
        view_height = self.scroll_area.viewport().height() - 20
        zoom_w = (view_width / page.rect.width) * 100 / 1.5
        zoom_h = (view_height / page.rect.height) * 100 / 1.5
        zoom = int(min(zoom_w, zoom_h))
        zoom = max(50, min(300, zoom))
        for i, level in enumerate(self.ZOOM_LEVELS):
            if level >= zoom:
                self.zoom_combo.setCurrentIndex(max(0, i - 1))
                break
    
    def get_text(self, page: int = None) -> str:
        if not self.doc:
            return ""
        if page is None:
            page = self.current_page
        if 0 <= page < self.page_count:
            return self.doc[page].get_text()
        return ""

    def search(self, query: str) -> list:
        """Sucht Text im gesamten PDF und gibt seitenweise Treffer zurück."""
        if not self.doc or not query:
            return []
        results = []
        for page_num, page in enumerate(self.doc):
            for rect in page.search_for(query):
                results.append({
                    "page": page_num + 1,
                    "rect": (rect.x0, rect.y0, rect.x1, rect.y1),
                })
        return results
    
    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

    def closeEvent(self, event):
        # FIX fitz document leak: Das fitz-Dokument wird nie geschlossen wenn das
        # Widget zerstoert wird. PyMuPDF haelt interne C-Ressourcen und File-Handles.
        # close_pdf() setzt self.doc = None nach doc.close(), verhindert doppeltes Close.
        self.close_pdf()
        super().closeEvent(event)

    def __del__(self):
        # Sicherheitsnetz: Falls closeEvent nicht aufgerufen wurde (z.B. bei
        # direkter Widget-Loeschung ohne Window-Close).
        try:
            if self.doc:
                self.doc.close()
                self.doc = None
        except Exception:
            pass
