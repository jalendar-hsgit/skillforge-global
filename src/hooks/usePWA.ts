import { useEffect, useState } from 'react';

/**
 * Hook to initialize and manage PWA functionality
 * Handles service worker registration, offline detection, and sync
 */
export const usePWA = () => {
  const [isOnline, setIsOnline] = useState(true);
  const [swRegistered, setSwRegistered] = useState(false);
  const [installPrompt, setInstallPrompt] = useState<any>(null);
  const [isPWAInstalled, setIsPWAInstalled] = useState(false);
  const [pendingSyncs, setPendingSyncs] = useState(0);

  useEffect(() => {
    // Check if running as PWA
    const isPWA = window.matchMedia('(display-mode: standalone)').matches ||
                  (window.navigator as any).standalone === true;
    setIsPWAInstalled(isPWA);

    // Register Service Worker
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker
        .register('/service-worker.js')
        .then((registration) => {
          console.log('Service Worker registered successfully:', registration);
          setSwRegistered(true);

          // Check for updates periodically
          setInterval(() => {
            registration.update();
          }, 60000); // Check every 60 seconds
        })
        .catch((error) => {
          console.error('Service Worker registration failed:', error);
        });
    }

    // Listen for online/offline events
    window.addEventListener('online', () => setIsOnline(true));
    window.addEventListener('offline', () => setIsOnline(false));

    // Handle install prompt
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      setInstallPrompt(e);
    });

    // Log app installed
    window.addEventListener('appinstalled', () => {
      console.log('PWA was installed');
      setIsPWAInstalled(true);
      logPWAEvent('install');
    });

    // Initial online status
    setIsOnline(navigator.onLine);

    return () => {
      window.removeEventListener('online', () => {});
      window.removeEventListener('offline', () => {});
    };
  }, []);

  // Listen for sync messages from service worker
  useEffect(() => {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data.type === 'SYNC_SUCCESS') {
          console.log('Sync successful:', event.data.sync_id);
          logPWAEvent('sync_success');
        } else if (event.data.type === 'SYNC_FAILED') {
          console.error('Sync failed:', event.data.sync_id);
          logPWAEvent('sync_failed');
        }
      });
    }
  }, []);

  // Request notification permission
  const requestNotificationPermission = async () => {
    if ('Notification' in window && Notification.permission === 'default') {
      const permission = await Notification.requestPermission();
      if (permission === 'granted') {
        // Subscribe to push notifications
        if ('serviceWorker' in navigator && 'PushManager' in window) {
          const registration = await navigator.serviceWorker.ready;
          try {
            // Get VAPID public key from config endpoint
            const config = await fetch('/api/v1x/pwa/config').then(r => r.json());
            
            const subscription = await registration.pushManager.subscribe({
              userVisibleOnly: true,
              applicationServerKey: config.vapid_public_key,
            });

            // Save subscription to backend
            await fetch('/api/v1x/pwa/notifications/subscribe', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(subscription),
            });

            logPWAEvent('notifications_enabled');
          } catch (error) {
            console.error('Failed to subscribe to push notifications:', error);
          }
        }
      }
    }
  };

  // Trigger install prompt
  const installPWA = async () => {
    if (!installPrompt) return;

    installPrompt.prompt();
    const { outcome } = await installPrompt.userChoice;
    console.log(`User response to install prompt: ${outcome}`);

    if (outcome === 'accepted') {
      logPWAEvent('install_prompt', { outcome: 'accepted' });
    }

    setInstallPrompt(null);
  };

  // Queue operation for offline sync
  const queueOfflineOperation = async (
    operationType: string,
    endpoint: string,
    payload: any,
    method = 'POST'
  ) => {
    if (!isOnline) {
      // Save to IndexedDB for later sync
      const db = await openIndexedDB();
      const tx = db.transaction('sync_queue', 'readwrite');
      tx.store.add({
        operationType,
        endpoint,
        payload,
        method,
        timestamp: Date.now(),
      });

      // Schedule background sync
      if ('serviceWorker' in navigator) {
        const registration = await navigator.serviceWorker.ready;
        if ('sync' in registration) {
          await (registration as any).sync.register('sync-submissions');
        }
      }
    } else {
      // Execute immediately
      try {
        const response = await fetch(endpoint, {
          method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });

        if (response.ok) {
          logPWAEvent('sync_success');
        }
      } catch (error) {
        console.error('Operation failed:', error);
        // Fallback to offline queue
        queueOfflineOperation(operationType, endpoint, payload, method);
      }
    }
  };

  // Cache a resource for offline use
  const cacheResource = async (cacheKey: string, resourceType: string, data: any) => {
    try {
      await fetch('/api/v1x/pwa/cache', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cache_key: cacheKey,
          resource_type: resourceType,
          data,
          expires_in_hours: 168,
        }),
      });

      logPWAEvent('cache_stored');
    } catch (error) {
      console.error('Failed to cache resource:', error);
    }
  };

  // Get cached resource
  const getCachedResource = async (cacheKey: string) => {
    try {
      const response = await fetch(`/api/v1x/pwa/cache/${cacheKey}`);
      if (response.ok) {
        const data = await response.json();
        logPWAEvent('cache_hit');
        return data.data;
      }
    } catch (error) {
      console.error('Failed to get cached resource:', error);
    }
    logPWAEvent('cache_miss');
    return null;
  };

  // Log PWA event
  const logPWAEvent = async (eventType: string, eventData?: any) => {
    try {
      await fetch('/api/v1x/pwa/analytics/event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event_type: eventType,
          event_data: eventData,
        }),
      }).catch(() => {
        // Silently fail if offline
      });
    } catch (error) {
      console.error('Failed to log PWA event:', error);
    }
  };

  return {
    isOnline,
    swRegistered,
    isPWAInstalled,
    installPrompt,
    pendingSyncs,
    installPWA,
    requestNotificationPermission,
    queueOfflineOperation,
    cacheResource,
    getCachedResource,
    logPWAEvent,
  };
};

// Helper to open IndexedDB
async function openIndexedDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('skillforge', 1);

    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);

    request.onupgradeneeded = (event) => {
      const db = (event.target as IDBOpenDBRequest).result;
      if (!db.objectStoreNames.contains('sync_queue')) {
        db.createObjectStore('sync_queue', { autoIncrement: true });
      }
      if (!db.objectStoreNames.contains('cache')) {
        db.createObjectStore('cache', { keyPath: 'cacheKey' });
      }
    };
  });
}
