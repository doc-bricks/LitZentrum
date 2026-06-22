"""
LitZentrum - Base class for all file formats.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar
import json
import jsonschema

T = TypeVar('T', bound='LitFormat')


class LitFormatError(Exception):
    """Raised when a LitFormat file cannot be processed."""
    pass


class LitValidationError(LitFormatError):
    """Raised when a LitFormat object fails JSON schema validation."""
    pass


class LitFormat(ABC):
    """Abstract base class for all .li* file formats."""
    
    SCHEMA_VERSION = "1.0.0"
    FILE_EXTENSION: str = ""
    SCHEMA_FILE: str = ""
    
    _schema_cache: Dict[str, dict] = {}
    
    @classmethod
    def get_schema(cls) -> dict:
        """Loads and caches the JSON schema for this format."""
        if cls.SCHEMA_FILE not in cls._schema_cache:
            schema_path = Path(__file__).parent.parent.parent / "schemas" / cls.SCHEMA_FILE
            if schema_path.exists():
                try:
                    with open(schema_path, 'r', encoding='utf-8') as f:
                        cls._schema_cache[cls.SCHEMA_FILE] = json.load(f)
                except (json.JSONDecodeError, OSError):
                    cls._schema_cache[cls.SCHEMA_FILE] = {}
            else:
                cls._schema_cache[cls.SCHEMA_FILE] = {}
        return cls._schema_cache[cls.SCHEMA_FILE]
    
    @abstractmethod
    def to_dict(self) -> dict:
        """Converts the object to a dictionary for JSON serialization."""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls: Type[T], data: dict) -> T:
        """Creates an instance from a dictionary."""
        pass

    def validate(self) -> bool:
        """Validates the object against its JSON schema."""
        schema = self.get_schema()
        if not schema:
            return True  # Kein Schema = keine Validierung
        
        try:
            jsonschema.validate(self.to_dict(), schema)
            return True
        except jsonschema.ValidationError as e:
            raise LitValidationError(f"Validierungsfehler: {e.message}")
    
    def save(self, path: Path) -> None:
        """Validates and saves the object to a JSON file at the given path."""
        self.validate()
        
        path = Path(path)
        if not path.suffix:
            path = path.with_suffix(self.FILE_EXTENSION)
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2, default=str)
    
    @classmethod
    def load(cls: Type[T], path: Path) -> T:
        """Loads an instance from a JSON file.

        Args:
            path: Path to the .li* file.

        Returns:
            Deserialized instance of the concrete subclass.

        Raises:
            LitFormatError: If the file does not exist.
        """
        path = Path(path)
        
        if not path.exists():
            raise LitFormatError(f"Datei nicht gefunden: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                raise LitFormatError(f"Ungültige JSON-Datei: {path}: {e}")

        return cls.from_dict(data)


def generate_id(prefix: str = "") -> str:
    """Generates a unique timestamp-based ID with an optional prefix."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"{prefix}{timestamp}" if prefix else timestamp


def now_iso() -> str:
    """Returns the current local time as an ISO 8601 string."""
    return datetime.now().isoformat()
