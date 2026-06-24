/**
 * QuickCards — Service Worker (PWA)
 *
 * Provides offline caching for the app shell so the app
 * loads instantly on repeat visits and is installable.
 */

const CACHE_NAME = 'quickcards-v1';
const ASSETS = [
  '/',
  '/index.html',
  '/style.css',
  '/js/state.js',
  '/js/api.js',
  '/js/ui.js',
  '/js/video.js',
  '/manifest.json',
];

// Install: pre-cache app shell
self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)));
  self.skipWaiting();
});

// Activate: clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))
      )
  );
  self.clients.claim();
});

// Fetch: serve from cache first, fall back to network
self.addEventListener('fetch', (event) => {
  // Skip non-GET and API requests
  if (event.request.method !== 'GET') return;
  if (event.request.url.includes('/generate')) return;
  if (event.request.url.includes('/health')) return;

  event.respondWith(
    caches.match(event.request).then((cached) => {
      return (
        cached ||
        fetch(event.request).then((response) => {
          // Cache successful responses
          if (response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return response;
        })
      );
    })
  );
});
