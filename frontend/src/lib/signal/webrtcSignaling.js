/**
 * WebRTC signaling encryption — Engine 8.7 (G6).
 * 1:1 SDP/ICE wrapped in signal_v1 ratchet ciphertext; group calls stay legacy cleartext.
 */
import { ProtocolVersion } from './constants';
import { encryptSignalText, decryptSignalText, canUseSignalMessaging } from './messages';
import { isNativeLibsignalAvailable } from './nativeLibsignal';

export const SignalingProtocol = {
  LEGACY_CLEARTEXT: 'legacy_cleartext',
  SIGNAL_V1: 'signal_v1',
};

const SENSITIVE_TYPES = new Set(['call-offer', 'call-answer', 'ice-candidate']);

export function getSignalingProtocol(msg) {
  return msg?.signaling_protocol || SignalingProtocol.LEGACY_CLEARTEXT;
}

export function isEncryptedSignaling(msg) {
  return getSignalingProtocol(msg) === SignalingProtocol.SIGNAL_V1;
}

/** Remote peer for ratchet lookup on incoming WS payloads. */
export function signalingRemoteUserId(msg, { myUserId, peerUserId }) {
  if (msg?.from && msg.from !== myUserId) return msg.from;
  return peerUserId;
}

export async function shouldEncryptSignaling({ isGroup, peer, user }) {
  if (isGroup) return false;
  if (!peer?.user_id || !user?.user_id) return false;
  if (!isNativeLibsignalAvailable()) return false;
  if (!user.signal_prekeys_ready || !peer.signal_prekeys_ready) return false;
  return canUseSignalMessaging(peer.user_id, user.user_id, true);
}

function buildInnerPayload(msg) {
  const inner = {};
  if (msg.sdp != null) inner.sdp = msg.sdp;
  if (msg.candidate != null) inner.candidate = msg.candidate;
  return inner;
}

/** Pack outgoing WS signaling — encrypts sdp/candidate for 1:1 when session ready. */
export async function packOutgoingSignaling(msg, { peerUserId, ourUserId, peer, user, isGroup = false }) {
  if (!SENSITIVE_TYPES.has(msg?.type)) {
    return msg;
  }
  if (isGroup) {
    return { ...msg, signaling_protocol: SignalingProtocol.LEGACY_CLEARTEXT };
  }

  const useSignal = await shouldEncryptSignaling({ isGroup: false, peer, user });
  if (!useSignal) {
    return { ...msg, signaling_protocol: SignalingProtocol.LEGACY_CLEARTEXT };
  }

  const inner = buildInnerPayload(msg);
  const enc = await encryptSignalText(peerUserId, ourUserId, JSON.stringify(inner));
  const packed = {
    type: msg.type,
    to: msg.to,
    signaling_protocol: SignalingProtocol.SIGNAL_V1,
    signaling_ciphertext: enc.ciphertext,
    signal_message_type: enc.signal_message_type,
  };
  if (msg.mode != null) packed.mode = msg.mode;
  return packed;
}

/** Unpack incoming WS signaling — decrypts signal_v1 inner sdp/candidate. */
export async function unpackIncomingSignaling(msg, { myUserId, peerUserId }) {
  if (!msg || !SENSITIVE_TYPES.has(msg.type)) {
    return msg;
  }

  const proto = getSignalingProtocol(msg);
  if (proto !== SignalingProtocol.SIGNAL_V1) {
    return msg;
  }
  if (msg.sdp != null || msg.candidate != null) {
    return msg;
  }
  if (!msg.signaling_ciphertext) {
    throw new Error('NO_SIGNALING_CIPHERTEXT');
  }

  const remoteId = signalingRemoteUserId(msg, { myUserId, peerUserId });
  if (!remoteId || !myUserId) throw new Error('NO_PEER');

  const plaintext = await decryptSignalText(remoteId, myUserId, {
    protocol: ProtocolVersion.SIGNAL_V1,
    ciphertext: msg.signaling_ciphertext,
    signal_message_type: msg.signal_message_type,
  });
  const inner = JSON.parse(plaintext || '{}');
  return {
    ...msg,
    ...(inner.sdp != null ? { sdp: inner.sdp } : {}),
    ...(inner.candidate != null ? { candidate: inner.candidate } : {}),
  };
}

/** Send signaling through socket with optional ratchet wrapping. */
export async function sendSignaling(socket, msg, ctx) {
  if (!socket?.send) return;
  const packed = await packOutgoingSignaling(msg, ctx);
  socket.send(packed);
}