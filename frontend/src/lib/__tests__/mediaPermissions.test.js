import { toast } from 'sonner';
import { ensureMediaPermissions, PERM_MIC, PERM_CAMERA } from '../mediaPermissions';

jest.mock('sonner', () => ({
  toast: { error: jest.fn() },
}));

jest.mock('../platform', () => ({
  isNativeApp: jest.fn(() => false),
}));

jest.mock('../nativeMediaPermissions', () => ({
  requestNativeMediaPermissions: jest.fn(),
  openNativeAppSettings: jest.fn(),
}));

const { isNativeApp } = require('../platform');
const { requestNativeMediaPermissions } = require('../nativeMediaPermissions');

describe('mediaPermissions', () => {
  const t = (key) => key;

  beforeEach(() => {
    jest.clearAllMocks();
    isNativeApp.mockReturnValue(false);
    navigator.mediaDevices = {
      getUserMedia: jest.fn().mockResolvedValue({
        getTracks: () => [{ stop: jest.fn() }],
      }),
    };
  });

  it('exports permission constants', () => {
    expect(PERM_MIC).toBe('microphone');
    expect(PERM_CAMERA).toBe('camera');
  });

  it('returns true when browser grants audio', async () => {
    const ok = await ensureMediaPermissions({ audio: true, video: false }, { t });
    expect(ok).toBe(true);
    expect(toast.error).not.toHaveBeenCalled();
  });

  it('returns false and toasts when browser denies audio', async () => {
    navigator.mediaDevices.getUserMedia.mockRejectedValue(new Error('denied'));
    const ok = await ensureMediaPermissions({ audio: true, video: false }, { t });
    expect(ok).toBe(false);
    expect(toast.error).toHaveBeenCalledWith('micPermissionDenied', expect.any(Object));
  });

  it('toasts camera message when video denied', async () => {
    navigator.mediaDevices.getUserMedia.mockRejectedValue(new Error('denied'));
    const ok = await ensureMediaPermissions({ audio: true, video: true }, { t });
    expect(ok).toBe(false);
    expect(toast.error).toHaveBeenCalledWith('cameraPermissionDenied', expect.any(Object));
  });

  it('uses native plugin on Android', async () => {
    isNativeApp.mockReturnValue(true);
    requestNativeMediaPermissions.mockResolvedValue({
      microphone: 'granted',
      camera: 'granted',
    });
    const ok = await ensureMediaPermissions({ audio: true, video: true }, { t });
    expect(ok).toBe(true);
    expect(requestNativeMediaPermissions).toHaveBeenCalledWith({ audio: true, video: true });
  });

  it('offers settings action on native when denied', async () => {
    isNativeApp.mockReturnValue(true);
    requestNativeMediaPermissions.mockResolvedValue({
      microphone: 'denied',
      camera: 'prompt',
    });
    const ok = await ensureMediaPermissions({ audio: true, video: false }, { t });
    expect(ok).toBe(false);
    expect(toast.error).toHaveBeenCalledWith(
      'micPermissionDenied',
      expect.objectContaining({ action: expect.objectContaining({ label: 'openSettings' }) }),
    );
  });
});