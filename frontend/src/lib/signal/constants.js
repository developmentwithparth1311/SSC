/** Pinned official libsignal — must match backend/core/signal_policy.py */
export const LIBSIGNAL_PINNED_VERSION = '0.96.2';
export const LIBSIGNAL_NPM_PACKAGE = '@signalapp/libsignal-client';
export const LIBSIGNAL_ANDROID_ARTIFACT = 'org.signal:libsignal-android';

export const ProtocolVersion = {
  LEGACY_RSA: 'legacy_rsa',
  SIGNAL_V1: 'signal_v1',
};

/** libsignal CiphertextMessage types */
export const SignalMessageType = {
  WHISPER: 2,
  PREKEY: 3,
};