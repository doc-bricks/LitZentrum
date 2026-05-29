# Portierungsplan LitZentrum

Stand: 2026-05-27

## Zweck und Ausgangslage

LitZentrum ist eine ordnerbasierte Literaturverwaltung für wissenschaftliche Arbeiten. Die Vollversion braucht lokale Dateisystemrechte, PDF-Verarbeitung mit PyMuPDF, BibTeX-/Word-Export, optionale Ollama-Anbindung und Git-/Backup-Flows. Diese Eigenschaften sprechen gegen einen direkten Mobile-Klon, aber klar für eine ergänzende plattformübergreifende Leselinie.

Der sinnvolle Cross-Platform-Ansatz ist deshalb zweigeteilt:

1. Desktop bleibt die autoritative Vollversion für Windows, macOS und Linux.
2. Web/PWA wird ein Companion für Android, iOS und Browser, der Bibliotheken, Metadaten, Notizen, Zitate, Aufgaben, Zusammenfassungen und BibTeX-Exports aus einem redigierten JSON-Bündel lesen kann.

## Zielgruppen und Use Cases

| Zielgruppe | Bedarf | Konsequenz |
|---|---|---|
| Studierende und Forschende | Literatur unterwegs nachschlagen, Zitate kopieren, Lesestatus prüfen | Mobile Companion statt vollständiger PDF-Werkstatt |
| Schreibende am Desktop | PDFs importieren, Metadaten pflegen, BibTeX/Word exportieren, KI nutzen | Desktop-Vollversion bleibt zentral |
| LLM-/Automationsnutzung | Bibliotheken maschinenlesbar prüfen, Zitate/Tasks auslesen | Stabiles JSON-Exportformat priorisieren |
| Datenschutzbewusste Nutzer | Keine Cloud-Pflicht, keine ungeprüften PDF-Uploads | Export standardmäßig ohne PDF-Inhalte |

## Plattformbewertung

| Plattform | Bewertung | Entscheidung |
|---|---|---|
| Windows Store | Sinnvoll als erster Store-Kanal, wenn Store-Assets, Datenschutz-/Support-URL, MSIX und WACK erledigt sind. AGPL/PyMuPDF ist nur sauber, wenn Quellcode und Lizenzhinweise öffentlich bleiben. | P1: vorbereiten, nicht vor Store-Pflichtartefakten einreichen |
| Android | Hoher Nutzen für Lesen, Zitieren und Aufgaben unterwegs; nativer Zugriff auf lokale Desktop-Projektordner wäre zu fragil. | P2: über Web/PWA oder Capacitor-Wrapper, kein nativer Vollklon |
| Webapp | Beste gemeinsame Linie für Android, iOS und Browser. Offline-fähiger Import eines Exportbündels reicht für viele Mobile-Use-Cases. | P1: Web/PWA-Companion planen |
| iOS | Sinnvoll nur als PWA/TestFlight-Hülle, weil Datei- und PDF-Workflows stark sandboxed sind. | P2: PWA, später optional App-Store-Hülle |
| Mac App | Fachlich sinnvoll, weil akademische Nutzer häufig macOS verwenden. PySide6/PyMuPDF sollten als Source-Smoke geprüft werden; öffentliche Builds brauchen Signierung/Notarisierung. | P1: Source-Smoke, P2: signierbarer Build |
| Linux Version | Sinnvoll für Forschung, Open Source und reproduzierbare Arbeitsumgebungen. | P1: Source-Smoke, P2: AppImage/Tarball |

## Zielarchitektur

### Desktop-Vollversion

- Windows bleibt primärer Nutzerkanal.
- macOS und Linux werden zunächst als Source-Smoke-Ziele geführt.
- Die Desktop-App erzeugt ein portables Exportbündel `litzentrum-library-v1.json`.
- PDF-Dateien bleiben standardmäßig lokal und werden nur als relative Pfade, Dateinamen, Hashes und optionale Inhaltsflags referenziert.

### Web/PWA-Companion

- Importiert `litzentrum-library-v1.json`.
- Funktioniert offline im Browser und auf mobilen Geräten.
- Zeigt Projekte, Quellen, Metadaten, Notizen, Zitate, Aufgaben, Zusammenfassungen und Bibliografieeinträge.
- Erlaubt Suche, Filter, Zitierkopie und Lesestatus-Ansicht.
- Schreibt in der ersten Phase nicht zurück in das Desktop-Projekt, damit es keine Konflikte mit Ordner-/Git-Struktur gibt.

### Nicht-Ziele

- Keine öffentliche Webapp, die PDFs oder komplette Literaturprojekte auf einen Server hochlädt.
- Kein nativer Android-/iOS-Vollklon mit PDF-OCR, Ollama und lokaler Projektordnerverwaltung.
- Keine Cloud-Synchronisation ohne separate Datenschutz- und Konfliktstrategie.

## Umsetzungsstatus

| Bereich | Status | Nächster Schritt |
|---|---|---|
| Desktop Windows | vorhanden | Store-Pflichtartefakte prüfen |
| macOS | nicht geprüft | Source-Smoke auf Mac Studio planen |
| Linux | nicht geprüft | sauberer Linux-Smoke mit PySide6/PyMuPDF planen |
| Exportformat | implementiert | Web/PWA-Companion gegen das neue Bundle prototypisieren |
| Web/PWA | geplant | statischen Import-/Leser-Prototyp erstellen |
| Android/iOS | abgeleitet von Web/PWA | erst nach PWA-Smoke bewerten |

## Priorisierte Aufgaben

1. DONE 2026-05-29: Exportformat `litzentrum-library-v1.json` spezifiziert und implementiert.
2. DONE 2026-05-29: Desktop-Export ohne PDF-Inhalte und ohne absolute lokale Pfade per Regressionstests abgesichert.
3. P1: Linux- und macOS-Source-Smokes für Start, Projektöffnung und BibTeX-Export durchführen.
4. P1: Web/PWA-Companion als statischen Offline-Reader für Exportbündel erstellen.
5. P2: Windows-Store-Pflichtartefakte aktualisieren: Screenshots, Listing, Datenschutz-/Support-URL, MSIX, WACK.
6. P2: Android/iOS-PWA-Smokes für Import, Suche, Zitierkopie und Offline-Start durchführen.
7. P3: Optionale Schreib-/Roundtrip-Strategie für geänderte Notizen und Aufgaben prüfen.
