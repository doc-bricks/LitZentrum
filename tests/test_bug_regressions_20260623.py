# -*- coding: utf-8 -*-
"""Regressionstests Bugsweep 2026-06-23 (Desktop, /bugsweep-Loop Run 14/15).

Vier echte Bugs, die der vorherige Sweep (Bugsweep 27) nicht erfasst hatte:

1. bibtex.py: BibTeX-Feldwerte ohne Escaping von & % _ # { } -> unkompilierbares BibTeX.
2. liquote.py: page_range lieferte "None-10" wenn page None aber page_end gesetzt;
   ausserdem int-Felder ohne Konvertierung -> "10" <= 7 TypeError in get_by_page.
3. sync/__init__.py: restore_backup ohne Rollback -> Live-Projekt-Verlust bei copytree-Fehler.
4. source_manager.py (Hardening): search_sources ohne None-Guard fuer title/authors/tags.
"""
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# --- Bug 1: BibTeX-Escaping -------------------------------------------------

def test_bibtex_escapes_special_chars():
    from formats import LiMeta
    from modules.bibliography.bibtex import BibTeXGenerator

    meta = LiMeta(
        title="AT&T cost_analysis 10% #1",
        authors=["Müller, A&B"],
        year=2024,
        publisher="O'Reilly & Co_Ltd",
    )
    entry = BibTeXGenerator().generate_entry(meta)
    # Vor dem Fix standen &, _, %, # roh im Output -> unkompilierbar.
    assert r"\&" in entry
    assert r"\_" in entry
    assert r"\%" in entry
    assert r"\#" in entry
    # Kein roh stehendes ungeescaptes & mehr im Titel-/Autoren-/Verlagsfeld:
    assert "AT&T" not in entry  # muss "AT\&T" sein
    assert "cost_analysis" not in entry  # muss "cost\_analysis" sein


def test_bibtex_entry_key_uses_existing_sanitized_key():
    from formats import LiMeta
    from modules.bibliography.bibtex import BibTeXGenerator

    meta = LiMeta(
        title="Research Platforms",
        authors=["O'Brien Labs"],
        year=2024,
    )
    entry = BibTeXGenerator().generate_entry(meta)

    assert entry.startswith("@article{obrienlabs_2024_research,")
    assert "@article{O'Brien2024," not in entry


def test_legacy_bibtex_file_generator_uses_sanitized_key(tmp_path):
    from formats import LiMeta
    from modules.bibliography.bibtex_generator import BibTeXGenerator

    meta = LiMeta(
        title="Research Platforms",
        authors=["AT&T Research"],
        year=2024,
    )
    output = tmp_path / "refs.bib"

    BibTeXGenerator().generate_file([meta], output)

    content = output.read_text(encoding="utf-8")
    assert "@article{attresearch_2024_research," in content
    assert "@article{AT&T2024," not in content


def test_legacy_bibtex_generator_escapes_field_values(tmp_path):
    """Bugsweep Run 74: bibtex_generator.py escapte Feldwerte nicht (nur bibtex.py tat es).

    Sonderzeichen wie & % _ # in Titeln/Autoren/Verlagen erzeugten in bibtex_generator.py
    unkompilierbares BibTeX. Fix: escape_bibtex aus bibtex.py importiert und auf alle
    Freitextfelder (titel, autoren, journal, publisher, abstract, keywords) angewendet.
    URL/DOI/ISBN bleiben verbatim (Escaping wuerde hyperref-Verlinkung brechen).
    """
    from formats import LiMeta
    from modules.bibliography.bibtex_generator import BibTeXGenerator

    meta = LiMeta(
        title="AT&T cost_analysis 10% #1",
        authors=["Müller, A&B"],
        year=2024,
        publisher="O'Reilly & Co_Ltd",
        abstract="Enthält & Sonderzeichen_hier.",
        tags=["tag_one", "tag&two"],
        url="https://example.org/?a=1&b=2",
        doi="10.1000/abc_def",
    )
    output = tmp_path / "refs.bib"
    BibTeXGenerator().generate_file([meta], output)
    content = output.read_text(encoding="utf-8")

    # Freitextfelder muessen escaped sein.
    assert r"\&" in content
    assert r"\_" in content
    assert r"\%" in content
    assert r"\#" in content
    assert "AT&T" not in content        # Titel: muss "AT\&T" sein
    assert "cost_analysis" not in content  # Titel: muss "cost\_analysis" sein
    assert "A&B" not in content         # Autor
    assert "O'Reilly & Co_Ltd" not in content  # Publisher: & und _ escaped

    # URL und DOI bleiben verbatim.
    assert "https://example.org/?a=1&b=2" in content
    assert "10.1000/abc_def" in content


