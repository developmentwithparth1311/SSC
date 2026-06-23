import { Capacitor, registerPlugin } from '@capacitor/core';
import { LIBSIGNAL_PINNED_VERSION } from './constants';

const SscLibsignal = registerPlugin('SscLibsignal', {
  web: () => import('./nativeLibsignalWeb').then((m) => new m.SscLibsignalWeb()),
});

export function isNativeLibsignalAvailable() {
  return Capacitor.isNativePlatform();
}

export async function getPinnedLibsignalVersion() {
  if (!isNativeLibsignalAvailable()) {
    return { version: LIBSIGNAL_PINNED_VERSION, source: 'policy-only-web' };
  }
  return SscLibsignal.getPinnedVersion();
}

export async function generatePreKeyBundle() {
  if (!isNativeLibsignalAvailable()) {
    throw new Error('Signal prekeys require the SSC Android app (libsignal native)');
  }
  const bundle = await SscLibsignal.generatePreKeyBundle();
  if (bundle?.libsignal_version && bundle.libsignal_version !== LIBSIGNAL_PINNED_VERSION) {
    throw new Error(`Unexpected libsignal version: ${bundle.libsignal_version}`);
  }
  return bundle;
}

export async function hasSignalSession(peerUserId) {
  if (!isNativeLibsignalAvailable()) {
    return { has_session: false, skipped: true, reason: 'web' };
  }
  return SscLibsignal.hasSession({ peer_user_id: peerUserId });
}

export async function establishSignalSession(peerUserId, bundle, ourUserId) {
  if (!isNativeLibsignalAvailable()) {
    throw new Error('Signal sessions require the SSC Android app (libsignal native)');
  }
  return SscLibsignal.establishSession({
    peer_user_id: peerUserId,
    our_user_id: ourUserId,
    bundle,
  });
}

export async function encryptSignalMessage(peerUserId, ourUserId, plaintext) {
  if (!isNativeLibsignalAvailable()) {
    throw new Error('Signal encrypt requires the SSC Android app (libsignal native)');
  }
  return SscLibsignal.encryptSignalMessage({
    peer_user_id: peerUserId,
    our_user_id: ourUserId,
    plaintext,
  });
}

export async function decryptSignalMessage(peerUserId, ourUserId, ciphertext, signalMessageType) {
  if (!isNativeLibsignalAvailable()) {
    throw new Error('Signal decrypt requires the SSC Android app (libsignal native)');
  }
  return SscLibsignal.decryptSignalMessage({
    peer_user_id: peerUserId,
    our_user_id: ourUserId,
    ciphertext,
    signal_message_type: signalMessageType,
  });
}