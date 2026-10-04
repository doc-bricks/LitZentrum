<img src="assets/banner.svg" width="100%" alt="LitZen 横幅"/>

# LitZen

[English](README.md) · [Deutsch](README_de.md) · [Español](README_es.md) · **中文** · [日本語](README_ja.md) · [Русский](README_ru.md)

*机器辅助翻译；以英文 README 为准。*

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-purple.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://github.com/doc-bricks/LitZentrum)
[![Version](https://img.shields.io/badge/Version-1.0.0-purple.svg)](CHANGELOG.md)

**面向学术写作的本地优先文献管理工具。**

LitZen 是一款桌面应用程序，用于在普通项目文件夹中管理学术文献。它结合了基于 JSON 的本地存储、PDF 处理、笔记、引文、任务、摘要、BibTeX 导出，以及通过 Ollama 提供的可选本地 AI 支持。

## 从这里开始

| 目标 | 入口 |
|---|---|
| 在本地项目文件夹中管理文献 | `python src/main.py` |
| 跟踪文献来源、笔记、引文、任务和摘要 | `src/core/` 和 `src/gui/` |
| 为学术写作导出引用 | BibTeX 导出和引用样式 |
| 在移动设备上查看文献库而无需分发 PDF | `web_companion/` 搭配 `litzentrum-library-v1.json` |
| 检查用于智能体或工具集成的数据契约 | `schemas/litzentrum-library-v1.schema.json` 和 `EXPORTFORMAT.md` |

## 发现背景

LitZen 最适合被描述为一款本地优先的文献管理器、离线参考文献管理器、以 PDF 为支撑的学术写作工作空间，以及基于 PySide6 的研究工具。它有意区别于云端参考文献管理器、托管式阅读平台和团队引用服务：项目保存在普通文件夹中，导出是显式进行的，而 Web/PWA 配套应用接收的是经过脱敏的 JSON 数据包，而不是完整的 PDF 库。

如果您正在比较各种工具，当您需要一个围绕 PDF 文件、BibTeX、笔记、引文、任务跟踪以及可选本地 Ollama 支持的本地替代方案时，请使用 LitZen。它不是 Zotero、Mendeley 或 JabRef 的克隆，不是 Calibre 那样的电子书库，也不是云同步或机构图书馆门户。

## 功能特性

- 基于文件夹的文献库结构：每个文献来源位于各自的目录中。
- PDF 集成：导入、预览、文本提取和全文工作流。
- 笔记和引文：页码引用、标签和分类。
- 任务管理：项目级任务和单个文献来源的任务。
- 摘要：手动撰写，或可选择由 AI 辅助生成。
- 参考文献：BibTeX 导出和多种引用样式。
- 配套导出：`litzentrum-library-v1.json`，供只读的 Web/PWA 阅读器使用，不嵌入 PDF 二进制文件。
- 可选的 AI 集成：使用 Ollama 在本地处理。
- 对 Git 友好的项目布局，适用于版本化的研究工作。
- 静态的 `web_companion/` 阅读器，可在移动浏览器上离线导入、搜索并复制引用。

## 截图

![主窗口](README/screenshots/main.png)

## 安装

```bash
git clone https://github.com/doc-bricks/LitZentrum.git
cd LitZentrum
pip install -r requirements.txt
python src/main.py
```

## 环境要求

- Python 3.11+
- PySide6
- PyMuPDF
- bibtexparser
- jsonschema
- requests，仅用于可选的 Ollama 集成

## 项目结构

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

## 文件格式

所有项目数据均以 UTF-8 编码的 JSON 存储：

| 格式 | 说明 |
|---|---|
| `.liproj` | 项目配置 |
| `.limeta` | 文献来源元数据 |
| `.linote` | 笔记 |
| `.liquote` | 引文 |
| `.litask` | 任务 |
| `.lisum` | 摘要 |
| `litzentrum-library-v1.json` | 只读的配套导出数据包 |

配套导出包含项目、文献来源、元数据、笔记、引文、任务、摘要和 BibTeX。它不包含 PDF 文件、PDF 二进制数据或本地绝对路径。

## 项目布局

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

## 引用样式

- APA 7
- MLA 9
- Chicago
- DIN 1505-2
- Harvard

## 可选的 AI 集成

LitZen 可以使用本地安装的 Ollama，提供可选的 AI 辅助摘要、引文提取和元数据支持。

```bash
ollama run mistral
```

## 开发

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

已于 2026-10-04 验证：74 项 Python 测试、平台源码冒烟测试以及 25
项 Web Companion 测试均已通过。

## Web/PWA 配套应用

`web_companion/` 文件夹包含一个用于 `litzentrum-library-v1.json` 的静态离线阅读器。
它支持本地导入、跨元数据/笔记/引文/任务/摘要的搜索、引用复制、
service worker 缓存、本地恢复上次加载的数据包，以及面向移动端 PWA 的预检，涵盖
Android/iOS 安装就绪性、离线导航和触控目标检查。

## 平台源码冒烟测试

`tests/source_platform_smoke.py` 验证 macOS
和 Linux 用户所使用的源码安装路径。它会创建并重新打开一个临时项目，通过离屏 GUI 路径
显示一个文献来源，导出 BibTeX 并验证
`litzentrum-library-v1.json`。GitHub 工作流
`.github/workflows/platform-smoke.yml` 在 Ubuntu 和 macOS 上运行同样的冒烟测试。

## Windows Store

`store_package.json`、`STORE_LISTING.md`、`PRIVACY_POLICY.md`、`SUPPORT.md`、
`WINDOWS_STORE_PREP.md` 和 `generate_store_screenshots.py` 记录了 LitZen 当前的
Windows Store 基线。当前状态涵盖公开元数据、
支持/隐私页面，以及位于
`README/screenshots/store/` 下可复现的四张 Store 截图。可复现的 Windows EXE/MSIX 构建路径和 WACK
仍是接下来明确要做的步骤。

## 许可证

AGPL v3。参见 [LICENSE](LICENSE)。

本项目使用 PySide6 (LGPL) 和 PyMuPDF (AGPL)。

## 责任声明

本项目是无偿的开源捐赠。根据《德国民法典》第 521 条，责任仅限于故意和重大过失。使用风险自负。不承担任何保证、维护保证或适用于特定目的的责任。
