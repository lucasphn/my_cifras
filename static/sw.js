const SHELL_CACHE = 'mycifras-shell-v5';
const SHELL_URLS = [
  '/static/brand/logo-light.svg',
  '/static/brand/favicon.svg',
  '/static/manifest.json',
];

self.addEventListener('install', function(e) {
  e.waitUntil(
    caches.open(SHELL_CACHE)
      .then(function(c) { return c.addAll(SHELL_URLS); })
      .then(function() { return self.skipWaiting(); })
      .catch(function() { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function(e) {
  e.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(
        keys.filter(function(k) { return k !== SHELL_CACHE; })
            .map(function(k) { return caches.delete(k); })
      );
    }).then(function() { return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function(e) {
  var url = new URL(e.request.url);

  // Só processa http/https
  if (url.protocol !== 'http:' && url.protocol !== 'https:') return;
  // API calls — pass through
  if (url.pathname.startsWith('/api/')) return;
  // Auth, login e raiz — sempre network (sessão varia por usuário)
  if (url.pathname === '/' ||
      url.pathname.startsWith('/login') ||
      url.pathname.startsWith('/oauth')) return;

  // Assets estáticos: stale-while-revalidate
  e.respondWith(
    caches.open(SHELL_CACHE).then(function(cache) {
      return cache.match(e.request).then(function(cached) {
        var network = fetch(e.request).then(function(resp) {
          if (resp.ok && e.request.method === 'GET') {
            cache.put(e.request, resp.clone());
          }
          return resp;
        }).catch(function() { return cached; });
        return cached || network;
      });
    })
  );
});
