jest.mock('../../lib/platform', () => ({
  isInstalledClient: jest.fn(),
}));

jest.mock('../../lib/signalIdentityBootstrap', () => ({
  bootstrapSignalIdentity: jest.fn(),
}));

jest.mock('../../lib/signal/nativeLibsignal', () => ({
  hasSignalSession: jest.fn(),
  isNativeLibsignalAvailable: jest.fn(),
}));

jest.mock('../../lib/signal/x3dh', () => ({
  ensureSignalSession: jest.fn(),
}));

jest.mock('../../lib/signal/migration', () => ({
  shouldSendWithSignal: jest.fn(),
}));

import { MessagingGateReason, messagingGateI18nKey } from '../messagingGateReasons';
import { evaluateMessagingGate } from '../messagingGate';
import { isInstalledClient } from '../../lib/platform';
import { bootstrapSignalIdentity } from '../../lib/signalIdentityBootstrap';
import { hasSignalSession, isNativeLibsignalAvailable } from '../../lib/signal/nativeLibsignal';
import { ensureSignalSession } from '../../lib/signal/x3dh';
import { shouldSendWithSignal } from '../../lib/signal/migration';

describe('messagingGateReasons', () => {
  it('maps reasons to i18n keys', () => {
    expect(messagingGateI18nKey(MessagingGateReason.SELF_PREKEYS_NOT_READY)).toBe('encryptionErrSelfPrekeys');
    expect(messagingGateI18nKey(MessagingGateReason.PEER_PREKEYS_NOT_READY)).toBe('encryptionErrPeerPrekeys');
    expect(messagingGateI18nKey(MessagingGateReason.PEER_MISSING)).toBe('encryptionErrPeerMissing');
    expect(messagingGateI18nKey(MessagingGateReason.NOT_INSTALLED)).toBe('encryptionErrNotInstalled');
    expect(messagingGateI18nKey(MessagingGateReason.SIGNAL_PATH_UNAVAILABLE)).toBe('encryptionErrSignalPath');
    expect(messagingGateI18nKey(MessagingGateReason.OK)).toBeNull();
  });
});

describe('evaluateMessagingGate', () => {
  const peer = { user_id: 'peer-1', signal_prekeys_ready: true };
  const user = { user_id: 'me-1', signal_prekeys_ready: true };

  beforeEach(() => {
    jest.clearAllMocks();
    isInstalledClient.mockReturnValue(true);
    isNativeLibsignalAvailable.mockReturnValue(true);
    bootstrapSignalIdentity.mockResolvedValue({ ok: true });
    ensureSignalSession.mockResolvedValue(undefined);
    hasSignalSession.mockResolvedValue({ has_session: true });
    shouldSendWithSignal.mockResolvedValue(true);
  });

  it('returns libsignal_unavailable when native bridge is missing', async () => {
    isNativeLibsignalAvailable.mockReturnValue(false);
    const gate = await evaluateMessagingGate({ isGroup: false, peer, user });
    expect(gate).toMatchObject({ ok: false, reason: MessagingGateReason.LIBSIGNAL_UNAVAILABLE });
  });

  it('returns self_prekeys_not_ready when user prekeys are not ready', async () => {
    const gate = await evaluateMessagingGate({
      isGroup: false,
      peer,
      user: { ...user, signal_prekeys_ready: false },
    });
    expect(gate).toMatchObject({ ok: false, reason: MessagingGateReason.SELF_PREKEYS_NOT_READY });
  });

  it('returns peer_prekeys_not_ready when peer prekeys are not ready', async () => {
    const gate = await evaluateMessagingGate({
      isGroup: false,
      peer: { ...peer, signal_prekeys_ready: false },
      user,
    });
    expect(gate).toMatchObject({ ok: false, reason: MessagingGateReason.PEER_PREKEYS_NOT_READY });
  });

  it('returns ok when session is established', async () => {
    const gate = await evaluateMessagingGate({ isGroup: false, peer, user });
    expect(gate).toMatchObject({ ok: true, useSignal: true, reason: MessagingGateReason.OK });
  });

  it('returns peer_missing when peer is absent in 1:1 chat', async () => {
    const gate = await evaluateMessagingGate({ isGroup: false, peer: null, user });
    expect(gate).toMatchObject({ ok: false, reason: MessagingGateReason.PEER_MISSING });
  });
});