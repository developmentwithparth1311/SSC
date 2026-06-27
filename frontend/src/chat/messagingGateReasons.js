/** Messaging gate reason codes + i18n mapping (no heavy imports — safe for unit tests). */

export const MessagingGateReason = {
  OK: 'ok',
  NOT_INSTALLED: 'not_installed',
  LIBSIGNAL_UNAVAILABLE: 'libsignal_unavailable',
  BOOTSTRAP_FAILED: 'bootstrap_failed',
  SELF_PREKEYS_NOT_READY: 'self_prekeys_not_ready',
  PEER_PREKEYS_NOT_READY: 'peer_prekeys_not_ready',
  PEER_MISSING: 'peer_missing',
  SESSION_ESTABLISH_FAILED: 'session_establish_failed',
  NO_SIGNAL_SESSION: 'no_signal_session',
  GROUP_NOT_READY: 'group_not_ready',
  SIGNAL_PATH_UNAVAILABLE: 'signal_path_unavailable',
};

export function messagingGateI18nKey(reason) {
  switch (reason) {
    case MessagingGateReason.OK:
      return null;
    case MessagingGateReason.LIBSIGNAL_UNAVAILABLE:
      return 'encryptionErrLibsignal';
    case MessagingGateReason.BOOTSTRAP_FAILED:
      return 'encryptionErrBootstrap';
    case MessagingGateReason.SELF_PREKEYS_NOT_READY:
      return 'encryptionErrSelfPrekeys';
    case MessagingGateReason.PEER_PREKEYS_NOT_READY:
      return 'encryptionErrPeerPrekeys';
    case MessagingGateReason.SESSION_ESTABLISH_FAILED:
      return 'encryptionErrSession';
    case MessagingGateReason.NO_SIGNAL_SESSION:
      return 'encryptionErrNoSession';
    case MessagingGateReason.GROUP_NOT_READY:
      return 'encryptionErrGroup';
    case MessagingGateReason.PEER_MISSING:
      return 'encryptionErrPeerMissing';
    case MessagingGateReason.NOT_INSTALLED:
      return 'encryptionErrNotInstalled';
    case MessagingGateReason.SIGNAL_PATH_UNAVAILABLE:
      return 'encryptionErrSignalPath';
    default:
      return 'encryptionNotReady';
  }
}