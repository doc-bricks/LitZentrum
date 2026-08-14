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


# --- Tofu-Regression (Welle-1 U2) ------------------------------------------
# Root-Cause: QT_QPA_PLATFORM=offscreen + widget.grab() rendert auf diesem
# System keine echten Glyphen (.notdef-Kaestchen = Tofu). Die erzeugten
# Store-Screenshots bestanden dadurch komplett aus leeren Kaestchen.
# Fix: native Plattform + Qt.WA_DontShowOnScreen. Diese Tests sichern dagegen.

def _generator_source() -> str:
    generator = Path(__file__).resolve().parents[1] / "generate_store_screenshots.py"
    return generator.read_text(encoding="utf-8")


def test_generator_uses_native_platform_not_offscreen() -> None:
    """Der Generator darf die offscreen-Plattform nicht erzwingen."""
    import re

    source = _generator_source()
    assert "WA_DontShowOnScreen" in source, (
        "Fix fehlt: Das Fenster muss ueber WA_DontShowOnScreen unsichtbar "
        "gehalten werden statt ueber die offscreen-Plattform."
    )
    forces_offscreen = re.search(
        r"""environ(?:\.setdefault\(|\[)\s*["']QT_QPA_PLATFORM["']\s*[,\]]\s*=?\s*["']offscreen["']""",
        source,
    )
    assert not forces_offscreen, (
        "Generator setzt QT_QPA_PLATFORM auf offscreen -- die Screenshots "
        "wuerden Tofu (Kaestchen statt Text) enthalten."
    )


def test_generator_guards_against_offscreen_at_runtime() -> None:
    """Auch zur Laufzeit muss offscreen erkannt und abgelehnt werden."""
    source = _generator_source()
    assert 'platform_name == "offscreen"' in source, (
        "Laufzeit-Guard fehlt: Laeuft Qt doch unter offscreen, muss der "
        "Generator abbrechen statt unbrauchbare Bilder zu schreiben."
    )


def test_status_message_hides_overlapping_label() -> None:
    """Die Statuszeile darf sich nicht mit dem Projekt-Label ueberlagern."""
    source = _generator_source()
    assert "_show_status_message" in source, (
        "Ohne _show_status_message zeichnen Statusbotschaft und Projekt-Label "
        "uebereinander -- im Screenshot entsteht unlesbarer Textsalat."
    )
    # showMessage darf nur an genau einer Stelle stehen: in der Hilfsfunktion
    # selbst. Jeder weitere Aufruf umgeht das Ausblenden des Projekt-Labels.
    assert source.count("().showMessage(") == 1, (
        "showMessage() wird ausserhalb von _show_status_message() aufgerufen; "
        "dort fehlt das Ausblenden des Projekt-Labels, wodurch sich Botschaft "
        "und Label im Screenshot ueberlagern."
    )
