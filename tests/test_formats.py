"""
LitZentrum - Tests für Format-Klassen
"""
import sys
from pathlib import Path

# Pfad hinzufügen
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
import tempfile


class TestLiMetaFormat(unittest.TestCase):
    """Tests für LiMeta"""
    
    def test_create_minimal(self):
        from formats import LiMeta
        
        meta = LiMeta(title="Test Article")
        self.assertEqual(meta.title, "Test Article")
        self.assertEqual(meta.authors, [])
        self.assertEqual(meta.schema_version, "1.0.0")
    
    def test_create_full(self):
        from formats import LiMeta
        
        meta = LiMeta(
            title="Understanding AI",
            authors=["Smith, John", "Doe, Jane"],
            year=2024,
            doi="10.1234/example",
            source_type="article",
        )
        
        self.assertEqual(meta.title, "Understanding AI")
        self.assertEqual(len(meta.authors), 2)
        self.assertEqual(meta.year, 2024)
        self.assertEqual(meta.first_author, "Smith")
    
    def test_citation_key(self):
        from formats import LiMeta
        
        meta = LiMeta(
            title="Test",
            authors=["Mueller, Hans"],
            year=2023,
        )
        
        self.assertEqual(meta.citation_key, "Mueller2023")
    
    def test_save_load(self):
        from formats import LiMeta
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "meta.limeta"
            
            original = LiMeta(
                title="Test Article",
                authors=["Author One"],
                year=2024,
                tags=["test", "example"],
            )
            original.save(path)
            
            # Datei existiert
            self.assertTrue(path.exists())
            
            # Laden
            loaded = LiMeta.load(path)
            self.assertEqual(loaded.title, original.title)
            self.assertEqual(loaded.authors, original.authors)
            self.assertEqual(loaded.year, original.year)
            self.assertEqual(loaded.tags, original.tags)


class TestLiNoteFormat(unittest.TestCase):
    """Tests für LiNote"""
    
    def test_create_empty(self):
        from formats import LiNote
        
        notes = LiNote()
        self.assertEqual(len(notes), 0)
    
    def test_add_notes(self):
        from formats import LiNote
        
        notes = LiNote()
        notes.add("Erste Notiz", page=1, tags=["wichtig"])
        notes.add("Zweite Notiz", page=5)
        
        self.assertEqual(len(notes), 2)
        self.assertEqual(notes.notes[0].content, "Erste Notiz")
        self.assertEqual(notes.notes[0].page, 1)
    
    def test_get_by_page(self):
        from formats import LiNote
        
        notes = LiNote()
        notes.add("Seite 1", page=1)
        notes.add("Seite 5", page=5)
        notes.add("Auch Seite 1", page=1)
        
        page1_notes = notes.get_by_page(1)
        self.assertEqual(len(page1_notes), 2)


