"""
LitZentrum - Einstellungen Dialog
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QTabWidget,
    QLineEdit, QComboBox, QPushButton, QCheckBox, QSpinBox,
    QDialogButtonBox, QFileDialog, QLabel, QWidget, QGroupBox
)

from core import get_settings


class SettingsDialog(QDialog):
    """Dialog für Einstellungen"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = get_settings()
        self.setWindowTitle("Einstellungen")
        self.setMinimumSize(550, 450)
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        tabs = QTabWidget()
        
        # Tab 1: Allgemein
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        # Erscheinungsbild
        appearance_group = QGroupBox("Erscheinungsbild")
        appearance_layout = QFormLayout(appearance_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Hell", "Dunkel", "System"])
        appearance_layout.addRow("Design:", self.theme_combo)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Deutsch", "English"])
        appearance_layout.addRow("Sprache:", self.language_combo)
        
        general_layout.addWidget(appearance_group)
        
        # Zitation
        citation_group = QGroupBox("Zitation")
        citation_layout = QFormLayout(citation_group)
        
        self.citation_style_combo = QComboBox()
        self.citation_style_combo.addItems(["APA", "MLA", "Chicago", "DIN 1505", "Harvard"])
        citation_layout.addRow("Standard-Stil:", self.citation_style_combo)
        
        self.auto_key_check = QCheckBox("Automatisch generieren")
        citation_layout.addRow("Zitations-Key:", self.auto_key_check)
        
        general_layout.addWidget(citation_group)
        general_layout.addStretch()
        
        tabs.addTab(general_tab, "Allgemein")
        
        # Tab 2: PDF
        pdf_tab = QWidget()
        pdf_layout = QVBoxLayout(pdf_tab)
        
        pdf_group = QGroupBox("PDF-Anzeige")
        pdf_form = QFormLayout(pdf_group)
        
        self.pdf_zoom_spin = QSpinBox()
        self.pdf_zoom_spin.setRange(50, 300)
        self.pdf_zoom_spin.setSuffix(" %")
        pdf_form.addRow("Standard-Zoom:", self.pdf_zoom_spin)
        
        self.highlight_color_combo = QComboBox()
        self.highlight_color_combo.addItems(["Gelb", "Grün", "Blau", "Rosa", "Orange"])
        pdf_form.addRow("Markierungsfarbe:", self.highlight_color_combo)
        
        pdf_layout.addWidget(pdf_group)
        pdf_layout.addStretch()
        
        tabs.addTab(pdf_tab, "PDF")
        
        # Tab 3: KI
        ai_tab = QWidget()
        ai_layout = QVBoxLayout(ai_tab)
        
        ai_group = QGroupBox("Ollama-Integration")
        ai_form = QFormLayout(ai_group)
        
        self.ai_enabled_check = QCheckBox("KI-Funktionen aktivieren")
        ai_form.addRow("", self.ai_enabled_check)
        
        self.ai_url_input = QLineEdit()
        self.ai_url_input.setPlaceholderText("http://localhost:11434")
        ai_form.addRow("Ollama-URL:", self.ai_url_input)
        
        self.ai_model_combo = QComboBox()
        self.ai_model_combo.setEditable(True)
        self.ai_model_combo.addItems(["mistral:latest", "llama2:latest", "codellama:latest"])
        ai_form.addRow("Modell:", self.ai_model_combo)

        btn_layout = QHBoxLayout()
        test_btn = QPushButton("Verbindung testen")
        test_btn.clicked.connect(self._test_ai_connection)
        btn_layout.addWidget(test_btn)

        refresh_btn = QPushButton("Modelle laden")
        refresh_btn.clicked.connect(self._refresh_ai_models)
        btn_layout.addWidget(refresh_btn)
        ai_form.addRow("", btn_layout)
        
        ai_layout.addWidget(ai_group)
        ai_layout.addStretch()
        
        tabs.addTab(ai_tab, "KI")
        
        # Tab 4: Backup
        backup_tab = QWidget()
        backup_layout = QVBoxLayout(backup_tab)
        
        backup_group = QGroupBox("Automatische Sicherung")
        backup_form = QFormLayout(backup_group)
        
        self.auto_backup_check = QCheckBox("Automatisches Backup aktivieren")
        backup_form.addRow("", self.auto_backup_check)
        
        self.backup_interval_spin = QSpinBox()
        self.backup_interval_spin.setRange(5, 120)
        self.backup_interval_spin.setSuffix(" Minuten")
        backup_form.addRow("Intervall:", self.backup_interval_spin)
        
        path_layout = QHBoxLayout()
        self.backup_path_input = QLineEdit()
        self.backup_path_input.setReadOnly(True)
        path_layout.addWidget(self.backup_path_input)
        
        browse_btn = QPushButton("📁")
        browse_btn.clicked.connect(self._browse_backup_path)
        path_layout.addWidget(browse_btn)
        backup_form.addRow("Backup-Ordner:", path_layout)
        
        backup_layout.addWidget(backup_group)
        backup_layout.addStretch()
        
        tabs.addTab(backup_tab, "Backup")
        
        layout.addWidget(tabs)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.RestoreDefaults
        )
        buttons.accepted.connect(self._save_and_close)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self._restore_defaults)
        layout.addWidget(buttons)
    
    def _load_settings(self):
        """Lädt aktuelle Einstellungen"""
        # Allgemein
        theme = self.settings.get("theme", "light")
        self.theme_combo.setCurrentIndex({"light": 0, "dark": 1, "system": 2}.get(theme, 0))
        
        lang = self.settings.get("language", "de")
        self.language_combo.setCurrentIndex(0 if lang == "de" else 1)
        
        style = self.settings.get("default_citation_style", "apa")
        style_map = {"apa": 0, "mla": 1, "chicago": 2, "din": 3, "harvard": 4}
        self.citation_style_combo.setCurrentIndex(style_map.get(style, 0))
        
        self.auto_key_check.setChecked(self.settings.get("auto_generate_citation_key", True))
        
        # PDF
        self.pdf_zoom_spin.setValue(self.settings.get("pdf_zoom_default", 100))
        
        # KI
        self.ai_enabled_check.setChecked(self.settings.get("ai_enabled", False))
        self.ai_url_input.setText(self.settings.get("ai_base_url", "http://localhost:11434"))
        self.ai_model_combo.setCurrentText(self.settings.get("ai_model", "mistral:latest"))
        
        # Backup
        self.auto_backup_check.setChecked(self.settings.get("auto_backup", True))
        self.backup_interval_spin.setValue(self.settings.get("backup_interval_minutes", 30))
        self.backup_path_input.setText(self.settings.get("backup_path", "") or "")
    
    def _save_and_close(self):
        """Speichert Einstellungen"""
        # Allgemein
        theme_map = {0: "light", 1: "dark", 2: "system"}
        self.settings.set("theme", theme_map[self.theme_combo.currentIndex()])
        self.settings.set("language", "de" if self.language_combo.currentIndex() == 0 else "en")
        
        style_map = {0: "apa", 1: "mla", 2: "chicago", 3: "din", 4: "harvard"}
        self.settings.set("default_citation_style", style_map[self.citation_style_combo.currentIndex()])
        self.settings.set("auto_generate_citation_key", self.auto_key_check.isChecked())
        
        # PDF
        self.settings.set("pdf_zoom_default", self.pdf_zoom_spin.value())
        
        # KI
        self.settings.set("ai_enabled", self.ai_enabled_check.isChecked())
        self.settings.set("ai_base_url", self.ai_url_input.text())
        self.settings.set("ai_model", self.ai_model_combo.currentText())
        
        # Backup
        self.settings.set("auto_backup", self.auto_backup_check.isChecked())
        self.settings.set("backup_interval_minutes", self.backup_interval_spin.value())
        self.settings.set("backup_path", self.backup_path_input.text() or None)
        
        self.settings.sync()
        self.accept()
    
    def _restore_defaults(self):
        """Stellt Standardeinstellungen wieder her"""
        from PySide6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self, "Zurücksetzen",
            "Alle Einstellungen auf Standard zurücksetzen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings.reset_to_defaults()
            self._load_settings()
    
    def _browse_backup_path(self):
        """Backup-Ordner auswählen"""
        from pathlib import Path
        path = QFileDialog.getExistingDirectory(
            self, "Backup-Ordner auswählen", str(Path.home())
        )
        if path:
            self.backup_path_input.setText(path)
    
    def _fetch_ollama_models(self) -> list[str] | None:
        """Ruft verfügbare Modelle von Ollama ab.

        Returns:
            Liste der Modellnamen oder None bei Verbindungsfehler.
        """
        import requests

        url = self.ai_url_input.text() or "http://localhost:11434"
        try:
            response = requests.get(f"{url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m["name"] for m in models]
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            pass
        except (ValueError, KeyError):
            pass
        return None

    def _populate_model_combo(self, model_names: list[str]):
        """Befüllt die Modell-ComboBox mit den verfügbaren Modellen.

        Args:
            model_names: Liste der Ollama-Modellnamen.
        """
        current = self.ai_model_combo.currentText()
        self.ai_model_combo.clear()
        self.ai_model_combo.addItems(model_names)
        # Vorherige Auswahl beibehalten, falls noch verfügbar
        if current in model_names:
            self.ai_model_combo.setCurrentText(current)
        elif model_names:
            self.ai_model_combo.setCurrentIndex(0)

    def _refresh_ai_models(self):
        """Lädt verfügbare Modelle von Ollama und befüllt die ComboBox."""
        from PySide6.QtWidgets import QMessageBox

        model_names = self._fetch_ollama_models()
        if model_names is not None and len(model_names) > 0:
            self._populate_model_combo(model_names)
            QMessageBox.information(
                self, "Modelle geladen",
                f"{len(model_names)} Modell(e) gefunden."
            )
        else:
            QMessageBox.warning(
                self, "Fehler",
                "Keine Modelle gefunden.\n\nStellen Sie sicher, dass Ollama läuft."
            )

    def _test_ai_connection(self):
        """Testet Ollama-Verbindung und aktualisiert die Modell-ComboBox."""
        from PySide6.QtWidgets import QMessageBox

        model_names = self._fetch_ollama_models()
        if model_names is not None:
            self._populate_model_combo(model_names)
            QMessageBox.information(
                self, "Erfolg",
                f"Verbindung erfolgreich!\n\nVerfügbare Modelle:\n" +
                "\n".join(model_names[:10])
            )
        else:
            import requests
            url = self.ai_url_input.text() or "http://localhost:11434"
            try:
                response = requests.get(f"{url}/api/tags", timeout=5)
                QMessageBox.warning(self, "Fehler", f"Server antwortet mit: {response.status_code}")
            except requests.exceptions.ConnectionError:
                QMessageBox.warning(self, "Fehler", "Keine Verbindung zu Ollama.\n\nStellen Sie sicher, dass Ollama läuft.")
            except (requests.exceptions.Timeout, OSError) as e:
                QMessageBox.warning(self, "Fehler", f"Fehler: {e}")