def test_bibtex_url_and_doi_not_escaped():
    from formats import LiMeta
    from modules.bibliography.bibtex import BibTeXGenerator

    meta = LiMeta(
        title="Test",
        authors=["Doe, J"],
        year=2024,
        url="https://example.org/path?a=1&b=2#frag",
        doi="10.1000/abc_def",
    )
    entry = BibTeXGenerator().generate_entry(meta)
    # url/doi muessen verbatim bleiben (Escapen wuerde \url/hyperref brechen).
    assert "https://example.org/path?a=1&b=2#frag" in entry
    assert "10.1000/abc_def" in entry


def test_bibtex_backslash_roundtrip():
    from formats import LiMeta
    from modules.bibliography.bibtex import escape_bibtex

    # Backslash darf nicht durch die nachfolgende Klammer-Escapierung zerstoert werden.
    assert escape_bibtex(r"a\b") == r"a\textbackslash{}b"
    assert escape_bibtex("x{y}z") == r"x\{y\}z"


# --- Bug 2: liquote page_range + int-Konvertierung --------------------------

def test_quote_page_range_no_none_string():
    from formats.liquote import Quote

    q = Quote(id="q1", text="t", created_at="2024", page=None, page_end=10)
    # Vor dem Fix: "None-10". Erwartet: leerer String (kein gueltiger Bereich).
    assert q.page_range == ""

    q2 = Quote(id="q2", text="t", created_at="2024", page=5, page_end=10)
    assert q2.page_range == "5-10"

    q3 = Quote(id="q3", text="t", created_at="2024", page=7, page_end=None)
    assert q3.page_range == "7"


def test_liquote_int_coercion_from_dict():
    from formats.liquote import LiQuote

    # Alte/handeditierte Datei mit String-Seitenzahlen.
    data = {"quotes": [{"id": "q1", "text": "zitat", "page": "10", "page_end": "12"}]}
    lq = LiQuote.from_dict(data)
    assert lq.quotes[0].page == 10
    assert lq.quotes[0].page_end == 12
    # Vor dem Fix crashte dieser Vergleich mit TypeError ("10" <= 11).
    hits = lq.get_by_page(11)
    assert hits and hits[0].id == "q1"


def test_limeta_year_coercion_from_dict():
    from formats import LiMeta

    meta = LiMeta.from_dict({"title": "T", "year": "2023"})
    assert meta.year == 2023
    meta_bad = LiMeta.from_dict({"title": "T", "year": "nicht-zahl"})
    assert meta_bad.year is None


# --- Bug 3: sync restore_backup Rollback ------------------------------------

def test_restore_backup_keeps_live_project_on_copytree_failure(tmp_path, monkeypatch):
    from modules.sync import BackupManager

    project = tmp_path / "projekt"
    project.mkdir()
    (project / "wichtig.txt").write_text("LIVE-DATEN", encoding="utf-8")

    backup = tmp_path / "backup_quelle"
    backup.mkdir()
    (backup / "wichtig.txt").write_text("BACKUP-DATEN", encoding="utf-8")

    mgr = BackupManager(project)

    # copytree (Staging-Schritt) schlaegt fehl.
    def boom(*args, **kwargs):
        raise OSError("Disk voll")

    monkeypatch.setattr(shutil, "copytree", boom)

    ok = mgr.restore_backup(backup)
    assert ok is False
    # Kritisch: Live-Projekt muss unangetastet und mit Originalinhalt vorhanden sein.
    assert project.exists()
    assert (project / "wichtig.txt").read_text(encoding="utf-8") == "LIVE-DATEN"


def test_restore_backup_success(tmp_path):
    from modules.sync import BackupManager

    project = tmp_path / "projekt"
    project.mkdir()
    (project / "wichtig.txt").write_text("LIVE-DATEN", encoding="utf-8")

    backup = tmp_path / "backup_quelle"
    backup.mkdir()
    (backup / "wichtig.txt").write_text("BACKUP-DATEN", encoding="utf-8")

    mgr = BackupManager(project)
    ok = mgr.restore_backup(backup)
    assert ok is True
    assert (project / "wichtig.txt").read_text(encoding="utf-8") == "BACKUP-DATEN"
    # Keine Staging-/Temp-Reste.
    assert not (tmp_path / "projekt_restore_staging").exists()
    assert not (tmp_path / "projekt_before_restore").exists()


# --- Bug 4: source_manager None-Hardening -----------------------------------

def test_search_sources_handles_none_title(tmp_path):
    from formats import LiMeta
    from core.source_manager import SourceManager, LitSource

    mgr = SourceManager(tmp_path, "quellen")

    # Programmatisch erzeugte Quelle mit None-Title/-Authors/-Tags.
    meta = LiMeta(title="Brauchbar")
    meta.title = None
    meta.authors = None
    meta.tags = None
    src = LitSource(path=tmp_path / "s1", meta=meta)

    # get_all_sources direkt ueberschreiben -> Logik mit None-Feldern pruefen.
    mgr.get_all_sources = lambda: [src]  # type: ignore
    # Darf nicht crashen (vor dem Fix: AttributeError bei None.lower()):
    assert mgr.search_sources("xyz") == []
