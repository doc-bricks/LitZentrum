"""Tests for PDFViewer.search() — pdf_tab.py calls self.pdf_viewer.search(query)."""
import sys
from pathlib import Path

# src/ in Suchpfad eintragen (wie die anderen Testdateien)
_src = str(Path(__file__).parent.parent / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)


def test_pdf_viewer_has_search_method():
    """PDFViewer must expose search() — pdf_tab.py calls it directly."""
    from gui.widgets.pdf_viewer import PDFViewer
    assert callable(getattr(PDFViewer, "search", None)), (
        "PDFViewer is missing a search() method; "
        "pdf_tab._search_pdf() calls self.pdf_viewer.search(query) which raises AttributeError"
    )


def test_pdf_viewer_search_returns_empty_without_doc():
    """search() must return [] when no PDF is loaded."""
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)

    from gui.widgets.pdf_viewer import PDFViewer
    viewer = PDFViewer()
    assert viewer.search("anything") == []
    assert viewer.search("") == []


def test_pdf_viewer_search_finds_text_and_returns_1based_page(tmp_path):
    """search() must return 1-based page numbers and the expected keys."""
    try:
        import fitz
    except ImportError:
        import pytest
        pytest.skip("PyMuPDF nicht verfügbar")

    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)

    # Einseitiges In-Memory-PDF mit dem Suchbegriff "needle" erzeugen
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "needle")
    pdf_path = tmp_path / "search_test.pdf"
    doc.save(str(pdf_path))
    doc.close()

    from gui.widgets.pdf_viewer import PDFViewer
    viewer = PDFViewer()
    viewer.open_pdf(pdf_path)

    hits = viewer.search("needle")
    assert hits, "search() sollte mindestens einen Treffer liefern"
    assert hits[0]["page"] == 1, "Seitennummer muss 1-basiert sein (wie go_to_page() erwartet)"
    assert set(hits[0]) == {"page", "rect"}, "Dict-Keys müssen {'page', 'rect'} sein"

    # Kein Treffer bei unbekanntem Begriff
    assert viewer.search("xyz_nonexistent_42") == []


def test_pdf_viewer_toolbar_is_not_a_qtoolbar():
    """Die Werkzeugleiste des Viewers darf KEINE QToolBar sein.

    Regression WP-LZ-01: QMainWindow.restoreState() sucht QToolBar-Kinder
    rekursiv und ordnet sie ueber den objectName dem gespeicherten
    Fensterzustand zu. Eine hier verschachtelte QToolBar wurde dadurch in das
    Toolbar-Band des Hauptfensters gezogen (gemessene Geometrie (0, 21, 417, 33)
    statt (0, 0, 760, 33)) und vom darunter liegenden Viewer ueberdeckt --
    sichtbar blieb nur die obere Haelfte der Knopfreihe.
    """
    from PySide6.QtWidgets import QApplication, QToolBar
    app = QApplication.instance() or QApplication(sys.argv)

    from gui.widgets.pdf_viewer import PDFViewer
    viewer = PDFViewer()

    found = viewer.findChildren(QToolBar)
    assert not found, (
        "PDFViewer enthaelt eine verschachtelte QToolBar. "
        "QMainWindow.restoreState() reisst sie in das Toolbar-Band des "
        "Hauptfensters; die Knopfreihe wird dann vom Viewer ueberdeckt. "
        "Stattdessen QWidget + QHBoxLayout verwenden."
    )


def test_pdf_viewer_toolbar_does_not_overlap_viewer():
    """Werkzeugleiste und Scrollbereich duerfen sich nicht ueberlappen."""
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)

    from gui.widgets.pdf_viewer import PDFViewer
    viewer = PDFViewer()
    viewer.resize(760, 600)
    viewer.show()
    app.processEvents()

    toolbar = viewer.layout().itemAt(0).widget()
    scroll_area = viewer.scroll_area
    overlap = (toolbar.y() + toolbar.height()) - scroll_area.y()

    viewer.close()

    assert overlap <= 0, (
        f"Werkzeugleiste ragt {overlap}px in den Scrollbereich hinein "
        f"(Leiste {toolbar.geometry()}, Ansicht {scroll_area.geometry()}). "
        "Die Knopfreihe wird dadurch abgeschnitten."
    )


def test_pdf_viewer_toolbar_keeps_minimum_height():
    """Die Leiste behaelt ihre Hoehe, auch wenn der Viewer stark gestaucht wird."""
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)

    from gui.widgets.pdf_viewer import PDFViewer
    viewer = PDFViewer()
    toolbar = viewer.layout().itemAt(0).widget()
    natural = toolbar.sizeHint().height()

    viewer.resize(760, 60)  # absichtlich viel zu niedrig
    viewer.show()
    app.processEvents()
    squeezed = toolbar.height()
    viewer.close()

    assert squeezed >= natural, (
        f"Werkzeugleiste auf {squeezed}px gestaucht (natuerlich {natural}px) -- "
        "die Knoepfe waeren angeschnitten."
    )