class TestLiQuoteFormat(unittest.TestCase):
    """Tests für LiQuote"""
    
    def test_add_quotes(self):
        from formats import LiQuote
        
        quotes = LiQuote()
        quotes.add("Direktes Zitat", page=10, quote_type="direct")
        quotes.add("Indirektes Zitat", page=15, quote_type="indirect")
        
        self.assertEqual(len(quotes), 2)
        
        direct = quotes.get_direct()
        self.assertEqual(len(direct), 1)

    def test_page_range_formatting(self):
        from formats.liquote import Quote

        # Single page
        q1 = Quote(id="q1", type="direct", text="Text 1", page=10, created_at="2026-09-14T12:00:00")
        self.assertEqual(q1.page_range, "10")

        # Equal start and end
        q2 = Quote(id="q2", type="direct", text="Text 2", page=10, page_end=10, created_at="2026-09-14T12:00:00")
        self.assertEqual(q2.page_range, "10")

        # Multi-page range
        q3 = Quote(id="q3", type="direct", text="Text 3", page=10, page_end=15, created_at="2026-09-14T12:00:00")
        self.assertEqual(q3.page_range, "10-15")

        # Inverted range normalized
        q4 = Quote(id="q4", type="direct", text="Text 4", page=15, page_end=10, created_at="2026-09-14T12:00:00")
        self.assertEqual(q4.page_range, "10-15")

        # Only page_end (no "None-5")
        q5 = Quote(id="q5", type="direct", text="Text 5", page=None, page_end=5, created_at="2026-09-14T12:00:00")
        self.assertEqual(q5.page_range, "5")

        # Page 0 (not treated as empty/None)
        q6 = Quote(id="q6", type="direct", text="Text 6", page=0, created_at="2026-09-14T12:00:00")
        self.assertEqual(q6.page_range, "0")

        # None
        q7 = Quote(id="q7", type="direct", text="Text 7", page=None, created_at="2026-09-14T12:00:00")
        self.assertEqual(q7.page_range, "")

    def test_add_quote_with_page_end(self):
        from formats import LiQuote

        quotes = LiQuote()
        q = quotes.add("Zitat über mehrere Seiten", page=20, page_end=25)
        self.assertEqual(q.page, 20)
        self.assertEqual(q.page_end, 25)
        self.assertEqual(q.page_range, "20-25")

        d = quotes.to_dict()
        loaded = LiQuote.from_dict(d)
        self.assertEqual(len(loaded.quotes), 1)
        self.assertEqual(loaded.quotes[0].page_end, 25)
        self.assertEqual(loaded.quotes[0].page_range, "20-25")

    def test_get_by_page_range(self):
        from formats import LiQuote

        quotes = LiQuote()
        quotes.add("Abschnitt A", page=5, page_end=8)
        quotes.add("Abschnitt B", page=7)

        # Page 4: none
        self.assertEqual(len(quotes.get_by_page(4)), 0)
        # Page 5: Abschnitt A
        self.assertEqual(len(quotes.get_by_page(5)), 1)
        # Page 7: both Abschnitt A and Abschnitt B
        self.assertEqual(len(quotes.get_by_page(7)), 2)
        # Page 8: Abschnitt A
        self.assertEqual(len(quotes.get_by_page(8)), 1)
        # Page 9: none
        self.assertEqual(len(quotes.get_by_page(9)), 0)


class TestLiTaskFormat(unittest.TestCase):
    """Tests für LiTask"""
    
    def test_add_tasks(self):
        from formats import LiTask
        
        tasks = LiTask()
        tasks.add("Kapitel 1 lesen", priority="high")
        tasks.add("Zusammenfassung schreiben", due_date="2024-12-31")
        
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks.open_count, 2)
    
    def test_complete_task(self):
        from formats import LiTask
        
        tasks = LiTask()
        tasks.add("Test Task")
        
        tasks.complete(tasks.tasks[0].id)
        
        self.assertEqual(tasks.tasks[0].status, "done")
        self.assertIsNotNone(tasks.tasks[0].completed_at)


class TestProjectManager(unittest.TestCase):
    """Tests für ProjectManager"""
    
    def test_create_project(self):
        from core import ProjectManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = ProjectManager()
            
            project = pm.create_project(
                path=Path(tmpdir) / "TestProjekt",
                name="Test Projekt",
                description="Ein Testprojekt",
            )
            
            self.assertTrue(project.path.exists())
            self.assertTrue(project.sources_path.exists())
            self.assertTrue((project.path / "projekt_config.liproj").exists())
    
    def test_open_project(self):
        from core import ProjectManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = ProjectManager()
            
            # Erstellen
            project = pm.create_project(
                path=Path(tmpdir) / "TestProjekt",
                name="Test Projekt",
            )
            
            pm.close_project()
            
            # Neu öffnen
            reopened = pm.open_project(project.path)
            self.assertEqual(reopened.name, "Test Projekt")


if __name__ == "__main__":
    unittest.main()
