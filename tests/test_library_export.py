import json
import sys
import tempfile
import unittest
from pathlib import Path

import jsonschema

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core import LibraryExporter, ProjectManager, SourceManager
from formats import LiMeta, LiNote, LiQuote, LiSum, LiTask


class TestLibraryExport(unittest.TestCase):
    def _create_context(self):
        tempdir = tempfile.TemporaryDirectory()
        project_manager = ProjectManager()
        project = project_manager.create_project(
            path=Path(tempdir.name) / "Überblick",
            name="Überblick",
            description="Projekt für Übungsfälle",
        )
        source_manager = SourceManager(project.path, project.config.sources_folder)
        exporter = LibraryExporter(project_manager, source_manager)
        return tempdir, project_manager, project, source_manager, exporter

    def test_export_writes_valid_utf8_bundle(self):
        tempdir, project_manager, project, source_manager, exporter = self._create_context()
        try:
            pdf_path = Path(tempdir.name) / "eingang.pdf"
            pdf_path.write_bytes(b"%PDF-1.4\nTest")

            source = source_manager.create_source(
                LiMeta(
                    title="Ärztliche Übung",
                    authors=["Müller, Jörg"],
                    year=2024,
                    tags=["größer"],
                    abstract="Kurze Übersicht",
                ),
                pdf_path=pdf_path,
            )

            notes = LiNote()
            notes.add("Wichtige Größe", page=3, tags=["prüfung"])
            notes.notes[0].updated_at = notes.notes[0].created_at
            source_manager.save_notes(source, notes)

            quotes = LiQuote()
            quotes.add("Direktes Zitat", page=4, tags=["äußerung"])
            source_manager.save_quotes(source, quotes)

            tasks = LiTask()
            tasks.add("Abschnitt prüfen", priority="high")
            source_manager.save_tasks(source, tasks)

            summaries = LiSum()
            summaries.add("Kurzüberblick", "Inhalt mit Umlaut")
            summaries.summaries[0].updated_at = summaries.summaries[0].created_at
            source_manager.save_summaries(source, summaries)

            project_notes = LiNote()
            project_notes.add("Übergreifende Notiz")
            project_notes.notes[0].updated_at = project_notes.notes[0].created_at
            project_manager.save_project_notes(project_notes, project)

            project_tasks = LiTask()
            project_tasks.add("Projektweite Prüfung")
            project_manager.save_project_tasks(project_tasks, project)

            output_path = Path(tempdir.name) / "exports" / "bibliothek"
            written_path = exporter.export_project(project, output_path)

            raw = written_path.read_bytes()
            self.assertIn("Überblick".encode("utf-8"), raw)
            self.assertIn("Ärztliche Übung".encode("utf-8"), raw)

            payload = json.loads(written_path.read_text(encoding="utf-8"))
            with open(exporter.SCHEMA_FILE, "r", encoding="utf-8") as handle:
                schema = json.load(handle)
            jsonschema.validate(payload, schema)

            exported_project = payload["projects"][0]
            exported_source = exported_project["sources"][0]
            self.assertEqual(exported_project["name"], "Überblick")
            self.assertEqual(exported_source["metadata"]["title"], "Ärztliche Übung")
            self.assertEqual(exported_source["notes"][0]["content"], "Wichtige Größe")
            self.assertTrue(payload["bibliography"]["bibtex"].startswith("@article{"))
        finally:
            tempdir.cleanup()

    def test_export_uses_relative_paths_and_handles_missing_pdf(self):
        tempdir, _project_manager, project, source_manager, exporter = self._create_context()
        try:
            source = source_manager.create_source(
                LiMeta(
                    title="Fehlende Datei",
                    authors=["Beispiel, Eva"],
                    year=2025,
                    source_file="quelle.pdf",
                )
            )

            payload = exporter.build_bundle(project)
            file_entry = payload["projects"][0]["sources"][0]["files"][0]

            self.assertEqual(
                file_entry["relative_path"],
                f"{project.config.sources_folder}/{source.path.name}/quelle.pdf",
            )
            self.assertFalse(file_entry["included"])
            self.assertFalse(file_entry["exists"])
            self.assertIsNone(file_entry["sha256"])

            dumped = json.dumps(payload, ensure_ascii=False)
            self.assertNotIn(str(project.path), dumped)
            self.assertNotIn(tempdir.name, dumped)
        finally:
            tempdir.cleanup()

    def test_export_strips_absolute_source_file_from_metadata(self):
        tempdir, _project_manager, project, source_manager, exporter = self._create_context()
        try:
            source_manager.create_source(
                LiMeta(
                    title="Privater Pfad",
                    authors=["Beispiel, Eva"],
                    year=2025,
                    source_file=r"C:\Users\Example\Private\quelle.pdf",
                )
            )

            payload = exporter.build_bundle(project)
            dumped = json.dumps(payload, ensure_ascii=False)
            exported_source = payload["projects"][0]["sources"][0]

            self.assertEqual(exported_source["metadata"]["source_file"], "quelle.pdf")
            self.assertEqual(exported_source["files"][0]["relative_path"], "Quellen/Beispiel2025_Privater_Pfad/quelle.pdf")
            self.assertNotIn(r"C:\Users\Example\Private", dumped)
        finally:
            tempdir.cleanup()

    def test_export_empty_project_creates_empty_bundle(self):
        tempdir, _project_manager, project, _source_manager, exporter = self._create_context()
        try:
            payload = exporter.build_bundle(project)
            exported_project = payload["projects"][0]

            self.assertEqual(exported_project["sources"], [])
            self.assertEqual(exported_project["project_notes"], [])
            self.assertEqual(exported_project["project_tasks"], [])
            self.assertEqual(payload["bibliography"]["bibtex"], "")

            exporter.validate_bundle(payload)
        finally:
            tempdir.cleanup()


class TestLiMetaFromDict(unittest.TestCase):
    """Regression tests for LiMeta.from_dict null-field handling."""

    def test_null_title_falls_back_to_untitled(self):
        """Regression: data.get('title','Untitled') silently passes None through
        when the JSON has "title": null.  Using `or` catches the null case."""
        meta = LiMeta.from_dict({"title": None})
        self.assertEqual(meta.title, "Untitled")

    def test_null_title_roundtrip_does_not_crash_search_sources(self):
        """Roundtrip via to_dict/from_dict must not produce a None title.
        If it did, search_sources() would crash on meta.title.lower()."""
        # A source saved with title="" and reloaded must keep title non-None
        original = LiMeta(title="")
        reloaded = LiMeta.from_dict(original.to_dict())
        # to_dict stores "" → from_dict sees "" → `"" or "Untitled"` = "Untitled"
        # Either way, title must be a non-None str
        self.assertIsInstance(reloaded.title, str)
        # Confirm .lower() does not crash (the actual call in search_sources)
        reloaded.title.lower()  # must not raise

    def test_null_title_bibtex_key_does_not_crash(self):
        """bibtex_key calls _to_ascii(self.title) — must not raise for null title."""
        meta = LiMeta.from_dict({"title": None})
        # After the fix, title is "Untitled" — bibtex_key must not raise
        key = meta.bibtex_key
        self.assertIn("untitled", key)


if __name__ == "__main__":
    unittest.main()
