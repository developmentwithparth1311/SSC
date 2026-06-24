/**
 * WebRTC local/remote media helpers — shared by 1:1 and group calls.
 */

export const DEFAULT_CAMERA_FACING = 'user';

export const AUDIO_CALL_CONSTRAINTS = { audio: true, video: false };

export function videoConstraintsForFacing(facingMode = DEFAULT_CAMERA_FACING) {
  return { width: 640, height: 480, facingMode };
}

export const VIDEO_CALL_CONSTRAINTS = {
  audio: true,
  video: videoConstraintsForFacing(DEFAULT_CAMERA_FACING),
};

export function oppositeCameraFacing(facing = DEFAULT_CAMERA_FACING) {
  return facing === 'environment' ? 'user' : 'environment';
}

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

/** Combine live receiver tracks into one remote MediaStream. */
export function getRemoteStreamFromPeerConnection(pc) {
  if (!pc) return null;
  const tracks = pc.getReceivers()
    .map((r) => r.track)
    .filter((t) => t && t.readyState === 'live');
  if (!tracks.length) return null;
  return new MediaStream(tracks);
}

/** Add or re-enable a camera track on an existing local stream. */
export async function addVideoTrackToStream(stream, facingMode = DEFAULT_CAMERA_FACING) {
  if (!stream) throw new Error('no_stream');
  const existing = stream.getVideoTracks().find((t) => t.readyState === 'live');
  if (existing) {
    existing.enabled = true;
    return existing;
  }
  const cam = await navigator.mediaDevices.getUserMedia({
    video: videoConstraintsForFacing(facingMode),
    audio: false,
  });
  const videoTrack = cam.getVideoTracks()[0];
  if (videoTrack) stream.addTrack(videoTrack);
  return videoTrack;
}

async function acquireFacingVideoTrack(facingMode = DEFAULT_CAMERA_FACING) {
  const cam = await navigator.mediaDevices.getUserMedia({
    video: videoConstraintsForFacing(facingMode),
    audio: false,
  });
  const videoTrack = cam.getVideoTracks()[0];
  if (!videoTrack) throw new Error('no_video_track');
  return videoTrack;
}

/** Swap front/back camera without renegotiating the call. */
export async function replaceVideoTrackFacing(pc, stream, facingMode = DEFAULT_CAMERA_FACING) {
  if (!stream) throw new Error('no_stream');
  const oldVideo = stream.getVideoTracks()[0];
  if (oldVideo) {
    oldVideo.stop();
    stream.removeTrack(oldVideo);
  }
  const videoTrack = await acquireFacingVideoTrack(facingMode);
  stream.addTrack(videoTrack);
  const sender = pc?.getSenders?.().find((s) => s.track?.kind === 'video');
  if (sender) {
    await sender.replaceTrack(videoTrack);
  }
  return videoTrack;
}

/** Swap camera for full-mesh group calls (one stream, many peer connections). */
export async function replaceVideoTrackFacingOnMesh(peerConnections, stream, facingMode = DEFAULT_CAMERA_FACING) {
  if (!stream) throw new Error('no_stream');
  const oldVideo = stream.getVideoTracks()[0];
  if (oldVideo) {
    oldVideo.stop();
    stream.removeTrack(oldVideo);
  }
  const videoTrack = await acquireFacingVideoTrack(facingMode);
  stream.addTrack(videoTrack);
  const pcs = Array.isArray(peerConnections) ? peerConnections : [];
  await Promise.all(pcs.map(async (pc) => {
    const sender = pc?.getSenders?.().find((s) => s.track?.kind === 'video');
    if (sender) await sender.replaceTrack(videoTrack);
  }));
  return videoTrack;
}

/** Attach (or replace) the local video track on a peer connection. */
export async function applyVideoToPeerConnection(pc, stream, facingMode = DEFAULT_CAMERA_FACING) {
  const videoTrack = await addVideoTrackToStream(stream, facingMode);
  const sender = pc.getSenders().find((s) => s.track?.kind === 'video');
  if (sender) {
    await sender.replaceTrack(videoTrack);
  } else {
    pc.addTrack(videoTrack, stream);
  }
}

/** Detach and stop the local video track; audio is unchanged. */
export async function removeVideoFromPeerConnection(pc, stream) {
  const videoTrack = stream?.getVideoTracks?.()[0];
  const sender = pc.getSenders().find((s) => s.track?.kind === 'video');
  if (sender) await sender.replaceTrack(null);
  if (videoTrack) {
    videoTrack.enabled = false;
    videoTrack.stop();
    stream.removeTrack(videoTrack);
  }
}