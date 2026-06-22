"""
LitZentrum - Sync Module
Git-Integration und Backup-Funktionen
"""
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import shutil
import subprocess
import logging


class GitSync:
    """Git-Integration für Projektversionierung"""
    
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.git_dir = self.project_path / ".git"
    
    def is_git_available(self) -> bool:
        """Prüft ob Git installiert ist"""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (OSError, subprocess.SubprocessError, FileNotFoundError) as e:
            logging.debug(f"Git nicht verfügbar: {e}")
            return False
    
    def is_repository(self) -> bool:
        """Prüft ob Projekt ein Git-Repository ist"""
        return self.git_dir.exists()
    
    def init(self) -> bool:
        """Initialisiert Git-Repository"""
        if not self.is_git_available():
            return False
        
        if self.is_repository():
            return True
        
        try:
            result = subprocess.run(
                ["git", "init"],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                # .gitignore erstellen
                self._create_gitignore()
                return True
        except (OSError, subprocess.SubprocessError, PermissionError) as e:
            logging.debug(f"Fehler beim Git-Init: {e}")
        return False
    
    def _create_gitignore(self):
        """Erstellt .gitignore"""
        gitignore = self.project_path / ".gitignore"
        content = """# LitZentrum
__pycache__/
*.pyc
.DS_Store
Thumbs.db

# Temporäre Dateien
*.tmp
*.bak
~$*

# Große PDF-Dateien (optional)
# *.pdf
"""
        gitignore.write_text(content, encoding="utf-8")
    
    def status(self) -> Optional[str]:
        """Gibt Git-Status zurück"""
        if not self.is_repository():
            return None

        try:
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout
        except (OSError, subprocess.SubprocessError) as e:
            logging.debug(f"Fehler beim Git-Status: {e}")
            return None
    
    def add_all(self) -> bool:
        """Staged alle Änderungen"""
        try:
            result = subprocess.run(
                ["git", "add", "-A"],
                cwd=str(self.project_path),
                capture_output=True,
                timeout=30,
            )
            return result.returncode == 0
        except (OSError, subprocess.SubprocessError) as e:
            logging.debug(f"Fehler beim Git-Add: {e}")
            return False
    
    def commit(self, message: str = None) -> bool:
        """Erstellt Commit"""
        if not message:
            message = f"LitZentrum Auto-Commit: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        try:
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=str(self.project_path),
                capture_output=True,
                timeout=30,
            )
            return result.returncode == 0
        except (OSError, subprocess.SubprocessError) as e:
            logging.debug(f"Fehler beim Git-Commit: {e}")
            return False
    
    def auto_commit(self, message: str = None) -> bool:
        """Add + Commit in einem Schritt"""
        return self.add_all() and self.commit(message)


class BackupManager:
    """Lokale Backup-Verwaltung"""
    
    def __init__(self, project_path: Path, backup_dir: Path = None):
        self.project_path = Path(project_path)
        self.backup_dir = Path(backup_dir) if backup_dir else self.project_path.parent / "backups"
    
    def create_backup(self, name: str = None) -> Optional[Path]:
        """Erstellt Backup des Projekts"""
        # Backup-Verzeichnis erstellen
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup-Name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if name:
            backup_name = f"{self.project_path.name}_{name}_{timestamp}"
        else:
            backup_name = f"{self.project_path.name}_{timestamp}"
        
        backup_path = self.backup_dir / backup_name
        
        try:
            # Kopiere Projektordner
            shutil.copytree(
                self.project_path,
                backup_path,
                ignore=shutil.ignore_patterns(
                    "__pycache__", "*.pyc", ".git", "*.tmp"
                ),
            )
            return backup_path
        except Exception as e:
            print(f"Backup-Fehler: {e}")
            return None
    
    def list_backups(self) -> List[Path]:
        """Listet alle Backups"""
        if not self.backup_dir.exists():
            return []
        
        backups = []
        prefix = self.project_path.name
        for item in self.backup_dir.iterdir():
            if item.is_dir() and item.name.startswith(prefix):
                backups.append(item)
        
        # Nach Datum sortieren (neueste zuerst)
        backups.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return backups
    
    def restore_backup(self, backup_path: Path) -> bool:
        """Stellt Backup wieder her"""
        if not backup_path.exists():
            return False
        
        try:
            # Aktuelles Projekt sichern
            temp_backup = self.project_path.parent / f"{self.project_path.name}_before_restore"
            if temp_backup.exists():
                shutil.rmtree(temp_backup)
            
            self.project_path.rename(temp_backup)
            
            # Backup wiederherstellen
            shutil.copytree(backup_path, self.project_path)
            
            # Temporäres Backup löschen
            shutil.rmtree(temp_backup)
            
            return True
        except Exception as e:
            print(f"Restore-Fehler: {e}")
            return False
    
    def delete_backup(self, backup_path: Path) -> bool:
        """Löscht ein Backup"""
        if backup_path.exists() and backup_path.is_dir():
            try:
                shutil.rmtree(backup_path)
                return True
            except (OSError, PermissionError, shutil.Error) as e:
                logging.debug(f"Fehler beim Löschen des Backups '{backup_path}': {e}")
        return False
    
    def cleanup_old_backups(self, keep_count: int = 10):
        """Löscht alte Backups, behält die neuesten"""
        backups = self.list_backups()
        
        if len(backups) > keep_count:
            for old_backup in backups[keep_count:]:
                self.delete_backup(old_backup)
