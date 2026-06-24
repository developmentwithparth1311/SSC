import {
  mediaConstraintsForMode,
  bindRemoteStream,
  bindLocalPreview,
  getRemoteStreamFromPeerConnection,
  oppositeCameraFacing,
  videoConstraintsForFacing,
  AUDIO_CALL_CONSTRAINTS,
  VIDEO_CALL_CONSTRAINTS,
} from '../callMedia';

describe('callMedia', () => {
  it('returns audio constraints for audio mode', () => {
    expect(mediaConstraintsForMode('audio')).toEqual(AUDIO_CALL_CONSTRAINTS);
  });

  it('returns video constraints for video mode', () => {
    expect(mediaConstraintsForMode('video')).toEqual(VIDEO_CALL_CONSTRAINTS);
  });

  it('builds facing-specific video constraints', () => {
    expect(videoConstraintsForFacing('environment')).toEqual({
      width: 640,
      height: 480,
      facingMode: 'environment',
    });
  });

  it('toggles between front and back camera', () => {
    expect(oppositeCameraFacing('user')).toBe('environment');
    expect(oppositeCameraFacing('environment')).toBe('user');
  });

  it('bindRemoteStream attaches stream and plays', () => {
    const videoEl = { srcObject: null, muted: false, play: jest.fn() };
    const audioEl = { srcObject: null, play: jest.fn() };
    const stream = { id: 'remote' };
    bindRemoteStream({ videoEl, audioEl, stream });
    expect(videoEl.srcObject).toBe(stream);
    expect(videoEl.muted).toBe(true);
    expect(audioEl.srcObject).toBe(stream);
    expect(audioEl.play).toHaveBeenCalled();
  });

  it('bindLocalPreview mutes local preview', () => {
    const videoEl = { srcObject: null, muted: false, play: jest.fn() };
    const stream = { id: 'local' };
    bindLocalPreview(videoEl, stream);
    expect(videoEl.srcObject).toBe(stream);
    expect(videoEl.muted).toBe(true);
  });

  it('getRemoteStreamFromPeerConnection combines live receiver tracks', () => {
    const audio = { kind: 'audio', readyState: 'live' };
    const video = { kind: 'video', readyState: 'live' };
    const pc = {
      getReceivers: () => [{ track: audio }, { track: video }, { track: { readyState: 'ended' } }],
    };
    global.MediaStream = jest.fn((tracks) => ({ getTracks: () => tracks }));
    const stream = getRemoteStreamFromPeerConnection(pc);
    expect(stream.getTracks()).toEqual([audio, video]);
  });
});