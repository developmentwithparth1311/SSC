import { startIncomingRingtone, stopIncomingRingtone } from '../callRingtone';

describe('callRingtone', () => {
  beforeEach(() => {
    jest.useFakeTimers();
    class FakeOscillator {
      constructor() {
        this.frequency = { value: 0 };
        this.type = '';
      }
      connect() {}
      start() {}
      stop() {}
    }
    class FakeGain {
      constructor() {
        this.gain = { value: 0, setTargetAtTime: jest.fn() };
      }
      connect() {}
    }
    class FakeCtx {
      constructor() {
        this.state = 'running';
      }
      createGain() { return new FakeGain(); }
      createOscillator() { return new FakeOscillator(); }
      resume() { return Promise.resolve(); }
      close() { return Promise.resolve(); }
    }
    window.AudioContext = FakeCtx;
    window.webkitAudioContext = FakeCtx;
  });

  afterEach(() => {
    stopIncomingRingtone();
    jest.useRealTimers();
  });

  it('starts and stops without throwing', () => {
    expect(() => startIncomingRingtone()).not.toThrow();
    expect(() => stopIncomingRingtone()).not.toThrow();
  });

  it('can restart after stop', () => {
    startIncomingRingtone();
    stopIncomingRingtone();
    expect(() => startIncomingRingtone()).not.toThrow();
  });
});