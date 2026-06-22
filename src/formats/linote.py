"""
LitZentrum - LiNote Format (.linote)
Notizen für Literaturquellen
"""
from dataclasses import dataclass, field
from typing import List, Optional

from .base import LitFormat, generate_id, now_iso


@dataclass
class Note:
    """Eine einzelne Notiz"""
    id: str
    content: str
    created_at: str
    page: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    updated_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "page": self.page,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        return cls(
            id=data.get("id", generate_id("n_")),
            content=data.get("content", ""),
            page=data.get("page"),
            tags=data.get("tags") or [],
            created_at=data.get("created_at", now_iso()),
            updated_at=data.get("updated_at"),
        )


@dataclass
class LiNote(LitFormat):
    """Sammlung von Notizen zu einer Quelle"""
    
    FILE_EXTENSION = ".linote"
    SCHEMA_FILE = "linote.schema.json"
    
    notes: List[Note] = field(default_factory=list)
    schema_version: str = "1.0.0"
    
    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "notes": [n.to_dict() for n in self.notes],
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "LiNote":
        notes = [Note.from_dict(n) for n in data.get("notes") or []]
        return cls(
            notes=notes,
            schema_version=data.get("schema_version", "1.0.0"),
        )
    
    def add(self, content: str, page: Optional[int] = None, 
            tags: List[str] = None) -> Note:
        """Fügt eine neue Notiz hinzu"""
        note = Note(
            id=generate_id("n_"),
            content=content,
            page=page,
            tags=tags or [],
            created_at=now_iso(),
        )
        self.notes.append(note)
        return note
    
    def get_by_page(self, page: int) -> List[Note]:
        """Gibt alle Notizen zu einer Seite zurück"""
        return [n for n in self.notes if n.page == page]
    
    def get_by_tag(self, tag: str) -> List[Note]:
        """Gibt alle Notizen mit einem Tag zurück"""
        return [n for n in self.notes if tag in n.tags]
    
    def remove(self, note_id: str) -> bool:
        """Entfernt eine Notiz nach ID"""
        for i, note in enumerate(self.notes):
            if note.id == note_id:
                del self.notes[i]
                return True
        return False
    
    def __len__(self) -> int:
        return len(self.notes)
