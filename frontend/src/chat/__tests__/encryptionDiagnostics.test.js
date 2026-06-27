jest.mock('../../lib/platform', () => ({
  isInstalledClient: jest.fn(() => true),
  isElectronApp: jest.fn(() => false),
}));

jest.mock('../../lib/signal/prekeys', () => ({
  fetchMyPreKeyStatus: jest.fn(),
}));

jest.mock('../../lib/signal/nativeLibsignal', () => ({
  isNativeLibsignalAvailable: jest.fn(),
  generatePreKeyBundle: jest.fn(),
  hasSignalSession: jest.fn(),
}));

import { fetchMyPreKeyStatus } from '../../lib/signal/prekeys';
import {
  generatePreKeyBundle,
  hasSignalSession,
  isNativeLibsignalAvailable,
} from '../../lib/signal/nativeLibsignal';
import { collectEncryptionDiagnostics } from '../encryptionDiagnostics';

describe('collectEncryptionDiagnostics', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('returns early when libsignal is unavailable', async () => {
    isNativeLibsignalAvailable.mockReturnValue(false);
    const diag = await collectEncryptionDiagnostics({ user: { user_id: 'me', signal_prekeys_ready: true } });
    expect(diag.libsignal_available).toBe(false);
    expect(fetchMyPreKeyStatus).not.toHaveBeenCalled();
  });

  it('reports identity match and peer session', async () => {
    isNativeLibsignalAvailable.mockReturnValue(true);
    fetchMyPreKeyStatus.mockResolvedValue({ ready: true, identity_key_public: 'ID-A' });
    generatePreKeyBundle.mockResolvedValue({ identity_key_public: 'ID-A' });
    hasSignalSession.mockResolvedValue({ has_session: true });

    const diag = await collectEncryptionDiagnostics({
      user: { user_id: 'me', signal_prekeys_ready: true },
      peer: { user_id: 'peer', signal_prekeys_ready: true },
    });

    expect(diag.identity_matches_server).toBe(true);
    expect(diag.session_with_peer).toBe(true);
    expect(diag.peer_user_id).toBe('peer');
  });

  it('captures bootstrap errors', async () => {
    isNativeLibsignalAvailable.mockReturnValue(true);
    fetchMyPreKeyStatus.mockRejectedValue(new Error('network down'));

    const diag = await collectEncryptionDiagnostics({
      user: { user_id: 'me', signal_prekeys_ready: false },
    });

    expect(diag.bootstrap_error).toBe('network down');
  });
});