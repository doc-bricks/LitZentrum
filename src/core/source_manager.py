"""
LitZentrum - Source Manager.
Manages individual literature sources.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import shutil
import re

from formats import LiMeta, LiNote, LiQuote, LiTask, LiSum


@dataclass
class LitSource:
    """Represents a single literature source."""
    path: Path
    meta: LiMeta
    
    @property
    def name(self) -> str:
        return self.path.name
    
    @property
    def pdf_path(self) -> Optional[Path]:
        """Returns the path to the source PDF, or None if no PDF is associated."""
        if self.meta.source_file:
            return self.path / self.meta.source_file
        # Suche nach PDF
        pdfs = list(self.path.glob("*.pdf"))
        return pdfs[0] if pdfs else None
    
    @property
    def has_pdf(self) -> bool:
        pdf = self.pdf_path
        return pdf is not None and pdf.exists()
    
    @property
    def notes_path(self) -> Path:
        return self.path / "notes.linote"
    
    @property
    def quotes_path(self) -> Path:
        return self.path / "quotes.liquote"
    
    @property
    def tasks_path(self) -> Path:
        return self.path / "tasks.litask"
    
    @property
    def summaries_path(self) -> Path:
        return self.path / "summaries.lisum"


class SourceManager:
    """Manages literature sources."""
    
    META_FILE = "meta.limeta"
    
    def __init__(self, project_path: Path = None, sources_folder: str = "Quellen"):
        self.project_path = Path(project_path) if project_path else None
        self.sources_folder = sources_folder
    
    @property
    def sources_path(self) -> Optional[Path]:
        if self.project_path:
            return self.project_path / self.sources_folder
        return None
    
    def create_source(self, meta: LiMeta, pdf_path: Path = None) -> LitSource:
        """Creates a new source directory with metadata and empty data files.

        Args:
            meta: Metadata for the new source.
            pdf_path: Optional path to a PDF to copy into the source folder.

        Returns:
            The newly created LitSource instance.

        Raises:
            ValueError: If no project path has been set on this manager.
        """
        if not self.sources_path:
            raise ValueError("Kein Projekt-Pfad gesetzt")
        
        # Ordnername generieren
        folder_name = self._generate_folder_name(meta)
        source_path = self._get_unique_source_path(folder_name)
        source_path.mkdir(parents=True, exist_ok=False)
        
        # PDF kopieren
        if pdf_path and Path(pdf_path).exists():
            pdf_dest = source_path / Path(pdf_path).name
            shutil.copy2(pdf_path, pdf_dest)
            meta.source_file = pdf_dest.name
        
        # Metadaten speichern
        meta.save(source_path / self.META_FILE)
        
        # Leere Dateien erstellen
        LiNote().save(source_path / "notes.linote")
        LiQuote().save(source_path / "quotes.liquote")
        LiTask().save(source_path / "tasks.litask")
        LiSum().save(source_path / "summaries.lisum")
        
        return LitSource(path=source_path, meta=meta)
    
    def load_source(self, path: Path) -> LitSource:
        """Loads an existing source from a directory.

        Args:
            path: Source directory containing a meta.limeta file.

        Returns:
            The loaded LitSource instance.

        Raises:
            FileNotFoundError: If no metadata file is found in the directory.
        """
        path = Path(path)
        meta_path = path / self.META_FILE
        
        if not meta_path.exists():
            raise FileNotFoundError(f"Keine Metadaten in: {path}")
        
        meta = LiMeta.load(meta_path)
        return LitSource(path=path, meta=meta)
    
    def get_all_sources(self) -> List[LitSource]:
        """Returns all sources found in the project's sources directory."""
        if not self.sources_path or not self.sources_path.exists():
            return []
        
        sources = []
        for folder in self.sources_path.iterdir():
            if folder.is_dir():
                try:
                    source = self.load_source(folder)
                    sources.append(source)
                except FileNotFoundError:
                    pass  # Ordner ohne Metadaten ignorieren
        
        return sources
    
    def get_notes(self, source: LitSource) -> LiNote:
        """Loads the notes for a source."""
        if source.notes_path.exists():
            return LiNote.load(source.notes_path)
        return LiNote()
    
    def save_notes(self, source: LitSource, notes: LiNote):
        """Saves notes for a source."""
        notes.save(source.notes_path)
    
    def get_quotes(self, source: LitSource) -> LiQuote:
        """Loads the quotes for a source."""
        if source.quotes_path.exists():
            return LiQuote.load(source.quotes_path)
        return LiQuote()
    
    def save_quotes(self, source: LitSource, quotes: LiQuote):
        """Saves quotes for a source."""
        quotes.save(source.quotes_path)
    
    def get_tasks(self, source: LitSource) -> LiTask:
        """Loads the tasks for a source."""
        if source.tasks_path.exists():
            return LiTask.load(source.tasks_path)
        return LiTask()
    
    def save_tasks(self, source: LitSource, tasks: LiTask):
        """Saves tasks for a source."""
        tasks.save(source.tasks_path)
    
    def get_summaries(self, source: LitSource) -> LiSum:
        """Loads the summaries for a source."""
        if source.summaries_path.exists():
            return LiSum.load(source.summaries_path)
        return LiSum()
    
    def save_summaries(self, source: LitSource, summaries: LiSum):
        """Saves summaries for a source."""
        summaries.save(source.summaries_path)
    
    def delete_source(self, source: LitSource):
        """Deletes a source and all its associated files from disk."""
        if source.path.exists():
            shutil.rmtree(source.path)
    
    def _generate_folder_name(self, meta: LiMeta) -> str:
        """Generates a filesystem-safe folder name from source metadata (Author+Year_Title)."""
        _invalid = re.compile(r'[<>:"/\\|?*\s]')
        author = _invalid.sub("", meta.first_author) or "Unbekannt"
        year = str(meta.year) if meta.year else "oJ"

        # Titel kürzen und säubern
        title = meta.title[:30] if meta.title else "Untitled"
        title = _invalid.sub("_", title).strip("_")

        return f"{author}{year}_{title}"

    def _get_unique_source_path(self, folder_name: str) -> Path:
        """Returns a non-existing source path, suffixing duplicates with _2, _3, ..."""
        base_path = self.sources_path / folder_name
        if not base_path.exists():
            return base_path

        counter = 2
        while True:
            candidate = self.sources_path / f"{folder_name}_{counter}"
            if not candidate.exists():
                return candidate
            counter += 1
    
    def search_sources(self, query: str) -> List[LitSource]:
        """Searches sources by title, author, or tags (case-insensitive)."""
        query = query.lower()
        results = []
        
        for source in self.get_all_sources():
            # Titel
            if query in source.meta.title.lower():
                results.append(source)
                continue
            
            # Autoren
            for author in source.meta.authors:
                if query in author.lower():
                    results.append(source)
                    break
            else:
                # Tags
                for tag in source.meta.tags:
                    if query in tag.lower():
                        results.append(source)
                        break
        
        return results
