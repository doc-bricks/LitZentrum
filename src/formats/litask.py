"""
LitZentrum - LiTask Format (.litask)
Aufgaben für Literaturquellen
"""
from dataclasses import dataclass, field
from typing import List, Optional

from .base import LitFormat, generate_id, now_iso


@dataclass
class Task:
    """Eine einzelne Aufgabe"""
    id: str
    title: str
    status: str
    created_at: str
    description: Optional[str] = None
    priority: str = "normal"  # low, normal, high, urgent
    due_date: Optional[str] = None
    page: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    completed_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "due_date": self.due_date,
            "page": self.page,
            "tags": self.tags,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            id=data.get("id", generate_id("t_")),
            title=data.get("title", ""),
            description=data.get("description"),
            status=data.get("status", "open"),
            priority=data.get("priority", "normal"),
            due_date=data.get("due_date"),
            page=data.get("page"),
            tags=data.get("tags") or [],
            created_at=data.get("created_at", now_iso()),
            completed_at=data.get("completed_at"),
        )
    
    def complete(self):
        """Markiert die Aufgabe als erledigt"""
        self.status = "done"
        self.completed_at = now_iso()
    
    @property
    def is_open(self) -> bool:
        return self.status in ("open", "in_progress")
    
    @property
    def is_overdue(self) -> bool:
        """Prüft ob die Aufgabe überfällig ist"""
        if not self.due_date or not self.is_open:
            return False
        from datetime import datetime
        # Bugsweep 27: ungueltiges oder tz-aware due_date nicht crashen lassen
        # (fromisoformat-ValueError bzw. naive/aware-Vergleich-TypeError) -> dann "nicht ueberfaellig".
        try:
            due = datetime.fromisoformat(self.due_date)
        except (ValueError, TypeError):
            return False
        return datetime.now(due.tzinfo) > due


@dataclass
class LiTask(LitFormat):
    """Sammlung von Aufgaben"""
    
    FILE_EXTENSION = ".litask"
    SCHEMA_FILE = "litask.schema.json"
    
    tasks: List[Task] = field(default_factory=list)
    schema_version: str = "1.0.0"
    
    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "tasks": [t.to_dict() for t in self.tasks],
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "LiTask":
        tasks = [Task.from_dict(t) for t in data.get("tasks") or []]
        return cls(
            tasks=tasks,
            schema_version=data.get("schema_version", "1.0.0"),
        )
    
    def add(self, title: str, description: str = None,
            priority: str = "normal", due_date: str = None,
            page: int = None, tags: List[str] = None) -> Task:
        """Fügt eine neue Aufgabe hinzu"""
        task = Task(
            id=generate_id("t_"),
            title=title,
            description=description,
            status="open",
            priority=priority,
            due_date=due_date,
            page=page,
            tags=tags or [],
            created_at=now_iso(),
        )
        self.tasks.append(task)
        return task
    
    def get_open(self) -> List[Task]:
        """Gibt alle offenen Aufgaben zurück"""
        return [t for t in self.tasks if t.is_open]
    
    def get_overdue(self) -> List[Task]:
        """Gibt alle überfälligen Aufgaben zurück"""
        return [t for t in self.tasks if t.is_overdue]
    
    def get_by_priority(self, priority: str) -> List[Task]:
        """Gibt Aufgaben nach Priorität zurück"""
        return [t for t in self.tasks if t.priority == priority]
    
    def complete(self, task_id: str) -> bool:
        """Markiert eine Aufgabe als erledigt"""
        for task in self.tasks:
            if task.id == task_id:
                task.complete()
                return True
        return False
    
    def remove(self, task_id: str) -> bool:
        """Entfernt eine Aufgabe"""
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                del self.tasks[i]
                return True
        return False
    
    def __len__(self) -> int:
        return len(self.tasks)
    
    @property
    def open_count(self) -> int:
        return len(self.get_open())
