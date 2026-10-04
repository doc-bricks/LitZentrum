<img src="assets/banner.svg" width="100%" alt="Banner de LitZen"/>

# LitZen

[English](README.md) · [Deutsch](README_de.md) · **Español** · [中文](README_zh.md) · [日本語](README_ja.md) · [Русский](README_ru.md)

*Traducción asistida por máquina; el README en inglés es la versión de referencia.*

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-purple.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://github.com/doc-bricks/LitZentrum)
[![Version](https://img.shields.io/badge/Version-1.0.0-purple.svg)](CHANGELOG.md)

**Gestión de literatura local-first para la escritura académica.**

LitZen es una aplicación de escritorio para gestionar literatura académica en carpetas de proyecto sencillas. Combina almacenamiento local basado en JSON, manejo de PDF, notas, citas, tareas, resúmenes, exportación a BibTeX y soporte opcional de IA local mediante Ollama.

## Por dónde empezar

| Objetivo | Punto de entrada |
|---|---|
| Gestionar literatura en carpetas de proyecto locales | `python src/main.py` |
| Seguir fuentes, notas, citas, tareas y resúmenes | `src/core/` y `src/gui/` |
| Exportar citas para la escritura académica | Exportación a BibTeX y estilos de citación |
| Revisar una biblioteca en el móvil sin distribuir PDF | `web_companion/` con `litzentrum-library-v1.json` |
| Inspeccionar los contratos de datos para integración con agentes o herramientas | `schemas/litzentrum-library-v1.schema.json` y `EXPORTFORMAT.md` |

## Contexto de descubrimiento

LitZen se describe mejor como un gestor de literatura local-first, un gestor de bibliografía sin conexión, un espacio de trabajo de escritura académica respaldado por PDF y una herramienta de investigación basada en PySide6. Se diferencia deliberadamente de los gestores de referencias en la nube, las plataformas de lectura alojadas y los servicios de citación en equipo: los proyectos permanecen en carpetas normales, las exportaciones son explícitas y el compañero Web/PWA recibe un paquete JSON redactado en lugar de bibliotecas completas de PDF.

Si está comparando herramientas, use LitZen cuando quiera una alternativa local en torno a archivos PDF, BibTeX, notas, citas, seguimiento de tareas y soporte opcional de Ollama local. No es un clon de Zotero, Mendeley o JabRef, no es una biblioteca de libros electrónicos como Calibre, y no es un servicio de sincronización en la nube ni un portal de biblioteca institucional.

## Características

- Estructura de biblioteca basada en carpetas: cada fuente vive en su propio directorio.
- Integración de PDF: importación, vista previa, extracción de texto y flujos de trabajo de texto completo.
- Notas y citas: referencias de página, etiquetas y categorías.
- Gestión de tareas: tareas de todo el proyecto y por fuente.
- Resúmenes: manuales o, opcionalmente, asistidos por IA.
- Bibliografía: exportación a BibTeX y varios estilos de citación.
- Exportación para el compañero: `litzentrum-library-v1.json` para lectores Web/PWA de solo lectura sin binarios de PDF incrustados.
- Integración opcional de IA: procesamiento local con Ollama.
- Estructura de proyecto compatible con Git para trabajos de investigación versionados.
- Lector estático `web_companion/` para importar, buscar y copiar citas sin conexión en navegadores móviles.

## Capturas de pantalla

![Ventana principal](README/screenshots/main.png)

## Instalación

```bash
git clone https://github.com/doc-bricks/LitZentrum.git
cd LitZentrum
pip install -r requirements.txt
python src/main.py
```

## Requisitos

- Python 3.11+
- PySide6
- PyMuPDF
- bibtexparser
- jsonschema
- requests, solo para la integración opcional con Ollama

## Estructura del proyecto

```text
LitZentrum/
+-- src/
|   +-- main.py                 # Entry point
|   +-- core/                   # Project, source and export logic
|   +-- formats/                # .li* JSON file formats
|   +-- gui/                    # PySide6 user interface
|   +-- modules/                # Bibliography, PDF, AI and sync modules
+-- schemas/                    # JSON schemas
+-- tests/                      # Regression tests
+-- resources/                  # Icons and static assets
```

## Formatos de archivo

Todos los datos del proyecto se almacenan como JSON en UTF-8:

| Formato | Descripción |
|---|---|
| `.liproj` | Configuración del proyecto |
| `.limeta` | Metadatos de la fuente |
| `.linote` | Notas |
| `.liquote` | Citas |
| `.litask` | Tareas |
| `.lisum` | Resúmenes |
| `litzentrum-library-v1.json` | Paquete de exportación para el compañero, de solo lectura |

La exportación para el compañero contiene proyectos, fuentes, metadatos, notas, citas, tareas, resúmenes y BibTeX. No incluye archivos PDF, datos binarios de PDF ni rutas locales absolutas.

## Estructura de un proyecto

```text
MyProject/
+-- projekt_config.liproj
+-- projekt_tasks.litask
+-- projekt_notes.linote
+-- Quellen/
|   +-- Smith2023_Understanding_AI/
|   |   +-- meta.limeta
|   |   +-- notes.linote
|   |   +-- quotes.liquote
|   |   +-- tasks.litask
|   |   +-- summaries.lisum
|   |   +-- source.pdf
|   +-- Doe2024_Machine_Learning/
|       +-- ...
```

## Estilos de citación

- APA 7
- MLA 9
- Chicago
- DIN 1505-2
- Harvard

## Integración opcional de IA

LitZen puede usar una instalación local de Ollama para resúmenes asistidos por IA, extracción de citas y apoyo con metadatos, todo ello opcional.

```bash
ollama run mistral
```

## Desarrollo

```bash
pip install -r requirements.txt
python -m pytest -q
python -m py_compile src/main.py
python tests/source_platform_smoke.py
python -m pytest -q tests/test_store_materials.py
node --test web_companion/tests/library.test.mjs
node --test web_companion/tests/mobile-pwa.test.mjs
node --check web_companion/sw.js
```

Verificado el 2026-10-04: pasaron 74 pruebas de Python, la prueba de humo de la plataforma de origen y 25
pruebas del Web Companion.

## Compañero Web/PWA

La carpeta `web_companion/` contiene un lector estático sin conexión para `litzentrum-library-v1.json`.
Admite importación local, búsqueda en metadatos/notas/citas/tareas/resúmenes, copia de citas,
almacenamiento en caché mediante service worker, restauración local del último paquete cargado y una verificación previa PWA móvil para
la preparación de la instalación en Android/iOS, la navegación sin conexión y la comprobación de áreas táctiles.

## Prueba de humo de la plataforma de origen

`tests/source_platform_smoke.py` verifica la ruta de instalación desde el código fuente utilizada por los usuarios de macOS
y Linux. Crea y vuelve a abrir un proyecto temporal, muestra una fuente
a través de la ruta GUI sin pantalla (offscreen), exporta BibTeX y valida
`litzentrum-library-v1.json`. El flujo de trabajo de GitHub
`.github/workflows/platform-smoke.yml` ejecuta la misma prueba en Ubuntu y macOS.

## Windows Store

`store_package.json`, `STORE_LISTING.md`, `PRIVACY_POLICY.md`, `SUPPORT.md`,
`WINDOWS_STORE_PREP.md` y `generate_store_screenshots.py` recogen la línea base actual de
Windows Store para LitZen. El estado actual abarca los metadatos públicos,
las páginas de soporte/privacidad y un conjunto reproducible de cuatro capturas de pantalla de la Store en
`README/screenshots/store/`. Una ruta de compilación reproducible de EXE/MSIX para Windows y WACK
siguen siendo los próximos pasos explícitos.

## Licencia

AGPL v3. Consulte [LICENSE](LICENSE).

Este proyecto utiliza PySide6 (LGPL) y PyMuPDF (AGPL).

## Responsabilidad

Este proyecto es una donación de código abierto sin remuneración. La responsabilidad se limita al dolo y la negligencia grave conforme a la sección 521 del Código Civil alemán (BGB). Úsese bajo su propio riesgo. No se asume ninguna garantía, garantía de mantenimiento ni idoneidad para un fin determinado.
