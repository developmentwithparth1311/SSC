import { WS_URL } from './api';

export class ChatSocket {
  constructor(token, handlers = {}) {
    this.token = token;
    this.handlers = handlers;
    this.ws = null;
    this.alive = false;
    this.reconnectTimer = null;
    this.pingTimer = null;
  }

  async connect() {
    if (!this.token) return;
    try {
      let url = WS_URL;
      try {
        const { api } = await import('./api');
        const { data } = await api.post('/auth/ws-ticket');
        if (data?.ticket) {
          url = `${WS_URL}?ticket=${encodeURIComponent(data.ticket)}`;
        } else {
          url = `${WS_URL}?token=${encodeURIComponent(this.token)}`;
        }
      } catch {
        url = `${WS_URL}?token=${encodeURIComponent(this.token)}`;
      }
      this.ws = new WebSocket(url);
    } catch (e) {
      console.error('ws ctor', e);
      return;
    }
    this.ws.onopen = () => {
      this.alive = true;
      this.handlers.onOpen && this.handlers.onOpen();
      this.pingTimer = setInterval(() => this.send({ type: 'ping' }), 25000);
    };
    this.ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);
        this.handlers.onMessage && this.handlers.onMessage(data);
      } catch {}
    };
    this.ws.onclose = () => {
      this.alive = false;
      if (this.pingTimer) { clearInterval(this.pingTimer); this.pingTimer = null; }
      this.handlers.onClose && this.handlers.onClose();
      this.reconnectTimer = setTimeout(() => this.connect(), 3000);
    };
    this.ws.onerror = () => {};
  }

  send(payload) {
    if (this.ws && this.ws.readyState === 1) {
      try { this.ws.send(JSON.stringify(payload)); } catch {}
    }
  }

  close() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.pingTimer) clearInterval(this.pingTimer);
    if (this.ws) {
      this.ws.onclose = null;
      try { this.ws.close(); } catch {}
    }
  }
}
