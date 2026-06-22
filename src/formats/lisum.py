"""
LitZentrum - LiSum Format (.lisum)
Zusammenfassungen für Literaturquellen
"""
from dataclasses import dataclass, field
from typing import List, Optional

from .base import LitFormat, generate_id, now_iso


@dataclass
class Summary:
    """Eine einzelne Zusammenfassung"""
    id: str
    title: str
    content: str
    created_at: str
    type: str = "full"  # full, chapter, section, abstract
    source: str = "manual"  # manual, ai_generated, imported
    ai_model: Optional[str] = None
    pages: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    updated_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "type": self.type,
            "source": self.source,
            "ai_model": self.ai_model,
            "pages": self.pages,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Summary":
        return cls(
            id=data.get("id", generate_id("s_")),
            title=data.get("title", ""),
            content=data.get("content", ""),
            type=data.get("type", "full"),
            source=data.get("source", "manual"),
            ai_model=data.get("ai_model"),
            pages=data.get("pages"),
            tags=data.get("tags") or [],
            created_at=data.get("created_at", now_iso()),
            updated_at=data.get("updated_at"),
        )
    
    def update_content(self, content: str):
        """Aktualisiert den Inhalt"""
        self.content = content
        self.updated_at = now_iso()


@dataclass
class LiSum(LitFormat):
    """Sammlung von Zusammenfassungen"""
    
    FILE_EXTENSION = ".lisum"
    SCHEMA_FILE = "lisum.schema.json"
    
    summaries: List[Summary] = field(default_factory=list)
    schema_version: str = "1.0.0"
    
    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "summaries": [s.to_dict() for s in self.summaries],
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "LiSum":
        summaries = [Summary.from_dict(s) for s in data.get("summaries") or []]
        return cls(
            summaries=summaries,
            schema_version=data.get("schema_version", "1.0.0"),
        )
    
    def add(self, title: str, content: str,
            summary_type: str = "full", source: str = "manual",
            ai_model: str = None, pages: str = None,
            tags: List[str] = None) -> Summary:
        """Fügt eine neue Zusammenfassung hinzu"""
        summary = Summary(
            id=generate_id("s_"),
            title=title,
            content=content,
            type=summary_type,
            source=source,
            ai_model=ai_model,
            pages=pages,
            tags=tags or [],
            created_at=now_iso(),
        )
        self.summaries.append(summary)
        return summary
    
    def get_by_type(self, summary_type: str) -> List[Summary]:
        """Gibt Zusammenfassungen nach Typ zurück"""
        return [s for s in self.summaries if s.type == summary_type]
    
    def get_ai_generated(self) -> List[Summary]:
        """Gibt alle KI-generierten Zusammenfassungen zurück"""
        return [s for s in self.summaries if s.source == "ai_generated"]
    
    def get_manual(self) -> List[Summary]:
        """Gibt alle manuellen Zusammenfassungen zurück"""
        return [s for s in self.summaries if s.source == "manual"]
    
    def remove(self, summary_id: str) -> bool:
        """Entfernt eine Zusammenfassung"""
        for i, summary in enumerate(self.summaries):
            if summary.id == summary_id:
                del self.summaries[i]
                return True
        return False
    
    def __len__(self) -> int:
        return len(self.summaries)
