"""Regressionstests — bugfix-library-transfer 2026-06-21."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
SYNC_MODULE = ROOT / "src" / "modules" / "sync" / "__init__.py"
BASE_FORMAT = ROOT / "src" / "formats" / "base.py"
LIBRARY_EXPORT = ROOT / "src" / "core" / "library_export.py"


class TestD3SyncSubprocessTimeouts(unittest.TestCase):
    """BUG-D3: subprocess.run in sync/__init__.py ohne timeout=."""

    def setUp(self):
        self.src = SYNC_MODULE.read_text(encoding="utf-8")

    def _assert_cmd_has_timeout(self, cmd_snippet):
        idx = self.src.find(cmd_snippet)
        self.assertGreater(idx, 0, f'"{cmd_snippet}" nicht in sync/__init__.py gefunden')
        snippet = self.src[idx:idx + 200]
        self.assertIn("timeout", snippet,
                      f'subprocess.run mit "{cmd_snippet}" ohne timeout= — BUG-D3')

    def test_git_version_has_timeout(self):
        self._assert_cmd_has_timeout('"--version"')

    def test_git_init_has_timeout(self):
        self._assert_cmd_has_timeout('"init"')

    def test_git_status_has_timeout(self):
        self._assert_cmd_has_timeout('"status"')

    def test_git_add_has_timeout(self):
        self._assert_cmd_has_timeout('"-A"')

    def test_git_commit_has_timeout(self):
        self._assert_cmd_has_timeout('"-m", message')


class TestU2BaseFormatJsonLoad(unittest.TestCase):
    """BUG-U2: json.load ohne JSONDecodeError-Handler in formats/base.py."""

    def setUp(self):
        self.src = BASE_FORMAT.read_text(encoding="utf-8")

    def test_get_schema_has_json_error_handler(self):
        idx = self.src.find("def get_schema")
        self.assertGreater(idx, 0)
        snippet = self.src[idx:idx + 600]
        self.assertIn("JSONDecodeError", snippet,
                      "get_schema: json.load ohne JSONDecodeError-Handler — BUG-U2")

    def test_load_has_json_error_handler(self):
        idx = self.src.find("def load(")
        self.assertGreater(idx, 0)
        snippet = self.src[idx:idx + 600]
        self.assertIn("JSONDecodeError", snippet,
                      "load(): json.load ohne JSONDecodeError-Handler — BUG-U2")


class TestU2LibraryExportJsonLoad(unittest.TestCase):
    """BUG-U2: json.load ohne Handler in core/library_export.py."""

    def test_validate_bundle_has_json_error_handler(self):
        src = LIBRARY_EXPORT.read_text(encoding="utf-8")
        idx = src.find("def validate_bundle")
        self.assertGreater(idx, 0, "def validate_bundle nicht in library_export.py gefunden")
        snippet = src[idx:idx + 600]
        self.assertIn("JSONDecodeError", snippet,
                      "validate_bundle: json.load ohne JSONDecodeError-Handler — BUG-U2")


if __name__ == "__main__":
    unittest.main()
