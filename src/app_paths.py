"""
LitZentrum - Resolves the application's base directory for bundled resources
(schemas/, resources/icons/) so paths work both from source and from a
PyInstaller-frozen onefile build.

Source-Layout:  <repo_root>/src/{main.py,core/,formats/,...}
Frozen-Layout:  <_MEIPASS>/{main.py,core/,formats/,...}  (kein extra "src/")

Ein einzelnes gemeinsames Verzeichnis, relativ zu dem "schemas/" und
"resources/" beide Male auf demselben Weg gefunden werden, macht die
Unterscheidung fuer alle Aufrufer einheitlich statt an jeder Stelle die
Anzahl der `.parent`-Sprünge neu zu erraten.
"""
from __future__ import annotations

import sys
from pathlib import Path


def base_dir() -> Path:
    """Directory that contains schemas/ and resources/, in both run modes."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    # Source-Modus: diese Datei liegt in <repo_root>/src/app_paths.py
    return Path(__file__).resolve().parent.parent
