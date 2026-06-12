from __future__ import annotations

import json
import tempfile
from pathlib import Path

from generate_store_screenshots import SCREENSHOT_FILES, SUMMARY_FILE, generate_store_screenshots


def test_generate_store_screenshots_creates_expected_pngs_and_summary() -> None:
    with tempfile.TemporaryDirectory(prefix="litzentrum-store-shots-test-") as tmp_dir:
        output_dir = Path(tmp_dir)
        targets = generate_store_screenshots(output_dir)

        expected = {output_dir / name for name in SCREENSHOT_FILES.values()}
        assert set(targets) == expected

        for target in targets:
            data = target.read_bytes()
            assert data.startswith(b"\x89PNG\r\n\x1a\n")
            assert len(data) > 4096

        summary = json.loads((output_dir / SUMMARY_FILE).read_text(encoding="utf-8"))
        assert [entry["name"] for entry in summary["files"]] == list(SCREENSHOT_FILES.values())
