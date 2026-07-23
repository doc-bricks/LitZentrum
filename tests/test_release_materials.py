from __future__ import annotations

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read_version_from_main() -> str:
    content = (PROJECT_ROOT / "src" / "main.py").read_text(encoding="utf-8")
    match = re.search(r'app\.setApplicationVersion\("([^"]+)"\)', content)
    assert match is not None
    return match.group(1)


def test_build_exe_bat_uses_local_build_root_and_scanner() -> None:
    content = (PROJECT_ROOT / "build_exe.bat").read_text(encoding="utf-8")
    version = _read_version_from_main()

    assert r"C:\_Local_DEV\codex_build\litzentrum" in content
    assert "build_exclude_scanner.py" in content
    assert "--onefile" in content
    assert r"resources\icons\litzentrum.ico" in content
    assert f'set "VERSION={version}"' in content
    assert r'releases\v%VERSION%' in content
    assert r'%APP_NAME%-%VERSION%-win64.exe' in content


def test_readmes_document_direct_windows_exe_build() -> None:
    readme_en = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (PROJECT_ROOT / "README_de.md").read_text(encoding="utf-8")
    version = _read_version_from_main()

    assert "build_exe.bat" in readme_en
    assert "build_exe.bat" in readme_de
    assert f"LitZentrum-{version}-win64.exe" in readme_en
    assert f"LitZentrum-{version}-win64.exe" in readme_de


def test_gitignore_covers_internal_task_variants() -> None:
    content = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")

    assert "AUFGABEN-*.txt" in content
    assert "LOCK*.txt" in content
