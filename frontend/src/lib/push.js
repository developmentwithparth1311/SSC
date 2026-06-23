/* Service worker registration + push subscription helpers */
import { api } from './api';
import { isNativeApp, supportsWebPush } from './platform';

const VAPID_PUBLIC = process.env.REACT_APP_VAPID_PUBLIC;

function urlBase64ToUint8Array(b64String) {
  const padding = '='.repeat((4 - (b64String.length % 4)) % 4);
  const base64 = (b64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const raw = atob(base64);
  const arr = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) arr[i] = raw.charCodeAt(i);
  return arr;
}

export async function registerServiceWorker() {
  if (!supportsWebPush()) return null;
  try {
    const reg = await navigator.serviceWorker.register('/sw.js');
    return reg;
  } catch (e) {
    console.warn('sw register failed', e);
    return null;
  }
}

export async function subscribePush() {
  if (!supportsWebPush() || !VAPID_PUBLIC) {
    if (isNativeApp()) {
      console.info('[SSC] Web Push skipped in native shell (use PWA in browser or add FCM later)');
    }
    return null;
  }
  try {
    const perm = await Notification.requestPermission();
    if (perm !== 'granted') return null;
    const reg = await navigator.serviceWorker.ready;
    let sub = await reg.pushManager.getSubscription();
    if (!sub) {
      sub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC),
      });
    }
    const json = sub.toJSON();
    await api.post('/push/subscribe', { endpoint: json.endpoint, keys: json.keys });
    return sub;
  } catch (e) {
    console.warn('push subscribe failed', e);
    return null;
  }
}

export async function unsubscribePush() {
  if (!supportsWebPush()) return;
  try {
    const reg = await navigator.serviceWorker.ready;
    const sub = await reg.pushManager.getSubscription();
    if (sub) {
      const json = sub.toJSON();
      await api.post('/push/unsubscribe', { endpoint: json.endpoint, keys: json.keys || {} });
      await sub.unsubscribe();
    }
  } catch {}
}