from __future__ import annotations

import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read_version_from_main() -> str:
    content = (PROJECT_ROOT / "src" / "main.py").read_text(encoding="utf-8")
    match = re.search(r'app\.setApplicationVersion\("([^"]+)"\)', content)
    assert match is not None
    return match.group(1)


def test_store_package_matches_project_metadata() -> None:
    package = json.loads((PROJECT_ROOT / "store_package.json").read_text(encoding="utf-8"))

    assert package["app_name"] == "LitZentrum"
    assert package["identity_name"] == "Geiger.LitZentrum"
    assert package["executable"] == "LitZentrum.exe"
    assert package["capabilities"] == "runFullTrust"
    assert package["category"] == "Productivity"
    assert package["license"] == "AGPL-3.0-only"
    assert package["version"] == f"{_read_version_from_main()}.0"
    assert package["privacy_url"].endswith("/PRIVACY_POLICY.md")
    assert package["support_url"].endswith("/SUPPORT.md")


def test_store_documents_exist_and_reference_public_paths() -> None:
    listing = (PROJECT_ROOT / "STORE_LISTING.md").read_text(encoding="utf-8")
    support = (PROJECT_ROOT / "SUPPORT.md").read_text(encoding="utf-8")
    prep = (PROJECT_ROOT / "WINDOWS_STORE_PREP.md").read_text(encoding="utf-8")
    build = (PROJECT_ROOT / "releases" / "windowsstore" / "BUILD.md").read_text(encoding="utf-8")
    wack = (PROJECT_ROOT / "releases" / "windowsstore" / "WACK_PROTOCOL.md").read_text(encoding="utf-8")
    screenshot_note = (PROJECT_ROOT / "README" / "screenshots" / "store" / "README.md").read_text(
        encoding="utf-8"
    )

    assert "https://github.com/doc-bricks/LitZentrum/blob/master/PRIVACY_POLICY.md" in listing
    assert "https://github.com/doc-bricks/LitZentrum/blob/master/SUPPORT.md" in listing
    assert "https://github.com/doc-bricks/LitZentrum/issues" in support
    assert "MSIX" in prep
    assert "build_store_release.ps1" in build
    assert "WACK" in wack
    assert "main.png" in screenshot_note
    assert "quotes-workflow.png" in screenshot_note
    assert "bibtex-export.png" in screenshot_note
    assert "companion-export.png" in screenshot_note


def test_existing_main_screenshot_is_present() -> None:
    main_screenshot = PROJECT_ROOT / "README" / "screenshots" / "main.png"
    assert main_screenshot.exists()


def test_store_screenshot_targets_are_present() -> None:
    screenshot_dir = PROJECT_ROOT / "README" / "screenshots" / "store"
    assert (screenshot_dir / "main.png").exists()
    assert (screenshot_dir / "quotes-workflow.png").exists()
    assert (screenshot_dir / "bibtex-export.png").exists()
    assert (screenshot_dir / "companion-export.png").exists()
    assert (screenshot_dir / "summary.json").exists()


def test_store_assets_are_present() -> None:
    store_assets = PROJECT_ROOT / "store_assets"
    assert (store_assets / "Square44x44Logo.png").exists()
    assert (store_assets / "Square150x150Logo.png").exists()
    assert (store_assets / "Square310x310Logo.png").exists()
    assert (store_assets / "Wide310x150Logo.png").exists()
