/**
 * Platform detection — web PWA vs Capacitor native shell.
 * Web behavior is unchanged when not running inside Capacitor.
 */
let _capacitor = null;

function getCapacitor() {
  if (_capacitor !== null) return _capacitor;
  try {
    // eslint-disable-next-line global-require
    const { Capacitor } = require('@capacitor/core');
    _capacitor = Capacitor;
  } catch {
    _capacitor = false;
  }
  return _capacitor;
}

export function isNativeApp() {
  const Cap = getCapacitor();
  return !!(Cap && Cap.isNativePlatform && Cap.isNativePlatform());
}

export function getPlatform() {
  const Cap = getCapacitor();
  if (Cap && Cap.getPlatform) return Cap.getPlatform();
  return 'web';
}

/** Backend base URL (no trailing slash). Set at build time via REACT_APP_BACKEND_URL. */
export function getBackendUrl() {
  const raw = process.env.REACT_APP_BACKEND_URL || '';
  const url = raw.trim().replace(/\/$/, '');
  if (!url) {
    if (isNativeApp()) {
      console.warn('[SSC] REACT_APP_BACKEND_URL missing — native app needs your production API URL at build time');
    }
    return 'http://localhost:8000';
  }
  return url;
}

export function supportsWebPush() {
  return !isNativeApp() && 'serviceWorker' in navigator && 'PushManager' in window;
}