"""
LitZentrum - LiQuote Format (.liquote)
Zitate aus Literaturquellen
"""
from dataclasses import dataclass, field
from typing import List, Optional

from .base import LitFormat, generate_id, now_iso


@dataclass
class Quote:
    """Ein einzelnes Zitat"""
    id: str
    text: str
    created_at: str
    type: str = "direct"  # direct, indirect, paraphrase
    page: Optional[int] = None
    page_end: Optional[int] = None
    comment: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    used_in: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "text": self.text,
            "page": self.page,
            "page_end": self.page_end,
            "comment": self.comment,
            "tags": self.tags,
            "used_in": self.used_in,
            "created_at": self.created_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Quote":
        return cls(
            id=data.get("id", generate_id("q_")),
            type=data.get("type", "direct"),
            text=data.get("text", ""),
            page=data.get("page"),
            page_end=data.get("page_end"),
            comment=data.get("comment"),
            tags=data.get("tags") or [],
            used_in=data.get("used_in") or [],
            created_at=data.get("created_at", now_iso()),
        )
    
    @property
    def page_range(self) -> str:
        """Gibt Seitenbereich als String zurück"""
        if self.page_end and self.page_end != self.page:
            return f"{self.page}-{self.page_end}"
        return str(self.page) if self.page else ""


@dataclass
class LiQuote(LitFormat):
    """Sammlung von Zitaten aus einer Quelle"""
    
    FILE_EXTENSION = ".liquote"
    SCHEMA_FILE = "liquote.schema.json"
    
    quotes: List[Quote] = field(default_factory=list)
    schema_version: str = "1.0.0"
    
    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "quotes": [q.to_dict() for q in self.quotes],
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "LiQuote":
        quotes = [Quote.from_dict(q) for q in data.get("quotes") or []]
        return cls(
            quotes=quotes,
            schema_version=data.get("schema_version", "1.0.0"),
        )
    
    def add(self, text: str, page: Optional[int] = None,
            quote_type: str = "direct", comment: str = None,
            tags: List[str] = None) -> Quote:
        """Fügt ein neues Zitat hinzu"""
        quote = Quote(
            id=generate_id("q_"),
            type=quote_type,
            text=text,
            page=page,
            comment=comment,
            tags=tags or [],
            created_at=now_iso(),
        )
        self.quotes.append(quote)
        return quote
    
    def get_direct(self) -> List[Quote]:
        """Gibt alle direkten Zitate zurück"""
        return [q for q in self.quotes if q.type == "direct"]
    
    def get_by_page(self, page: int) -> List[Quote]:
        """Gibt alle Zitate von einer Seite zurück"""
        return [q for q in self.quotes 
                if q.page == page or 
                (q.page and q.page_end and q.page <= page <= q.page_end)]
    
    def get_by_tag(self, tag: str) -> List[Quote]:
        """Gibt alle Zitate mit einem Tag zurück"""
        return [q for q in self.quotes if tag in q.tags]
    
    def remove(self, quote_id: str) -> bool:
        """Entfernt ein Zitat nach ID"""
        for i, quote in enumerate(self.quotes):
            if quote.id == quote_id:
                del self.quotes[i]
                return True
        return False
    
    def __len__(self) -> int:
        return len(self.quotes)
