"""
LitZentrum - BibTeX Generator
Erstellt BibTeX-Einträge aus LiMeta-Objekten
"""
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from formats import LiMeta


class BibTeXGenerator:
    """Generiert BibTeX-Dateien aus Metadaten"""
    
    TYPE_MAP = {
        "article": "article",
        "book": "book",
        "chapter": "inbook",
        "thesis": "phdthesis",
        "conference": "inproceedings",
        "website": "online",
        "other": "misc",
    }
    
    def __init__(self):
        self.entries: List[str] = []
    
    def add_entry(self, meta: LiMeta) -> str:
        """Fügt einen BibTeX-Eintrag hinzu"""
        entry = self._generate_entry(meta)
        self.entries.append(entry)
        return entry
    
    def _generate_entry(self, meta: LiMeta) -> str:
        """Generiert einen einzelnen BibTeX-Eintrag"""
        bib_type = self.TYPE_MAP.get(meta.source_type, "misc")
        key = meta.bibtex_key
        
        lines = [f"@{bib_type}{{{key},"]
        
        # Titel
        if meta.title:
            lines.append(f"  title = {{{meta.title}}},")
        
        # Autoren
        if meta.authors:
            authors_str = " and ".join(meta.authors)
            lines.append(f"  author = {{{authors_str}}},")
        
        # Jahr
        if meta.year:
            lines.append(f"  year = {{{meta.year}}},")
        
        # Journal/Booktitle
        if meta.journal:
            if bib_type == "article":
                lines.append(f"  journal = {{{meta.journal}}},")
            else:
                lines.append(f"  booktitle = {{{meta.journal}}},")
        
        # Volume
        if meta.volume:
            lines.append(f"  volume = {{{meta.volume}}},")
        
        # Number/Issue
        if meta.issue:
            lines.append(f"  number = {{{meta.issue}}},")
        
        # Pages
        if meta.pages:
            lines.append(f"  pages = {{{meta.pages}}},")
        
        # Publisher
        if meta.publisher:
            lines.append(f"  publisher = {{{meta.publisher}}},")
        
        # DOI
        if meta.doi:
            lines.append(f"  doi = {{{meta.doi}}},")
        
        # ISBN
        if meta.isbn:
            lines.append(f"  isbn = {{{meta.isbn}}},")
        
        # URL
        if meta.url:
            lines.append(f"  url = {{{meta.url}}},")
        
        # Abstract
        if meta.abstract:
            abstract = meta.abstract.replace("\n", " ")
            lines.append(f"  abstract = {{{abstract}}},")
        
        # Keywords/Tags
        if meta.tags:
            keywords = ", ".join(meta.tags)
            lines.append(f"  keywords = {{{keywords}}},")
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def generate_file(self, sources: List[LiMeta], output_path: Path) -> Path:
        """Generiert BibTeX-Datei für mehrere Quellen"""
        self.entries = []
        
        for meta in sources:
            self.add_entry(meta)
        
        content = self._generate_header() + "\n\n" + "\n\n".join(self.entries)
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path
    
    def _generate_header(self) -> str:
        """Generiert BibTeX-Header"""
        return f"""% LitZentrum BibTeX Export
% Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
% Entries: {len(self.entries)}
"""
    
    def get_bibtex_string(self) -> str:
        """Gibt alle Einträge als String zurück"""
        return self._generate_header() + "\n\n" + "\n\n".join(self.entries)
