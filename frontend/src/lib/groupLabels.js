/**
 * Optional local-only group title (creator device). Not sent to server.
 * Persisted in localStorage so names survive app restarts (sessionStorage cleared on kill).
 */
const STORAGE_KEY = 'ssc_group_labels';

function readMap() {
  if (typeof localStorage === 'undefined') return {};
  try {
    let raw = localStorage.getItem(STORAGE_KEY);
    if (!raw && typeof sessionStorage !== 'undefined') {
      const legacy = sessionStorage.getItem(STORAGE_KEY);
      if (legacy) {
        localStorage.setItem(STORAGE_KEY, legacy);
        sessionStorage.removeItem(STORAGE_KEY);
        raw = legacy;
      }
    }
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function writeMap(map) {
  if (typeof localStorage === 'undefined') return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(map));
  } catch {}
}

export function getLocalGroupLabel(conversationId) {
  if (!conversationId) return '';
  return readMap()[conversationId] || '';
}

export function setLocalGroupLabel(conversationId, label) {
  if (!conversationId || !label?.trim()) return;
  const map = readMap();
  map[conversationId] = label.trim();
  writeMap(map);
}

export function clearLocalGroupLabels() {
  if (typeof localStorage === 'undefined') return;
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {}
}