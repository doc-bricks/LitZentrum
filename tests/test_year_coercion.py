# -*- coding: utf-8 -*-
"""Regressionstests year-Coercion (Bugsweep 2026-06-23, CAVEAT limeta.py).

Verifiziert das Verhalten von to_optional_year (base.py) und die
Integration ueber LiMeta.from_dict fuer alle relevanten Edge-Cases:

- None, leerer String       -> None
- "n.d.", "o.J.", "s.d."   -> None  (kein-Datum-Marker)
- "2023", 2023, 2023.0     -> 2023  (normale Faelle)
- "2023.0" (Float-String)  -> 2023  (der fixte Gap: frueher None)
- "2023a" (Disambiguierung)-> None  (defensive Konvertierung; CAVEAT bleibt offen)
- "invalid", "abc"         -> None

Hintergrund: to_optional_int konnte keine Float-Strings konvertieren
("2023.0" -> ValueError -> None). to_optional_year loest das mit einem
int(float(s))-Fallback ohne die gemeinsam genutzte to_optional_int fuer
page/page_end-Felder zu aendern.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# ---------------------------------------------------------------------------
# to_optional_year direkt
# ---------------------------------------------------------------------------

def test_year_none_returns_none():
    from formats.base import to_optional_year
    assert to_optional_year(None) is None


def test_year_empty_string_returns_none():
    from formats.base import to_optional_year
    assert to_optional_year("") is None


def test_year_string_int_converts():
    from formats.base import to_optional_year
    assert to_optional_year("2023") == 2023


def test_year_native_int_converts():
    from formats.base import to_optional_year
    assert to_optional_year(2023) == 2023


def test_year_native_float_converts():
    from formats.base import to_optional_year
    assert to_optional_year(2023.0) == 2023


def test_year_float_string_converts():
    """Fixte Luecke: 'to_optional_int' konnte '2023.0' nicht -> None."""
    from formats.base import to_optional_year
    assert to_optional_year("2023.0") == 2023


def test_year_nd_marker_returns_none():
    from formats.base import to_optional_year
    assert to_optional_year("n.d.") is None


def test_year_oj_marker_returns_none():
    from formats.base import to_optional_year
    assert to_optional_year("o.J.") is None


def test_year_sd_marker_returns_none():
    from formats.base import to_optional_year
    assert to_optional_year("s.d.") is None


def test_year_generic_string_returns_none():
    from formats.base import to_optional_year
    assert to_optional_year("invalid") is None


def test_year_abc_returns_none():
    from formats.base import to_optional_year
    assert to_optional_year("abc") is None


def test_year_disambiguation_suffix_returns_none():
    """Defensiv: '2023a' -> None (kein verifizierter Bedarf; CAVEAT bleibt offen).

    Solange kein Produzent/Konsument fuer Disambiguierungs-Jahre identifiziert
    wurde, bleibt None die sichere Konvention.
    """
    from formats.base import to_optional_year
    assert to_optional_year("2023a") is None


def test_year_mixed_alpha_returns_none():
    from formats.base import to_optional_year
    assert to_optional_year("nicht-zahl") is None


# ---------------------------------------------------------------------------
# Integration: LiMeta.from_dict
# ---------------------------------------------------------------------------

def test_limeta_from_dict_year_string():
    from formats import LiMeta
    meta = LiMeta.from_dict({"title": "T", "year": "2023"})
    assert meta.year == 2023


def test_limeta_from_dict_year_float_string():
    """Regression fuer den Float-String-Gap."""
    from formats import LiMeta
    meta = LiMeta.from_dict({"title": "T", "year": "2023.0"})
    assert meta.year == 2023


def test_limeta_from_dict_year_nd():
    from formats import LiMeta
    meta = LiMeta.from_dict({"title": "T", "year": "n.d."})
    assert meta.year is None


def test_limeta_from_dict_year_none():
    from formats import LiMeta
    meta = LiMeta.from_dict({"title": "T", "year": None})
    assert meta.year is None


def test_limeta_from_dict_year_empty():
    from formats import LiMeta
    meta = LiMeta.from_dict({"title": "T", "year": ""})
    assert meta.year is None


def test_limeta_from_dict_year_disambiguation_stays_none():
    """Defensiv: '2023a' -> None; bestehender CAVEAT-Eintrag bleibt offen."""
    from formats import LiMeta
    meta = LiMeta.from_dict({"title": "T", "year": "2023a"})
    assert meta.year is None


def test_limeta_from_dict_year_native_int():
    from formats import LiMeta
    meta = LiMeta.from_dict({"title": "T", "year": 2023})
    assert meta.year == 2023


def test_limeta_from_dict_year_invalid_string():
    from formats import LiMeta
    meta = LiMeta.from_dict({"title": "T", "year": "nicht-zahl"})
    assert meta.year is None
