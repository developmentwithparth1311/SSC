/**
 * Snapshot of Signal readiness for Settings / debug logs.
 */
import { isElectronApp, isInstalledClient } from '../lib/platform';
import { fetchMyPreKeyStatus } from '../lib/signal/prekeys';
import {
  generatePreKeyBundle,
  hasSignalSession,
  isNativeLibsignalAvailable,
} from '../lib/signal/nativeLibsignal';

export async function collectEncryptionDiagnostics({ user, peer } = {}) {
  const out = {
    installed_client: isInstalledClient(),
    libsignal_available: isNativeLibsignalAvailable(),
    self_prekeys_ready: !!user?.signal_prekeys_ready,
    peer_prekeys_ready: peer ? peer.signal_prekeys_ready !== false : null,
    server_identity_ready: false,
    local_identity_ready: false,
    identity_matches_server: null,
    session_with_peer: null,
    peer_user_id: peer?.user_id || null,
  };

  if (isElectronApp() && typeof window !== 'undefined' && window.sscDesktop?.libsignalInitStatus) {
    try {
      const status = await window.sscDesktop.libsignalInitStatus();
      out.desktop_libsignal_init_ok = !!status?.ok;
      if (status?.error) out.desktop_libsignal_init_error = status.error;
    } catch (err) {
      out.desktop_libsignal_init_error = err?.message || String(err);
    }
  }

  if (!out.libsignal_available) return out;

  try {
    const status = await fetchMyPreKeyStatus();
    out.server_identity_ready = !!status?.ready;
    const bundle = await generatePreKeyBundle();
    out.local_identity_ready = !!bundle?.identity_key_public;
    if (status?.ready && bundle?.identity_key_public) {
      out.identity_matches_server = status.identity_key_public === bundle.identity_key_public;
    }
  } catch (err) {
    out.bootstrap_error = err?.message || String(err);
  }

  if (peer?.user_id && user?.user_id) {
    try {
      const session = await hasSignalSession(peer.user_id);
      out.session_with_peer = !!session?.has_session;
    } catch (err) {
      out.session_error = err?.message || String(err);
    }
  }

  return out;
}