import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core import ProjectManager, SourceManager
from formats import LiMeta


class TestSourceManager(unittest.TestCase):
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
