/**
 * X3DH session establishment — Engine 8.4.
 * Fetches peer prekey bundle (contacts only) and runs libsignal SessionBuilder on-device.
 */
import { api } from '../api';
import { establishSignalSession, hasSignalSession, isNativeLibsignalAvailable } from './nativeLibsignal';

const sessionPromises = new Map();

export async function fetchPeerPreKeyBundle(peerUserId) {
  const { data } = await api.get(`/keys/prekey-bundle/${peerUserId}`);
  return data;
}

export async function ensureSignalSession(peerUserId, ourUserId) {
  if (!peerUserId) return { skipped: true, reason: 'no_peer' };
  if (!ourUserId) return { skipped: true, reason: 'no_local_user' };
  if (!isNativeLibsignalAvailable()) {
    return { skipped: true, reason: 'web' };
  }

  const existing = sessionPromises.get(peerUserId);
  if (existing) return existing;

  const work = (async () => {
    const status = await hasSignalSession(peerUserId);
    if (status?.has_session) {
      return { established: false, already: true, has_session: true };
    }
    const bundle = await fetchPeerPreKeyBundle(peerUserId);
    const result = await establishSignalSession(peerUserId, bundle, ourUserId);
    // Verify the session was actually persisted to the native store.
    // If not, log a warning — the retry path in encryptSignalText will recover.
    const verify = await hasSignalSession(peerUserId);
    if (!verify?.has_session) {
      console.warn('[SSC] Signal session may not have persisted for', peerUserId, '— will retry at first encrypt');
    }
    return { ...result, has_session: verify?.has_session ?? result?.has_session ?? true };
  })();

  sessionPromises.set(peerUserId, work);
  try {
    return await work;
  } finally {
    sessionPromises.delete(peerUserId);
  }
}

/**
 * Force a fresh session establishment without checking hasSignalSession first.
 * Used to recover when the native store reports a session exists but
 * encryptSignalMessage fails with "session not found" (stale/incomplete write).
 */
export async function forceRefreshSignalSession(peerUserId, ourUserId) {
  if (!peerUserId || !ourUserId) return;
  if (!isNativeLibsignalAvailable()) return;
  const bundle = await fetchPeerPreKeyBundle(peerUserId);
  await establishSignalSession(peerUserId, bundle, ourUserId);
}