/**
 * Service Worker for Progressive Web App
 * Handles offline support, caching, and background sync
 */

const CACHE_NAME = 'skillforge-v1';
const RUNTIME_CACHE = 'skillforge-runtime';
const API_CACHE = 'skillforge-api';

// Files to cache on install
const CACHE_URLS = [
  '/',
  '/index.html',
  '/offline.html',
  '/manifest.json',
  '/_next/static/chunks/main.js',
];

// Install event - cache essential files
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(CACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((name) => name !== CACHE_NAME && name !== RUNTIME_CACHE && name !== API_CACHE)
            .map((name) => caches.delete(name))
        );
      })
      .then(() => self.clients.claim())
  );
});

// Fetch event - network first, fallback to cache
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip chrome extensions and other non-http requests
  if (!url.protocol.startsWith('http')) {
    return;
  }

  // API requests - network first with API cache
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response.ok) {
            const cache = caches.open(API_CACHE);
            cache.then((c) => c.put(request, response.clone()));
          }
          return response;
        })
        .catch(() => {
          return caches.match(request)
            .then((cached) => cached || cacheNotFound());
        })
    );
    return;
  }

  // Static assets - cache first
  if (
    request.destination === 'image' ||
    request.destination === 'font' ||
    request.destination === 'script' ||
    request.destination === 'style'
  ) {
    event.respondWith(
      caches.match(request)
        .then((cached) => {
          if (cached) return cached;
          return fetch(request)
            .then((response) => {
              if (response.ok) {
                const cache = caches.open(RUNTIME_CACHE);
                cache.then((c) => c.put(request, response.clone()));
              }
              return response;
            })
            .catch(() => cacheNotFound());
        })
    );
    return;
  }

  // HTML pages - network first with stale-while-revalidate
  if (request.destination === 'document') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response.ok) {
            const cache = caches.open(RUNTIME_CACHE);
            cache.then((c) => c.put(request, response.clone()));
          }
          return response;
        })
        .catch(() => {
          return caches.match(request)
            .then((cached) => cached || cacheNotFound());
        })
    );
    return;
  }
});

// Background sync for offline submissions
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-submissions') {
    event.waitUntil(syncOfflineSubmissions());
  }
});

async function syncOfflineSubmissions() {
  try {
    // Get pending syncs from IndexedDB
    const pending = await getPendingSyncs();
    
    for (const sync of pending) {
      try {
        const response = await fetch(sync.endpoint, {
          method: sync.method || 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(sync.payload),
        });

        if (response.ok) {
          await removeSyncItem(sync.id);
          // Notify all clients
          self.clients.matchAll().then((clients) => {
            clients.forEach((client) => {
              client.postMessage({
                type: 'SYNC_SUCCESS',
                sync_id: sync.id,
              });
            });
          });
        }
      } catch (error) {
        console.error('Sync failed:', error);
      }
    }
  } catch (error) {
    console.error('Background sync error:', error);
  }
}

async function getPendingSyncs() {
  // Mock - in real app, would query IndexedDB
  return [];
}

async function removeSyncItem(id) {
  // Mock - in real app, would delete from IndexedDB
}

function cacheNotFound() {
  return new Response(
    JSON.stringify({
      offline: true,
      message: 'You appear to be offline. Some features may not be available.',
    }),
    {
      status: 200,
      statusText: 'OK',
      headers: new Headers({
        'Content-Type': 'application/json',
      }),
    }
  );
}

// Push notification event
self.addEventListener('push', (event) => {
  if (!event.data) return;

  const options = {
    body: event.data.text(),
    icon: '/icon-192x192.png',
    badge: '/badge-72x72.png',
    vibrate: [200, 100, 200],
    tag: 'skillforge-notification',
    requireInteraction: false,
  };

  event.waitUntil(
    self.registration.showNotification('SkillForge Global', options)
  );
});

// Notification click event
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  event.waitUntil(
    clients.matchAll({ type: 'window' })
      .then((clientList) => {
        // Check if window is already open
        for (const client of clientList) {
          if (client.url === '/' && 'focus' in client) {
            return client.focus();
          }
        }
        // Open new window if not found
        if (clients.openWindow) {
          return clients.openWindow('/');
        }
      })
  );
});
