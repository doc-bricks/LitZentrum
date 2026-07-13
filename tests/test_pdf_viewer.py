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


def test_pdf_viewer_symbol_controls_expose_accessible_context():
    """Die kompakte Symbol-Toolbar muss Screenreadern sprechenden Kontext geben."""
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)

    from gui.widgets.pdf_viewer import PDFViewer
    viewer = PDFViewer()

    controls = [
        (viewer.prev_btn, "Vorherige Seite", "Vorherige Seite"),
        (viewer.next_btn, "Nächste Seite", "Nächste Seite"),
        (viewer.zoom_out_btn, "Verkleinern", "Verkleinern"),
        (viewer.zoom_in_btn, "Vergrößern", "Vergrößern"),
        (viewer.fit_width_btn, "An Breite anpassen", "An Breite anpassen"),
        (viewer.fit_page_btn, "An Seite anpassen", "An Seite anpassen"),
    ]

    for widget, name, tooltip in controls:
        assert widget.accessibleName() == name
        assert widget.toolTip() == tooltip
        assert widget.accessibleDescription()

    assert viewer.page_spin.accessibleName() == "Aktuelle Seite"
    assert viewer.page_spin.toolTip()
    assert viewer.page_spin.accessibleDescription()

    assert viewer.zoom_combo.accessibleName() == "Zoomstufe"
    assert viewer.zoom_combo.toolTip()
    assert viewer.zoom_combo.accessibleDescription()
