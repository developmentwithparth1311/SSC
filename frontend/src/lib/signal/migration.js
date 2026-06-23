/**
 * Signal migration — Engine 8.6 dual-read + honest encryption labels.
 */
import { decryptMessage } from '../crypto';
import { ProtocolVersion } from './constants';
import {
  canUseSignalMessaging,
  decryptSignalText,
  isSignalV1Message,
  signalRemoteUserId,
} from './messages';
import { isNativeLibsignalAvailable } from './nativeLibsignal';

export function getMessageProtocol(msg) {
  return msg?.protocol || ProtocolVersion.LEGACY_RSA;
}

export function isLegacyRsaMessage(msg) {
  return getMessageProtocol(msg) === ProtocolVersion.LEGACY_RSA;
}

/** Unified dual-read decrypt — legacy_rsa (vault) or signal_v1 (native store). */
export async function decryptMessageBody(msg, { myUserId, peerUserId, privateKey }) {
  if (!msg?.ciphertext) {
    throw new Error('NO_CIPHERTEXT');
  }
  if (isSignalV1Message(msg)) {
    const remoteId = signalRemoteUserId(msg, { myUserId, peerUserId });
    if (!remoteId || !myUserId) throw new Error('NO_KEY');
    return decryptSignalText(remoteId, myUserId, msg);
  }
  if (!privateKey) throw new Error('VAULT_LOCKED');
  const myKey = msg.encrypted_keys?.[myUserId];
  if (!myKey || !msg.iv) throw new Error('NO_KEY');
  return decryptMessage(privateKey, msg.ciphertext, msg.iv, myKey);
}

export async function resolveOutgoingEncryptionHint({ isGroup, peer, user }) {
  if (isGroup) {
    return { mode: ProtocolVersion.LEGACY_RSA, reason: 'group_chat' };
  }
  if (!peer?.user_id || !user?.user_id) {
    return { mode: ProtocolVersion.LEGACY_RSA, reason: 'no_peer' };
  }
  if (!isNativeLibsignalAvailable()) {
    return { mode: ProtocolVersion.LEGACY_RSA, reason: 'web_client' };
  }
  if (!user.signal_prekeys_ready) {
    return { mode: ProtocolVersion.LEGACY_RSA, reason: 'self_no_prekeys' };
  }
  if (!peer.signal_prekeys_ready) {
    return { mode: ProtocolVersion.LEGACY_RSA, reason: 'peer_no_prekeys' };
  }
  const ready = await canUseSignalMessaging(peer.user_id, user.user_id, true);
  if (ready) {
    return { mode: ProtocolVersion.SIGNAL_V1, reason: null };
  }
  return { mode: ProtocolVersion.LEGACY_RSA, reason: 'no_signal_session' };
}

export async function shouldSendWithSignal({ isGroup, attachmentId, messageType, peer, user }) {
  if (isGroup || attachmentId || messageType !== 'text') return false;
  if (!peer?.user_id || !user?.user_id) return false;
  if (!user.signal_prekeys_ready || !peer.signal_prekeys_ready) return false;
  return canUseSignalMessaging(peer.user_id, user.user_id, true);
}

/** Map outgoing hint reason → i18n key for composer banner. */
export function encryptionHintI18nKey(hint) {
  if (!hint) return null;
  if (hint.mode === ProtocolVersion.SIGNAL_V1) return 'encryptionHintSignal';
  switch (hint.reason) {
    case 'web_client': return 'encryptionHintLegacyWeb';
    case 'self_no_prekeys': return 'encryptionHintLegacySelf';
    case 'peer_no_prekeys': return 'encryptionHintLegacyPeer';
    case 'no_signal_session': return 'encryptionHintLegacySession';
    case 'group_chat': return 'encryptionHintLegacyGroup';
    default: return 'encryptionHintLegacyFallback';
  }
}