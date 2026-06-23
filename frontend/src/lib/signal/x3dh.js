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
    return { ...result, has_session: result?.has_session ?? true };
  })();

  sessionPromises.set(peerUserId, work);
  try {
    return await work;
  } finally {
    sessionPromises.delete(peerUserId);
  }
}