import { api } from './api';

export const PENDING_INVITE_KEY = 'ssc_pending_invite';

export function savePendingInvite(token) {
  if (token) sessionStorage.setItem(PENDING_INVITE_KEY, token);
}

export function getPendingInvite() {
  return sessionStorage.getItem(PENDING_INVITE_KEY) || '';
}

export function clearPendingInvite() {
  sessionStorage.removeItem(PENDING_INVITE_KEY);
}

/** Consume a stored invite token. Returns true if used successfully. */
export async function consumePendingInvite() {
  const token = getPendingInvite();
  if (!token) return false;
  try {
    await api.post(`/invites/use/${token.trim()}`);
    clearPendingInvite();
    return true;
  } catch {
    return false;
  }
}