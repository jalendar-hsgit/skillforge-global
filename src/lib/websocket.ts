/**
 * WebSocket client for real-time notifications
 */

export interface Notification {
  id: number;
  user_id: number;
  type: string;
  title: string;
  message: string;
  data?: Record<string, any>;
  is_read: boolean;
  created_at: string;
  read_at?: string;
}

export interface NotificationEvent {
  event: string;
  data: Notification | any;
}

type NotificationCallback = (notification: Notification) => void;

class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private token: string | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;
  private listeners: Set<NotificationCallback> = new Set();
  private isConnected = false;

  constructor() {
    const baseUrl = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
    // Convert http/https to ws/wss
    this.url = baseUrl
      .replace(/^https/, 'wss')
      .replace(/^http/, 'ws')
      .replace(/\/$/, '');
  }

  connect(token: string): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.isConnected && this.ws?.readyState === WebSocket.OPEN) {
        resolve();
        return;
      }

      this.token = token;
      const wsUrl = `${this.url}/api/v1x/notifications/ws?token=${encodeURIComponent(token)}`;

      try {
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('[WebSocket] Connected');
          this.isConnected = true;
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (err) {
            console.error('[WebSocket] Failed to parse message:', err);
          }
        };

        this.ws.onerror = (error) => {
          console.error('[WebSocket] Error:', error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('[WebSocket] Disconnected');
          this.isConnected = false;
          this.attemptReconnect();
        };
      } catch (err) {
        reject(err);
      }
    });
  }

  private handleMessage(data: NotificationEvent) {
    if (data.event === 'notification' && data.data) {
      // Notify all listeners
      this.listeners.forEach(callback => {
        try {
          callback(data.data);
        } catch (err) {
          console.error('Error in notification callback:', err);
        }
      });

      // Show browser notification if enabled
      this.showBrowserNotification(data.data);
    }
  }

  private showBrowserNotification(notification: Notification) {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(notification.title, {
        body: notification.message,
        icon: '/logo.png',
        tag: `notification-${notification.id}`,
      });
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
      console.log(`[WebSocket] Attempting to reconnect in ${delay}ms...`);

      setTimeout(() => {
        if (this.token) {
          this.connect(this.token).catch(err => {
            console.error('[WebSocket] Reconnect failed:', err);
          });
        }
      }, delay);
    }
  }

  subscribe(callback: NotificationCallback): () => void {
    this.listeners.add(callback);

    // Return unsubscribe function
    return () => {
      this.listeners.delete(callback);
    };
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.isConnected = false;
    }
  }

  send(message: any) {
    if (this.isConnected && this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('[WebSocket] Not connected, message not sent');
    }
  }

  isReady(): boolean {
    return this.isConnected && this.ws?.readyState === WebSocket.OPEN;
  }
}

// Singleton instance
let wsClient: WebSocketClient | null = null;

export function getWebSocketClient(): WebSocketClient {
  if (!wsClient) {
    wsClient = new WebSocketClient();
  }
  return wsClient;
}

export default WebSocketClient;
