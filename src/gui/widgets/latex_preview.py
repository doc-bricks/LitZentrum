"""
LitZentrum - LaTeX Formula Preview Widget
Rendert LaTeX-Formeln inline via KaTeX (QWebEngineView).

Verwendung:
    preview = LatexPreviewWidget()
    preview.update_content("Hier ist eine Formel: $E = mc^2$ und noch eine: $$\\int_0^1 f(x) dx$$")
"""
import re
from typing import Optional

from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

# QWebEngineView ist optional -- graceful fallback
try:
    from PySide6.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False


# KaTeX CDN (offline-Variante moeglich via lokale Dateien)
KATEX_CSS = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css"
KATEX_JS = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"
KATEX_AUTO = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"

# Regex fuer LaTeX-Erkennung (inline $...$ und display $$...$$)
LATEX_PATTERN = re.compile(r'\$\$.*?\$\$|\$[^\$]+?\$', re.DOTALL)


def contains_latex(text: str) -> bool:
    """Prueft ob Text LaTeX-Formeln enthaelt."""
    if not text:
        return False
    return bool(LATEX_PATTERN.search(text))


def escape_html(text: str) -> str:
    """Einfaches HTML-Escaping (ohne Formeln zu zerstoeren)."""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    # Zeilenumbrueche zu <br>
    text = text.replace("\n", "<br>")
    return text


def build_preview_html(text: str) -> str:
    """Baut die HTML-Seite fuer KaTeX-Rendering."""
    escaped = escape_html(text)

    # $ und $$ muessen als rohe Zeichen bleiben (nicht escaped)
    # Da wir & < > escapen aber $ nicht, funktioniert KaTeX auto-render

    # Wir muessen die $ Zeichen, die wir escaped haben, wiederherstellen
    # (escape_html zerstoert sie nicht, da $ kein HTML-Sonderzeichen ist)

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <link rel="stylesheet" href="{KATEX_CSS}">
    <style>
        body {{
            font-family: "Segoe UI", -apple-system, sans-serif;
            font-size: 13px;
            line-height: 1.6;
            color: #333;
            padding: 12px 16px;
            margin: 0;
            background: #fafafa;
        }}
        .katex-display {{
            margin: 12px 0;
            padding: 8px;
            background: #f0f4f8;
            border-radius: 4px;
            overflow-x: auto;
        }}
        .katex {{
            font-size: 1.1em;
        }}
        .no-latex {{
            color: #666;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div id="content">{escaped}</div>
    <script src="{KATEX_JS}"></script>
    <script src="{KATEX_AUTO}"></script>
    <script>
        renderMathInElement(document.getElementById("content"), {{
            delimiters: [
                {{left: "$$", right: "$$", display: true}},
                {{left: "$", right: "$", display: false}},
                {{left: "\\\\(", right: "\\\\)", display: false}},
                {{left: "\\\\[", right: "\\\\]", display: true}}
            ],
            throwOnError: false
        }});
    </script>
</body>
</html>"""


class LatexPreviewWidget(QWidget):
    """
    Widget das Text mit LaTeX-Formeln rendert.

    Benoetigt PySide6-WebEngine (QtWebEngineWidgets).
    Falls nicht verfuegbar: Fallback auf einfachen QLabel-Text.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._current_text = ""
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if WEBENGINE_AVAILABLE:
            self._web_view = QWebEngineView()
            self._web_view.setMinimumHeight(80)
            layout.addWidget(self._web_view)
            self._fallback_label = None
        else:
            self._web_view = None
            self._fallback_label = QLabel(
                "LaTeX-Preview nicht verfuegbar.\n"
                "Installiere: pip install PySide6-WebEngine"
            )
            self._fallback_label.setWordWrap(True)
            self._fallback_label.setStyleSheet("color: #888; font-style: italic; padding: 8px;")
            layout.addWidget(self._fallback_label)

    def update_content(self, text: str):
        """Aktualisiert den angezeigten Text mit LaTeX-Rendering."""
        self._current_text = text

        if not text:
            if self._web_view:
                self._web_view.setHtml("<html><body style='color:#888;font-style:italic;padding:12px;'>Kein Inhalt</body></html>")
            elif self._fallback_label:
                self._fallback_label.setText("Kein Inhalt")
            return

        if self._web_view:
            if contains_latex(text):
                html = build_preview_html(text)
                self._web_view.setHtml(html)
            else:
                # Kein LaTeX -- einfache Textanzeige
                simple_html = f"<html><body style='font-family:Segoe UI;font-size:13px;padding:12px;line-height:1.6;'>{escape_html(text)}</body></html>"
                self._web_view.setHtml(simple_html)
        elif self._fallback_label:
            self._fallback_label.setText(text[:500])

    def clear(self):
        """Leert die Anzeige."""
        self.update_content("")

    @staticmethod
    def is_available() -> bool:
        """Prueft ob WebEngine verfuegbar ist."""
        return WEBENGINE_AVAILABLE
