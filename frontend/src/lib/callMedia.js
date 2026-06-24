/**
 * WebRTC local/remote media helpers — shared by 1:1 and group calls.
 */

export const AUDIO_CALL_CONSTRAINTS = { audio: true, video: false };
export const VIDEO_CALL_CONSTRAINTS = {
  audio: true,
  video: { width: 640, height: 480, facingMode: 'user' },
};

export function mediaConstraintsForMode(mode) {
  return mode === 'video' ? VIDEO_CALL_CONSTRAINTS : AUDIO_CALL_CONSTRAINTS;
}

export async function acquireLocalMediaStream(mode) {
  const constraints = mediaConstraintsForMode(mode);
  return navigator.mediaDevices.getUserMedia(constraints);
}

/** Attach remote stream to video (picture) + audio (sound) elements. */
export function bindRemoteStream({ videoEl, audioEl, stream }) {
  if (!stream) return;
  if (videoEl) {
    videoEl.srcObject = stream;
    videoEl.muted = true;
    tryPlay(videoEl);
  }
  if (audioEl) {
    audioEl.srcObject = stream;
    tryPlay(audioEl);
  }
}

function tryPlay(el) {
  try {
    const p = el?.play?.();
    if (p?.catch) p.catch(() => {});
  } catch {}
}

export function bindLocalPreview(videoEl, stream) {
  if (!videoEl || !stream) return;
  videoEl.srcObject = stream;
  videoEl.muted = true;
  tryPlay(videoEl);
}