/**
 * Microphone / camera permission gate for calls and voice notes.
 * Android: native runtime permissions before getUserMedia.
 * Desktop / dev shell: browser prompt via getUserMedia probe.
 */
import { toast } from 'sonner';
import { isNativeApp } from './platform';
import {
  openNativeAppSettings,
  requestNativeMediaPermissions,
} from './nativeMediaPermissions';

export const PERM_MIC = 'microphone';
export const PERM_CAMERA = 'camera';

function isGranted(state) {
  return state === 'granted';
}

function deniedList(perms) {
  const denied = [];
  if (perms.audio && !isGranted(perms.micState)) denied.push(PERM_MIC);
  if (perms.video && !isGranted(perms.camState)) denied.push(PERM_CAMERA);
  return denied;
}

async function probeBrowserMedia({ audio, video }) {
  if (!navigator.mediaDevices?.getUserMedia) {
    return { micState: 'denied', camState: video ? 'denied' : 'prompt' };
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: !!audio,
      video: video ? { width: 640, height: 480 } : false,
    });
    stream.getTracks().forEach((t) => t.stop());
    return {
      micState: audio ? 'granted' : 'prompt',
      camState: video ? 'granted' : 'prompt',
    };
  } catch {
    return {
      micState: audio ? 'denied' : 'prompt',
      camState: video ? 'denied' : 'prompt',
    };
  }
}

/**
 * Request mic (and optionally camera). Returns true when all requested perms are granted.
 */
export async function ensureMediaPermissions(
  { audio = true, video = false } = {},
  { t, showToast = true } = {},
) {
  let micState = 'prompt';
  let camState = 'prompt';

  if (isNativeApp()) {
    try {
      const state = await requestNativeMediaPermissions({ audio, video });
      micState = state?.microphone || 'denied';
      camState = state?.camera || 'denied';
    } catch {
      micState = audio ? 'denied' : 'prompt';
      camState = video ? 'denied' : 'prompt';
    }
  } else {
    const probed = await probeBrowserMedia({ audio, video });
    micState = probed.micState;
    camState = probed.camState;
  }

  const denied = deniedList({ audio, video, micState, camState });
  if (denied.length === 0) return true;

  if (showToast && t) {
    const message = denied.includes(PERM_CAMERA)
      ? t('cameraPermissionDenied')
      : t('micPermissionDenied');
    toast.error(message, {
      duration: 8000,
      action: isNativeApp()
        ? {
            label: t('openSettings'),
            onClick: () => openNativeAppSettings().catch(() => {}),
          }
        : undefined,
    });
  }
  return false;
}

export async function openAppMediaSettings() {
  if (isNativeApp()) {
    await openNativeAppSettings();
  }
}