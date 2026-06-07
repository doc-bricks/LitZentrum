import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile, access } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));

async function readCompanionFile(name) {
  return readFile(join(root, name), "utf8");
}

test("manifest ist als Android-/iOS-PWA installierbar", async () => {
  const manifest = JSON.parse(await readCompanionFile("manifest.webmanifest"));
  assert.equal(manifest.display, "standalone");
  assert.equal(manifest.start_url, "./");
  assert.equal(manifest.lang, "de");
  assert.ok(manifest.theme_color);
  assert.ok(manifest.background_color);
  assert.ok(Array.isArray(manifest.icons));
  assert.ok(manifest.icons.length >= 1);
  assert.ok(manifest.id, "manifest.id fehlt – Android-PWA-Identität instabil");
});

test("Icon-Dateien existieren physisch", async () => {
  const icons = [
    "icons/Icon-192.png",
    "icons/Icon-512.png",
    "icons/Icon-maskable-192.png",
    "icons/Icon-maskable-512.png",
  ];
  for (const icon of icons) {
    await assert.doesNotReject(
      access(join(root, icon)),
      `Icon-Datei fehlt: ${icon}`
    );
  }
});

test("HTML enthält Mobile-Status und sichere Viewport-Metadaten", async () => {
  const html = await readCompanionFile("index.html");
  assert.match(html, /<meta name="viewport" content="width=device-width, initial-scale=1">/);
  assert.match(html, /id="mobile-status"/);
  assert.match(html, /id="android-status"/);
  assert.match(html, /id="ios-status"/);
  assert.match(html, /id="offline-status"/);
});

test("App-Code aktualisiert Android-, iOS- und Offline-Status", async () => {
  const app = await readCompanionFile("app.js");
  assert.match(app, /function updateMobilePwaStatus\(\)/);
  assert.match(app, /display-mode: standalone/);
  assert.match(app, /android/);
  assert.match(app, /iphone\|ipad\|ipod/);
  assert.match(app, /Offline-Cache bereit/);
});

// Hinweis: Die folgenden zwei Tests sind statische Quelltext-Assertions (kein Browser-Runtime).
// SW-Verhalten (Offline-Fallback mit ignoreSearch) und Badge-Laufzeit-Verhalten können im
// Node.js-Testharness nicht behavioral abgedeckt werden (kein Service-Worker-API, kein DOM).

test("Service Worker unterstützt Offline-Navigation", async () => {
  const sw = await readCompanionFile("sw.js");
  assert.match(sw, /litzentrum-web-companion-v3/);
  assert.match(sw, /self\.skipWaiting\(\)/);
  assert.match(sw, /self\.clients\.claim\(\)/);
  assert.match(sw, /event\.request\.mode === "navigate"/);
  assert.match(sw, /caches\.match\("\.\/index\.html"\)/);
  assert.match(sw, /ignoreSearch:\s*true/, "caches.match muss ignoreSearch:true setzen – sonst schlägt Offline-Fallback bei URLs mit Query-Params fehl");
});

test("Aufgaben-Badge erkennt alle Done-Status-Varianten", async () => {
  const app = await readCompanionFile("app.js");
  assert.match(app, /isDone\(task\.status\)/, "Badge-Logik muss isDone() aus library.js verwenden");
  const lib = await readCompanionFile("library.js");
  assert.match(lib, /"completed"/, "isDone() muss 'completed' als erledigt kennen");
  assert.match(lib, /"erledigt"/, "isDone() muss 'erledigt' als erledigt kennen");
  assert.match(lib, /"closed"/, "isDone() muss 'closed' als erledigt kennen");
});

test("Mobile CSS hält Touch-Ziele und Safe-Area stabil", async () => {
  const css = await readCompanionFile("style.css");
  assert.match(css, /\.mobile-status/);
  assert.match(css, /min-height: 44px/);
  assert.match(css, /env\(safe-area-inset-top\)/);
  assert.match(css, /@media \(max-width: 720px\)/);
});
