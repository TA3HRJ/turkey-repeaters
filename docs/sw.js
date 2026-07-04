/*
 * Service worker for Turkey Repeaters.
 *
 * Strategy:
 *  - Navigations (index.html): network-first, cache fallback — the app is
 *    always fresh online, and still opens fully offline.
 *  - Everything else (data JSON, CDN libs, tiles, icons): stale-while-
 *    revalidate — instant loads from cache, silently refreshed in background.
 *
 * Bump CACHE_VERSION when the precache list changes shape.
 */
const CACHE_VERSION = "v1";
const CACHE_NAME = `ta-repeaters-${CACHE_VERSION}`;

const PRECACHE = [
  "./",
  "./index.html",
  "./manifest.json",
  "./data/repeaters.min.json",
  "./assets/icon-192.png",
  "./assets/icon-512.png",
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then((c) => c.addAll(PRECACHE))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((k) => k.startsWith("ta-repeaters-") && k !== CACHE_NAME)
            .map((k) => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;

  // Never intercept Firebase/Google auth+firestore traffic.
  const url = new URL(req.url);
  if (/googleapis\.com|firebaseapp\.com|firestore/.test(url.host)) return;

  if (req.mode === "navigate") {
    e.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE_NAME).then((c) => c.put("./index.html", copy));
          return res;
        })
        .catch(() => caches.match("./index.html"))
    );
    return;
  }

  e.respondWith(
    caches.match(req).then((cached) => {
      const refresh = fetch(req)
        .then((res) => {
          if (res && res.ok) {
            const copy = res.clone();
            caches.open(CACHE_NAME).then((c) => c.put(req, copy));
          }
          return res;
        })
        .catch(() => cached);
      return cached || refresh;
    })
  );
});
