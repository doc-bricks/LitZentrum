<img src="assets/banner.svg" width="100%" alt="LitZen バナー"/>

# LitZen

[English](README.md) · [Deutsch](README_de.md) · [Español](README_es.md) · [中文](README_zh.md) · **日本語** · [Русский](README_ru.md)

*機械支援による翻訳です。正式な内容は英語版 README が優先されます。*

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-purple.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://github.com/doc-bricks/LitZentrum)
[![Version](https://img.shields.io/badge/Version-1.0.0-purple.svg)](CHANGELOG.md)

**学術的な執筆のための、ローカルファーストな文献管理。**

LitZen は、通常のプロジェクトフォルダ内で学術文献を管理するためのデスクトップアプリケーションです。ローカルの JSON ベースのストレージ、PDF の取り扱い、ノート、引用、タスク、要約、BibTeX エクスポート、そして Ollama によるオプションのローカル AI サポートを組み合わせています。

## はじめに

| 目的 | エントリーポイント |
|---|---|
| ローカルのプロジェクトフォルダで文献を管理する | `python src/main.py` |
| 文献、ノート、引用、タスク、要約を追跡する | `src/core/` と `src/gui/` |
| 学術的な執筆のために引用文献をエクスポートする | BibTeX エクスポートと引用スタイル |
| PDF を配布せずにモバイルでライブラリを確認する | `web_companion/` と `litzentrum-library-v1.json` |
| エージェントやツール連携のためのデータ契約を確認する | `schemas/litzentrum-library-v1.schema.json` と `EXPORTFORMAT.md` |

## 発見のための背景

LitZen は、ローカルファーストの文献マネージャー、オフラインの文献目録マネージャー、PDF を基盤とする学術執筆ワークスペース、そして PySide6 製のリサーチツールとして位置づけるのが最も適切です。クラウド型の文献管理ツール、ホスト型の閲覧プラットフォーム、チーム向けの引用サービスとは意図的に異なります。プロジェクトは通常のフォルダに置かれ、エクスポートは明示的に行われ、Web/PWA コンパニオンには PDF ライブラリ全体ではなく、秘匿情報を除いた JSON バンドルが渡されます。

ツールを比較検討している場合、PDF ファイル、BibTeX、ノート、引用、タスク管理、そしてオプションのローカル Ollama サポートを中心としたローカルな代替手段が欲しいときに LitZen を使ってください。Zotero、Mendeley、JabRef のクローンではなく、Calibre のような電子書籍ライブラリでもなく、クラウド同期や機関向けライブラリポータルでもありません。

## 機能

- フォルダベースのライブラリ構造:各文献はそれぞれ専用のディレクトリに置かれます。
- PDF 連携:インポート、プレビュー、テキスト抽出、全文ワークフロー。
- ノートと引用:ページ参照、タグ、カテゴリ。
- タスク管理:プロジェクト全体および文献ごとのタスク。
- 要約:手動、またはオプションで AI 支援。
- 文献目録:BibTeX エクスポートと複数の引用スタイル。
- コンパニオンエクスポート:PDF バイナリを埋め込まない、読み取り専用の Web/PWA リーダー向け `litzentrum-library-v1.json`。
- オプションの AI 連携:Ollama によるローカル処理。
- バージョン管理された研究作業のための Git フレンドリーなプロジェクト構成。
- モバイルブラウザでのオフラインインポート、検索、引用コピーに対応した静的な `web_companion/` リーダー。

## スクリーンショット

![メインウィンドウ](README/screenshots/main.png)

## インストール

```bash
git clone https://github.com/doc-bricks/LitZentrum.git
cd LitZentrum
pip install -r requirements.txt
python src/main.py
```

## 要件

- Python 3.11+
- PySide6
- PyMuPDF
- bibtexparser
- jsonschema
- requests(オプションの Ollama 連携にのみ必要)

## プロジェクト構成

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

## ファイル形式

すべてのプロジェクトデータは UTF-8 の JSON として保存されます。

| 形式 | 説明 |
|---|---|
| `.liproj` | プロジェクト設定 |
| `.limeta` | 文献のメタデータ |
| `.linote` | ノート |
| `.liquote` | 引用 |
| `.litask` | タスク |
| `.lisum` | 要約 |
| `litzentrum-library-v1.json` | 読み取り専用のコンパニオンエクスポートバンドル |

コンパニオンエクスポートには、プロジェクト、文献、メタデータ、ノート、引用、タスク、要約、BibTeX が含まれます。PDF ファイル、PDF のバイナリデータ、ローカルの絶対パスは含まれません。

## プロジェクトレイアウト

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

## 引用スタイル

- APA 7
- MLA 9
- Chicago
- DIN 1505-2
- Harvard

## オプションの AI 連携

LitZen は、ローカルにインストールされた Ollama を利用して、AI 支援による要約、引用の抽出、メタデータのサポートを行うことができます(オプション)。

```bash
ollama run mistral
```

## 開発

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

2026-10-04 に検証済み:74 件の Python テスト、プラットフォームのソーススモーク、および 25 件の
Web Companion テストが成功しました。

## Web/PWA コンパニオン

`web_companion/` フォルダには、`litzentrum-library-v1.json` 用の静的なオフラインリーダーが含まれています。
ローカルでのインポート、メタデータ/ノート/引用/タスク/要約を横断した検索、引用のコピー、
サービスワーカーによるキャッシュ、最後に読み込んだバンドルのローカル復元に対応しており、
さらに Android/iOS でのインストール可否、オフラインナビゲーション、タッチターゲットのチェックを行う
モバイル PWA プリフライトも備えています。

## プラットフォームのソーススモーク

`tests/source_platform_smoke.py` は、macOS と Linux のユーザーが利用するソースインストールの経路を検証します。
一時プロジェクトを作成して開き直し、1 件の文献をオフスクリーンの GUI 経路で表示し、
BibTeX をエクスポートして `litzentrum-library-v1.json` を検証します。GitHub ワークフロー
`.github/workflows/platform-smoke.yml` は、同じスモークを Ubuntu と macOS で実行します。

## Windows ストア

`store_package.json`、`STORE_LISTING.md`、`PRIVACY_POLICY.md`、`SUPPORT.md`、
`WINDOWS_STORE_PREP.md`、`generate_store_screenshots.py` は、LitZen の現在の
Windows ストア向けベースラインをまとめたものです。現時点では、公開メタデータ、
サポート/プライバシーのページ、そして `README/screenshots/store/` 配下の再現可能な
4 枚構成のストア用スクリーンショットセットが対象です。再現可能な Windows EXE/MSIX のビルド手順と WACK は、
今後の明確な次のステップとして残っています。

## ライセンス

AGPL v3。[LICENSE](LICENSE) を参照してください。

このプロジェクトは PySide6 (LGPL) と PyMuPDF (AGPL) を使用しています。

## 免責

このプロジェクトは無償のオープンソースの寄贈です。責任は、ドイツ民法典第 521 条に基づき、故意および重過失に限定されます。自己責任でご使用ください。保証、保守の保証、特定目的への適合性は一切想定されていません。
