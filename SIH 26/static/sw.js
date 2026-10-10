const CACHE_NAME = 'smart-edu-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/static/css/style.css',
  '/static/css/components.css',
  '/static/js/app.js',
  '/static/js/translations.js',
  '/static/js/charts.js',
  '/static/js/adaptive_quiz.js',
  '/static/js/ai_tutor.js',
  '/static/js/offline.js'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS_TO_CACHE))
  );
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((res) => {
      return res || fetch(e.request).catch(() => {
        // Fallback for offline network requests
        return caches.match('/');
      });
    })
  );
});
