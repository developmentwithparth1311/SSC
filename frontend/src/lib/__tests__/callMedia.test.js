import {
  mediaConstraintsForMode,
  bindRemoteStream,
  bindLocalPreview,
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
});