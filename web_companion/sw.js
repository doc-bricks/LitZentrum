const CACHE_NAME = "litzentrum-web-companion-v2";
const ASSETS = [
  "./",
  "./index.html",
  "./style.css",
  "./app.js",
  "./library.js",
  "./manifest.webmanifest",
  "../LitZentrum.ico"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(key => key !== CACHE_NAME)
          .map(key => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", event => {
  if (event.request.method !== "GET") {
    return;
  }
  event.respondWith(
    fetch(event.request).then(response => {
      const url = new URL(event.request.url);
      if (url.origin === self.location.origin && response.ok) {
        const copy = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(event.request, copy));
      }
      return response;
    }).catch(() =>
      caches.match(event.request).then(cached =>
        cached || (event.request.mode === "navigate" ? caches.match("./index.html") : undefined)
      )
    )
  );
});
