jest.mock('../installedMessaging', () => ({
  usesSignalOnlyMessaging: jest.fn(),
}));

jest.mock('../nativeLibsignal', () => ({
  isNativeLibsignalAvailable: jest.fn(),
}));

jest.mock('../x3dh', () => ({
  ensureSignalSession: jest.fn(),
}));

jest.mock('../messages', () => ({
  canUseSignalMessaging: jest.fn(),
  encryptSignalText: jest.fn(),
  decryptSignalText: jest.fn(),
}));

jest.mock('../groupMessages', () => ({
  canUseSignalGroupMessaging: jest.fn(),
  ensureGroupSenderKeysDistributed: jest.fn(),
  encryptGroupText: jest.fn(),
  decryptGroupText: jest.fn(),
}));

import { usesSignalOnlyMessaging } from '../installedMessaging';
import { isNativeLibsignalAvailable } from '../nativeLibsignal';
import { ensureSignalSession } from '../x3dh';
import { canUseSignalMessaging, encryptSignalText } from '../messages';
import {
  SignalingFailureReason,
  SignalingNotReadyError,
  SignalingProtocol,
  packOutgoingSignaling,
  signalingErrorI18nKey,
} from '../webrtcSignaling';

const user = { user_id: 'me', signal_prekeys_ready: true };
const peer = { user_id: 'peer', signal_prekeys_ready: true };
const offer = { type: 'call-offer', to: 'peer', mode: 'audio', sdp: { type: 'offer', sdp: 'v=0' } };

describe('webrtcSignaling', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    isNativeLibsignalAvailable.mockReturnValue(true);
    ensureSignalSession.mockResolvedValue(undefined);
    canUseSignalMessaging.mockResolvedValue(true);
    encryptSignalText.mockResolvedValue({
      ciphertext: 'ct',
      signal_message_type: 1,
    });
  });

  it('maps signaling errors to i18n keys', () => {
    expect(signalingErrorI18nKey(SignalingFailureReason.ENCRYPT_FAILED)).toBe('callSignalingEncryptFailed');
    expect(signalingErrorI18nKey(SignalingFailureReason.PEER_PREKEYS_NOT_READY)).toBe('encryptionErrPeerPrekeys');
  });

  it('throws on installed client when session establish fails', async () => {
    usesSignalOnlyMessaging.mockReturnValue(true);
    ensureSignalSession.mockRejectedValue(new Error('session boom'));

    await expect(
      packOutgoingSignaling(offer, {
        peerUserId: peer.user_id,
        ourUserId: user.user_id,
        peer,
        user,
      }),
    ).rejects.toBeInstanceOf(SignalingNotReadyError);
  });

  it('throws on installed client when encrypt fails — no cleartext fallback', async () => {
    usesSignalOnlyMessaging.mockReturnValue(true);
    encryptSignalText.mockRejectedValue(new Error('encrypt boom'));

    await expect(
      packOutgoingSignaling(offer, {
        peerUserId: peer.user_id,
        ourUserId: user.user_id,
        peer,
        user,
      }),
    ).rejects.toMatchObject({ reason: SignalingFailureReason.ENCRYPT_FAILED });
  });

  it('falls back to legacy cleartext on web when encrypt is not required', async () => {
    usesSignalOnlyMessaging.mockReturnValue(false);
    isNativeLibsignalAvailable.mockReturnValue(false);

    const packed = await packOutgoingSignaling(offer, {
      peerUserId: peer.user_id,
      ourUserId: user.user_id,
      peer,
      user,
    });

    expect(packed.signaling_protocol).toBe(SignalingProtocol.LEGACY_CLEARTEXT);
    expect(packed.sdp).toEqual(offer.sdp);
    expect(encryptSignalText).not.toHaveBeenCalled();
  });

  it('encrypts signaling on installed client when ready', async () => {
    usesSignalOnlyMessaging.mockReturnValue(true);

    const packed = await packOutgoingSignaling(offer, {
      peerUserId: peer.user_id,
      ourUserId: user.user_id,
      peer,
      user,
    });

    expect(packed.signaling_protocol).toBe(SignalingProtocol.SIGNAL_V1);
    expect(packed.signaling_ciphertext).toBe('ct');
    expect(packed.sdp).toBeUndefined();
  });
});