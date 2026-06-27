/**
 * Installed-client messaging gate — returns explicit readiness + failure reasons.
 */
import { isInstalledClient } from '../lib/platform';
import { bootstrapSignalIdentity } from '../lib/signalIdentityBootstrap';
import { hasSignalSession, isNativeLibsignalAvailable } from '../lib/signal/nativeLibsignal';
import { ensureSignalSession } from '../lib/signal/x3dh';
import { shouldSendWithSignal } from '../lib/signal/migration';
import { MessagingGateReason, messagingGateI18nKey } from './messagingGateReasons';

export { MessagingGateReason, messagingGateI18nKey };

const REASON_LOG = '[SSC messaging-gate]';

function httpDetail(err) {
  return err?.response?.data?.detail || err?.message || String(err);
}

function mapSessionError(err) {
  const detail = httpDetail(err);
  const status = err?.response?.status;
  if (status === 403 || detail.includes('contacts')) {
    return { reason: MessagingGateReason.SESSION_ESTABLISH_FAILED, detail: 'not_contacts' };
  }
  if (status === 404 || detail.includes('prekeys')) {
    return { reason: MessagingGateReason.PEER_PREKEYS_NOT_READY, detail };
  }
  if (status === 429) {
    return { reason: MessagingGateReason.SESSION_ESTABLISH_FAILED, detail: 'rate_limited' };
  }
  return { reason: MessagingGateReason.SESSION_ESTABLISH_FAILED, detail };
}

/**
 * @returns {Promise<{ ok: boolean, useSignal: boolean, reason: string, detail?: string }>}
 */
export async function evaluateMessagingGate({
  isGroup,
  peer,
  user,
  members,
  refreshUser,
}) {
  if (!usesSignalOnlyMessaging() || !user?.user_id) {
    const useSignal = await shouldSendWithSignal({ isGroup, peer, user, members });
    return { ok: true, useSignal, reason: MessagingGateReason.OK };
  }

  if (!isNativeLibsignalAvailable()) {
    console.warn(REASON_LOG, MessagingGateReason.LIBSIGNAL_UNAVAILABLE);
    return { ok: false, useSignal: false, reason: MessagingGateReason.LIBSIGNAL_UNAVAILABLE };
  }

  const boot = await bootstrapSignalIdentity(refreshUser);
  if (!boot?.ok) {
    console.warn(REASON_LOG, MessagingGateReason.BOOTSTRAP_FAILED, boot?.reason);
    return {
      ok: false,
      useSignal: false,
      reason: MessagingGateReason.BOOTSTRAP_FAILED,
      detail: boot?.reason,
    };
  }

  let freshUser = user;
  if (refreshUser) {
    freshUser = await refreshUser() || user;
  }
  if (!freshUser?.signal_prekeys_ready) {
    console.warn(REASON_LOG, MessagingGateReason.SELF_PREKEYS_NOT_READY);
    return { ok: false, useSignal: false, reason: MessagingGateReason.SELF_PREKEYS_NOT_READY };
  }

  if (!isGroup) {
    if (!peer?.user_id) {
      return { ok: false, useSignal: false, reason: MessagingGateReason.PEER_MISSING };
    }
    if (peer.signal_prekeys_ready === false) {
      console.warn(REASON_LOG, MessagingGateReason.PEER_PREKEYS_NOT_READY, peer.user_id);
      return { ok: false, useSignal: false, reason: MessagingGateReason.PEER_PREKEYS_NOT_READY };
    }
    try {
      await ensureSignalSession(peer.user_id, freshUser.user_id);
      const status = await hasSignalSession(peer.user_id);
      if (!status?.has_session) {
        console.warn(REASON_LOG, MessagingGateReason.NO_SIGNAL_SESSION, peer.user_id);
        return { ok: false, useSignal: false, reason: MessagingGateReason.NO_SIGNAL_SESSION };
      }
    } catch (err) {
      const mapped = mapSessionError(err);
      console.warn(REASON_LOG, mapped.reason, mapped.detail);
      return { ok: false, useSignal: false, ...mapped };
    }
  }

  const useSignal = await shouldSendWithSignal({ isGroup, peer, user: freshUser, members });
  if (!useSignal) {
    console.warn(REASON_LOG, isGroup ? MessagingGateReason.GROUP_NOT_READY : MessagingGateReason.SIGNAL_PATH_UNAVAILABLE);
    return {
      ok: false,
      useSignal: false,
      reason: isGroup ? MessagingGateReason.GROUP_NOT_READY : MessagingGateReason.SIGNAL_PATH_UNAVAILABLE,
    };
  }

  return { ok: true, useSignal: true, reason: MessagingGateReason.OK };
}

function usesSignalOnlyMessaging() {
  return isInstalledClient();
}

export async function prepareMessagingGate(opts) {
  return evaluateMessagingGate(opts);
}