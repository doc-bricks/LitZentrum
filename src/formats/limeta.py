"""
LitZentrum - LiMeta Format (.limeta)
Metadaten für Literaturquellen
"""
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .base import LitFormat, now_iso, to_optional_int, to_optional_year


@dataclass
class LiMeta(LitFormat):
    """Metadaten einer Literaturquelle"""
    
    FILE_EXTENSION = ".limeta"
    SCHEMA_FILE = "limeta.schema.json"
    
    # Pflichtfelder
    title: str
    
    # Optionale Felder
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    doi: Optional[str] = None
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    abstract: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    source_file: Optional[str] = None
    source_type: str = "article"
    metadata_source: str = "manual"
    verified: bool = False
    url: Optional[str] = None
    language: str = "de"
    
    # System-Felder
    schema_version: str = "1.0.0"
    created_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)
    
    def to_dict(self) -> dict:
        """Konvertiert zu Dictionary"""
        return {
            "schema_version": self.schema_version,
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "doi": self.doi,
            "isbn": self.isbn,
            "publisher": self.publisher,
            "journal": self.journal,
            "volume": self.volume,
            "issue": self.issue,
            "pages": self.pages,
            "abstract": self.abstract,
            "tags": self.tags,
            "source_file": self.source_file,
            "source_type": self.source_type,
            "metadata_source": self.metadata_source,
            "verified": self.verified,
            "url": self.url,
            "language": self.language,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "LiMeta":
        """Erstellt aus Dictionary"""
        return cls(
            title=data.get("title") or "Untitled",
            authors=data.get("authors") or [],
            year=to_optional_year(data.get("year")),
            doi=data.get("doi"),
            isbn=data.get("isbn"),
            publisher=data.get("publisher"),
            journal=data.get("journal"),
            volume=data.get("volume"),
            issue=data.get("issue"),
            pages=data.get("pages"),
            abstract=data.get("abstract"),
            tags=data.get("tags") or [],
            source_file=data.get("source_file"),
            source_type=data.get("source_type", "article"),
            metadata_source=data.get("metadata_source", "manual"),
            verified=data.get("verified", False),
            url=data.get("url"),
            language=data.get("language", "de"),
            schema_version=data.get("schema_version", "1.0.0"),
            created_at=data.get("created_at", now_iso()),
            updated_at=data.get("updated_at", now_iso()),
        )
    
    def update(self):
        """Aktualisiert updated_at Zeitstempel"""
        self.updated_at = now_iso()
    
    @property
    def first_author(self) -> str:
        """Gibt den ersten Autor zurück"""
        if self.authors:
            return self.authors[0].split(",")[0]
        return "Unbekannt"
    
    @property
    def citation_key(self) -> str:
        """Generiert einen Zitations-Schlüssel (z.B. 'Smith2023')"""
        author = self.first_author.replace(" ", "")
        year = str(self.year) if self.year else "oJ"
        return f"{author}{year}"

    @property
    def bibtex_key(self) -> str:
        """Generiert einen BibTeX-Key (z.B. 'mueller_2023_quantenphysik').

        Format: nachname_jahr_erstesWortDesTitels (ASCII, lowercase).
        Umlaute werden transliteriert (ae, oe, ue, ss).
        """
        # Nachname: erster Autor, Nachname-Teil
        author_raw = self.first_author if self.authors else "unknown"
        # Umlaute manuell ersetzen (vor NFKD, da NFKD ae/oe/ue nicht erzeugt)
        umlaut_map = {
            "ae": "ae", "oe": "oe", "ue": "ue", "ss": "ss",
            "\u00e4": "ae", "\u00f6": "oe", "\u00fc": "ue", "\u00df": "ss",
            "\u00c4": "Ae", "\u00d6": "Oe", "\u00dc": "Ue",
        }
        def _to_ascii(text: str) -> str:
            for char, repl in umlaut_map.items():
                text = text.replace(char, repl)
            # Restliche diakritische Zeichen via NFKD entfernen
            text = unicodedata.normalize("NFKD", text)
            text = text.encode("ascii", "ignore").decode("ascii")
            return text

        author_ascii = _to_ascii(author_raw).lower().strip()
        # Nur Buchstaben behalten
        author_ascii = re.sub(r"[^a-z]", "", author_ascii)
        if not author_ascii:
            author_ascii = "unknown"

        # Jahr
        year_part = str(self.year) if self.year else "oJ"

        # Erstes signifikantes Wort des Titels (Stoppwoerter ueberspringen)
        stopwords = {
            "der", "die", "das", "ein", "eine", "the", "a", "an",
            "und", "or", "and", "in", "im", "on", "of", "zu", "zur",
            "zum", "fuer", "for", "von", "with", "mit", "ueber",
        }
        title_ascii = _to_ascii(self.title).lower()
        words = re.findall(r"[a-z]+", title_ascii)
        first_word = "untitled"
        for w in words:
            if w not in stopwords:
                first_word = w
                break

        return f"{author_ascii}_{year_part}_{first_word}"
    
    def __str__(self) -> str:
        authors_str = ", ".join(self.authors[:2])
        if len(self.authors) > 2:
            authors_str += " et al."
        year_str = f" ({self.year})" if self.year else ""
        return f"{authors_str}{year_str}: {self.title}"
