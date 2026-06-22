# -*- coding: utf-8 -*-
"""Regressionstests — LitZentrum Desktop-Re-Sweep 2026-06-22 (Bugsweep-Loop-Lauf 27).

formats/core importierbar (src/ auf sys.path) -> echte Tests; Rest statisch.
Red-on-revert: LZ_SRC -> PRE-Backup-src-Verzeichnis.

  B1/B2 None-Listen: data.get(k, []) -> data.get(k) or [] (JSON null bricht sonst Iteration).
  B4 Task.is_overdue: ungueltiges/tz-aware due_date -> kein Crash.
  B5 base.save atomar; B6 base.load from_dict in try.
  A6 source_manager _generate_folder_name: first_author None.  A7 _on_add_source try/except.
"""
import os
import sys
import tempfile
from pathlib import Path

_PROJ = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, str(_PROJ / "src"))

_SRC = Path(os.environ.get("LZ_SRC", _PROJ / "src"))


def read(rel):
    return (_SRC / rel).read_text(encoding="utf-8")


def has(rel, n):
    return n in read(rel)


# --- echte Tests ---
def test_b1_litask_null_list_loads():
    from formats.litask import LiTask
    obj = LiTask.from_dict({"tasks": None})  # JSON null -> vor Fix: TypeError
    assert obj.tasks == []


def test_b2_task_null_tags():
    from formats.litask import Task
    t = Task.from_dict({"id": "t1", "title": "X", "tags": None})
    assert t.tags == []


def test_b4_is_overdue_bad_and_tzaware_date():
    from formats.litask import Task
    t1 = Task.from_dict({"id": "a", "title": "A", "status": "open", "due_date": "kein-datum"})
    assert t1.is_overdue is False  # ungueltiges Datum -> kein Crash
    t2 = Task.from_dict({"id": "b", "title": "B", "status": "open", "due_date": "2020-01-01T00:00:00+02:00"})
    assert isinstance(t2.is_overdue, bool)  # tz-aware -> kein naive/aware-TypeError


def test_b5_base_save_atomic(tmp_path):
    from formats.litask import LiTask
    obj = LiTask.from_dict({"tasks": []})
    p = tmp_path / "x.litask"
    obj.save(p)
    assert p.exists()
    assert not (tmp_path / "x.litask.tmp").exists()
    assert LiTask.load(p).tasks == []  # roundtrip


# --- statische Assertions (red-on-revert) ---
def test_b1b2_no_bare_list_default():
    import re
    for fmt in ("litask.py", "lisum.py", "liquote.py", "linote.py", "limeta.py"):
        src = read(f"formats/{fmt}")
        assert not re.search(r'\.get\(\s*"[^"]+"\s*,\s*\[\]\s*\)', src), f"{fmt}: bare get(...,[]) noch da"
        assert ") or []" in src, f"{fmt}: None-sicheres or [] fehlt"


def test_b5_base_atomic_static():
    assert has("formats/base.py", "tmp.replace(path)") and has("formats/base.py", '+ ".tmp"'), "base atomar fehlt"


def test_b6_base_from_dict_wrapped():
    assert has("formats/base.py", "Datei konnte nicht interpretiert werden"), "base from_dict-try fehlt"


def test_a6_source_first_author_guard():
    assert has("core/source_manager.py", 'str(meta.first_author or "")'), "first_author-Guard fehlt"


def test_a7_add_source_try_except():
    assert has("gui/main_window.py", "Quelle konnte nicht erstellt werden"), "_on_add_source try/except fehlt"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
