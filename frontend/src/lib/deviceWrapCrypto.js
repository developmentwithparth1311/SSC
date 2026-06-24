/**
 * Device-bound AES-GCM wrap — shared by vault credentials and session persistence.
 * Plaintext secrets never stored in localStorage; only ciphertext blobs.
 */

export const DEVICE_WRAP_KEY = 'ssc_device_wrap_secret';

function toB64(bytes) {
  return btoa(String.fromCharCode(...new Uint8Array(bytes)));
}

function fromB64(b64s) {
  return Uint8Array.from(atob(b64s), (c) => c.charCodeAt(0));
}

export async function getDeviceWrapKey() {
  if (typeof crypto?.subtle === 'undefined' || typeof localStorage === 'undefined') return null;
  let stored = localStorage.getItem(DEVICE_WRAP_KEY);
  if (!stored) {
    const raw = crypto.getRandomValues(new Uint8Array(32));
    stored = toB64(raw);
    localStorage.setItem(DEVICE_WRAP_KEY, stored);
  }
  const bytes = fromB64(stored);
  return crypto.subtle.importKey('raw', bytes, { name: 'AES-GCM' }, false, ['encrypt', 'decrypt']);
}

/** @returns {Promise<string|null>} `ciphertext.iv` base64 pair */
export async function wrapDeviceSecret(plaintext) {
  if (!plaintext) return null;
  const key = await getDeviceWrapKey();
  if (!key) return null;
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ct = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv },
    key,
    new TextEncoder().encode(plaintext),
  );
  return `${toB64(ct)}.${toB64(iv)}`;
}

/** @returns {Promise<string|null>} */
export async function unwrapDeviceSecret(blob) {
  if (!blob) return null;
  const key = await getDeviceWrapKey();
  if (!key) return null;
  try {
    const [ctB64, ivB64] = blob.split('.');
    const pt = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv: fromB64(ivB64) },
      key,
      fromB64(ctB64),
    );
    return new TextDecoder().decode(pt);
  } catch {
    return null;
  }
}

export function clearDeviceWrapSecret() {
  if (typeof localStorage === 'undefined') return;
  localStorage.removeItem(DEVICE_WRAP_KEY);
}