"""
LitZentrum - BibTeX Generator
Generiert BibTeX-Einträge aus LiMeta
"""
from pathlib import Path
from typing import List
import logging

from formats import LiMeta


class BibTeXGenerator:
    """Generiert BibTeX-Einträge"""
    
    TYPE_MAP = {
        "article": "article",
        "book": "book",
        "chapter": "inbook",
        "thesis": "phdthesis",
        "conference": "inproceedings",
        "website": "misc",
        "other": "misc",
    }
    
    def generate_entry(self, meta: LiMeta) -> str:
        """Generiert einen BibTeX-Eintrag"""
        entry_type = self.TYPE_MAP.get(meta.source_type, "misc")
        key = meta.citation_key
        
        lines = [f"@{entry_type}{{{key},"]
        
        # Titel
        if meta.title:
            lines.append(f'  title = {{{meta.title}}},')
        
        # Autoren
        if meta.authors:
            authors = " and ".join(meta.authors)
            lines.append(f'  author = {{{authors}}},')
        
        # Jahr
        if meta.year:
            lines.append(f'  year = {{{meta.year}}},')
        
        # Journal (für Artikel)
        if meta.journal:
            lines.append(f'  journal = {{{meta.journal}}},')
        
        # Volume
        if meta.volume:
            lines.append(f'  volume = {{{meta.volume}}},')
        
        # Number/Issue
        if meta.issue:
            lines.append(f'  number = {{{meta.issue}}},')
        
        # Seiten
        if meta.pages:
            lines.append(f'  pages = {{{meta.pages}}},')
        
        # Verlag
        if meta.publisher:
            lines.append(f'  publisher = {{{meta.publisher}}},')
        
        # DOI
        if meta.doi:
            lines.append(f'  doi = {{{meta.doi}}},')
        
        # ISBN
        if meta.isbn:
            lines.append(f'  isbn = {{{meta.isbn}}},')
        
        # URL
        if meta.url:
            lines.append(f'  url = {{{meta.url}}},')
        
        # Abstract
        if meta.abstract:
            abstract = meta.abstract.replace("\n", " ")
            lines.append(f'  abstract = {{{abstract}}},')
        
        # Schließende Klammer
        lines.append("}")
        
        return "\n".join(lines)
    
    def generate_bibliography(self, sources: List[LiMeta]) -> str:
        """Generiert komplette Bibliografie"""
        entries = [self.generate_entry(meta) for meta in sources]
        return "\n\n".join(entries)
    
    def save_bibliography(self, sources: List[LiMeta], path: Path):
        """Speichert Bibliografie als .bib Datei"""
        content = self.generate_bibliography(sources)
        
        path = Path(path)
        if not path.suffix:
            path = path.with_suffix(".bib")

        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)


class BibTeXParser:
    """Parst BibTeX-Dateien"""
    
    def parse_file(self, path: Path) -> List[LiMeta]:
        """Parst eine BibTeX-Datei"""
        import bibtexparser
        
        with open(path, 'r', encoding='utf-8') as f:
            bib_database = bibtexparser.load(f)
        
        sources = []
        for entry in bib_database.entries:
            meta = self._entry_to_meta(entry)
            sources.append(meta)
        
        return sources
    
    def _entry_to_meta(self, entry: dict) -> LiMeta:
        """Konvertiert BibTeX-Eintrag zu LiMeta"""
        # Typ-Mapping umgekehrt
        type_map = {
            "article": "article",
            "book": "book",
            "inbook": "chapter",
            "incollection": "chapter",
            "phdthesis": "thesis",
            "mastersthesis": "thesis",
            "inproceedings": "conference",
            "misc": "other",
        }
        
        entry_type = entry.get("ENTRYTYPE", "misc")
        source_type = type_map.get(entry_type, "other")
        
        # Autoren parsen
        authors_str = entry.get("author", "")
        authors = [a.strip() for a in authors_str.split(" and ") if a.strip()]
        
        # Jahr
        year_str = entry.get("year", "")
        try:
            year = int(year_str)
        except (ValueError, TypeError) as e:
            logging.debug(f"Fehler beim Parsen des Jahres '{year_str}': {e}")
            year = None
        
        return LiMeta(
            title=entry.get("title", "Untitled"),
            authors=authors,
            year=year,
            source_type=source_type,
            journal=entry.get("journal"),
            volume=entry.get("volume"),
            issue=entry.get("number"),
            pages=entry.get("pages"),
            publisher=entry.get("publisher"),
            doi=entry.get("doi"),
            isbn=entry.get("isbn"),
            url=entry.get("url"),
            abstract=entry.get("abstract"),
            metadata_source="bibtex_import",
        )
