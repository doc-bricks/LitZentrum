import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core import ProjectManager, SourceManager
from formats import LiMeta


class TestSourceManager(unittest.TestCase):
    def test_generate_folder_name_strips_invalid_path_chars_from_author(self):
        """Author names with '/' or other invalid chars must not create nested dirs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = ProjectManager().create_project(
                path=Path(tmpdir) / "TestProjekt",
                name="Test Projekt",
            )
            manager = SourceManager(project.path, project.config.sources_folder)
            meta = LiMeta(
                title="A Study",
                authors=["Smith/Jones, John"],
                year=2020,
            )
            folder_name = manager._generate_folder_name(meta)
            self.assertNotIn("/", folder_name)
            self.assertNotIn("\\", folder_name)
            self.assertNotIn(":", folder_name)
            # The created folder must be a single flat directory
            source = manager.create_source(meta)
            self.assertEqual(source.path.parent, manager.sources_path)

    def test_generate_folder_name_falls_back_when_author_fully_stripped(self):
        """If all chars are invalid, author portion falls back to 'Unbekannt'."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = ProjectManager().create_project(
                path=Path(tmpdir) / "TestProjekt",
                name="Test Projekt",
            )
            manager = SourceManager(project.path, project.config.sources_folder)
            meta = LiMeta(title="T", authors=["///"], year=2021)
            folder_name = manager._generate_folder_name(meta)
            self.assertTrue(folder_name.startswith("Unbekannt"))

    def test_create_source_uses_unique_folder_for_duplicate_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project = ProjectManager().create_project(
                path=Path(tmpdir) / "TestProjekt",
                name="Test Projekt",
            )
            manager = SourceManager(project.path, project.config.sources_folder)

            first = manager.create_source(
                LiMeta(
                    title="Duplicate Title",
                    authors=["Smith, Jane"],
                    year=2024,
                    tags=["first"],
                )
            )
            second = manager.create_source(
                LiMeta(
                    title="Duplicate Title",
                    authors=["Smith, Jane"],
                    year=2024,
                    tags=["second"],
                )
            )

            self.assertNotEqual(first.path, second.path)
            self.assertEqual(first.path.name, "Smith2024_Duplicate_Title")
            self.assertEqual(second.path.name, "Smith2024_Duplicate_Title_2")
            self.assertEqual(len(manager.get_all_sources()), 2)
            self.assertEqual(manager.load_source(first.path).meta.tags, ["first"])
            self.assertEqual(manager.load_source(second.path).meta.tags, ["second"])


if __name__ == "__main__":
    unittest.main()
