"""
LitZentrum - Library export bundle for companion clients.
"""
from pathlib import Path, PureWindowsPath
from typing import Dict, List, Optional
import hashlib
import json
import re

import jsonschema

from core.project_manager import LitProject, ProjectManager
from core.source_manager import LitSource, SourceManager
from modules.bibliography.styles import CitationStyleManager
from modules.bibliography.bibtex import BibTeXGenerator
from formats import now_iso


class LibraryExporter:
    """Builds and writes read-only library exports for companion clients."""

    APP_NAME = "LitZentrum"
    APP_VERSION = "1.0.0"
    SCHEMA_NAME = "litzentrum-library"
    SCHEMA_VERSION = "1.0"
    SCHEMA_FILE = Path(__file__).parent.parent.parent / "schemas" / "litzentrum-library-v1.schema.json"

    def __init__(
        self,
        project_manager: ProjectManager,
        source_manager: Optional[SourceManager] = None,
    ):
        self.project_manager = project_manager
        self.source_manager = source_manager

    def export_current_project(self, output_path: Path) -> Path:
        """Exports the currently opened project."""
        project = self.project_manager.current_project
        if not project:
            raise ValueError("Kein Projekt geöffnet")
        return self.export_project(project, output_path)

    def export_project(self, project: LitProject, output_path: Path) -> Path:
        """Builds, validates and writes the export bundle."""
        bundle = self.build_bundle(project)
        self.validate_bundle(bundle)

        output_path = Path(output_path)
        if not output_path.suffix:
            output_path = output_path.with_suffix(".json")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(bundle, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return output_path

    def build_bundle(self, project: LitProject) -> dict:
        """Builds the in-memory export bundle."""
        source_manager = self._get_source_manager(project)
        sources = sorted(source_manager.get_all_sources(), key=lambda source: source.path.name.lower())
        project_tasks = self.project_manager.get_project_tasks(project)
        project_notes = self.project_manager.get_project_notes(project)

        bibtex_generator = BibTeXGenerator()
        bibliography = bibtex_generator.generate_bibliography([source.meta for source in sources])

        return {
            "schema": self.SCHEMA_NAME,
            "schema_version": self.SCHEMA_VERSION,
            "app": {
                "name": self.APP_NAME,
                "version": self.APP_VERSION,
            },
            "exported_at": now_iso(),
            "capabilities": {
                "contains_pdf_files": False,
                "contains_pdf_text": False,
                "read_only_companion": True,
            },
            "projects": [
                {
                    "id": self._slugify(project.path.name or project.name, "project"),
                    "name": project.name,
                    "description": project.config.description,
                    "citation_style": project.config.citation_style,
                    "language": project.config.language,
                    "sources_folder": project.config.sources_folder,
                    "project_notes": [note.to_dict() for note in project_notes.notes],
                    "project_tasks": [task.to_dict() for task in project_tasks.tasks],
                    "sources": [self._serialize_source(project, source, source_manager) for source in sources],
                }
            ],
            "bibliography": {
                "bibtex": bibliography,
                "styles": CitationStyleManager.available_styles(),
            },
        }

    def validate_bundle(self, bundle: dict) -> None:
        """Validates the export bundle against the JSON schema."""
        with open(self.SCHEMA_FILE, "r", encoding="utf-8") as handle:
            schema = json.load(handle)
        jsonschema.validate(bundle, schema)

    def _serialize_source(
        self,
        project: LitProject,
        source: LitSource,
        source_manager: SourceManager,
    ) -> dict:
        notes = source_manager.get_notes(source)
        quotes = source_manager.get_quotes(source)
        tasks = source_manager.get_tasks(source)
        summaries = source_manager.get_summaries(source)

        return {
            "id": self._slugify(source.path.name, "source"),
            "folder_name": source.path.name,
            "metadata": self._serialize_metadata(source),
            "notes": [note.to_dict() for note in notes.notes],
            "quotes": [quote.to_dict() for quote in quotes.quotes],
            "tasks": [task.to_dict() for task in tasks.tasks],
            "summaries": [summary.to_dict() for summary in summaries.summaries],
            "files": self._serialize_files(project, source),
        }

    def _serialize_metadata(self, source: LitSource) -> dict:
        metadata = source.meta.to_dict()
        source_file = metadata.get("source_file")
        if source_file:
            metadata["source_file"] = self._basename(source_file)
        return metadata

    def _serialize_files(self, project: LitProject, source: LitSource) -> List[dict]:
        file_candidates: List[Path] = []
        if source.meta.source_file:
            source_file = source.meta.source_file
            if Path(source_file).is_absolute() or PureWindowsPath(source_file).is_absolute():
                file_candidates.append(Path(source_file))
            else:
                file_candidates.append(source.path / source_file)
        elif source.pdf_path:
            file_candidates.append(source.pdf_path)

        entries: List[dict] = []
        seen: set[str] = set()

        for candidate in file_candidates:
            if not candidate:
                continue

            candidate = Path(candidate)
            filename = self._basename(str(candidate))
            if filename in seen:
                continue
            seen.add(filename)

            try:
                relative_path = candidate.relative_to(project.path).as_posix()
            except ValueError:
                relative_path = (
                    Path(project.config.sources_folder) / source.path.name / filename
                ).as_posix()

            exists = candidate.exists()
            entries.append(
                {
                    "role": "source_pdf",
                    "name": filename,
                    "relative_path": relative_path,
                    "sha256": self._sha256(candidate) if exists else None,
                    "included": False,
                    "exists": exists,
                }
            )

        return entries

    def _get_source_manager(self, project: LitProject) -> SourceManager:
        if (
            self.source_manager
            and self.source_manager.project_path == project.path
            and self.source_manager.sources_folder == project.config.sources_folder
        ):
            return self.source_manager
        return SourceManager(project.path, project.config.sources_folder)

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _basename(value: str) -> str:
        return PureWindowsPath(value).name or Path(value).name

    @staticmethod
    def _slugify(value: str, fallback_prefix: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        return slug or f"{fallback_prefix}-{now_iso().replace(':', '-').replace('.', '-')}"
