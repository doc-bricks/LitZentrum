"""
LitZentrum - Literature management application.
Application entry point.
"""
import sys
from pathlib import Path

# Füge src zum Pfad hinzu
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from app_paths import base_dir
from gui import MainWindow


def main():
    """Starts the LitZentrum application."""
    # High-DPI Unterstützung
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("LitZentrum")
    app.setOrganizationName("LitZentrum")
    app.setApplicationVersion("1.0.0")
    
    # Style
    app.setStyle("Fusion")
    
    # Icon (falls vorhanden) -- base_dir() loest Quell- vs. Frozen-Layout auf
    icon_path = base_dir() / "resources" / "icons" / "litzentrum.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Hauptfenster
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
