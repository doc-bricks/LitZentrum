"""
LitZentrum - Tests fuer den BibTeX-Export.
"""
import sys
import tempfile
from pathlib import Path

# Projekt-src zum Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest


class TestBibTeXExport(unittest.TestCase):
    """Regressionstests fuer den BibTeX-Export."""

    def test_save_bibliography_creates_parent_directory_and_bib_suffix(self):
        from formats import LiMeta
        from modules.bibliography.bibtex import BibTeXGenerator

        meta = LiMeta(
            title="Test Article",
            authors=["Doe, Jane"],
            year=2024,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "exports" / "refs"

            generator = BibTeXGenerator()
            generator.save_bibliography([meta], output_path)

            expected_path = output_path.with_suffix(".bib")
            self.assertTrue(expected_path.exists())

            content = expected_path.read_text(encoding="utf-8")
            self.assertIn(f"@article{{{meta.citation_key},", content)
            self.assertIn("title = {Test Article}", content)
            self.assertIn("author = {Doe, Jane}", content)


if __name__ == "__main__":
    unittest.main()
