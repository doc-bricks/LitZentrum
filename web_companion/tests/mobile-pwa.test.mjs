import { test } from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
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

test("Service Worker unterstützt Offline-Navigation", async () => {
  const sw = await readCompanionFile("sw.js");
  assert.match(sw, /litzentrum-web-companion-v2/);
  assert.match(sw, /self\.skipWaiting\(\)/);
  assert.match(sw, /self\.clients\.claim\(\)/);
  assert.match(sw, /event\.request\.mode === "navigate"/);
  assert.match(sw, /caches\.match\("\.\/index\.html"\)/);
});

test("Mobile CSS hält Touch-Ziele und Safe-Area stabil", async () => {
  const css = await readCompanionFile("style.css");
  assert.match(css, /\.mobile-status/);
  assert.match(css, /min-height: 44px/);
  assert.match(css, /env\(safe-area-inset-top\)/);
  assert.match(css, /@media \(max-width: 720px\)/);
});
