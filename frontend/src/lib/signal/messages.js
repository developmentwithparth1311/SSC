/**
 * Double Ratchet messaging — Engine 8.5 (signal_v1).
 */
import { ProtocolVersion } from './constants';
import {
  decryptSignalMessage as nativeDecrypt,
  encryptSignalMessage as nativeEncrypt,
  hasSignalSession,
  isNativeLibsignalAvailable,
} from './nativeLibsignal';
import { ensureSignalSession } from './x3dh';

export function isSignalV1Message(msg) {
  return (msg?.protocol || ProtocolVersion.LEGACY_RSA) === ProtocolVersion.SIGNAL_V1;
}

export async function canUseSignalMessaging(peerUserId, ourUserId, peerHasPrekeys) {
  if (!peerUserId || !ourUserId || !peerHasPrekeys) return false;
  if (!isNativeLibsignalAvailable()) return false;
  try {
    await ensureSignalSession(peerUserId, ourUserId);
    const status = await hasSignalSession(peerUserId);
    return !!status?.has_session;
  } catch {
    return false;
  }
}

export async function encryptSignalText(peerUserId, ourUserId, plaintext) {
  return nativeEncrypt(peerUserId, ourUserId, plaintext ?? '');
}

export async function decryptSignalText(peerUserId, ourUserId, msg) {
  if (!isSignalV1Message(msg)) {
    throw new Error('not a signal_v1 message');
  }
  const result = await nativeDecrypt(
    peerUserId,
    ourUserId,
    msg.ciphertext,
    msg.signal_message_type,
  );
  return result?.plaintext ?? '';
}

/** Remote user id for session lookup: sender when receiving, peer when viewing own sends. */
export function signalRemoteUserId(msg, { myUserId, peerUserId }) {
  if (!msg || !myUserId) return null;
  if (msg.sender_id === myUserId) return peerUserId;
  return msg.sender_id;
}