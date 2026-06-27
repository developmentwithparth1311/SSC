import { act, renderHook } from '@testing-library/react';
import { useHoldToRecord } from '../useHoldToRecord';

describe('useHoldToRecord', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('starts recording after hold delay and sends on release', async () => {
    const startRecording = jest.fn().mockResolvedValue({ id: 'session-1' });
    const stopRecordingAndSend = jest.fn().mockResolvedValue(undefined);
    const cancelRecording = jest.fn();

    const { result } = renderHook(() => useHoldToRecord({
      startRecording,
      stopRecordingAndSend,
      cancelRecording,
    }));

    const preventDefault = jest.fn();
    const pointerEvent = { preventDefault, pointerId: 1, currentTarget: { setPointerCapture: jest.fn() } };

    await act(async () => {
      await result.current.onVoicePointerDown(pointerEvent);
    });

    expect(startRecording).not.toHaveBeenCalled();

    await act(async () => {
      jest.advanceTimersByTime(120);
      await Promise.resolve();
    });

    expect(startRecording).toHaveBeenCalled();
    expect(result.current.isRecording).toBe(true);

    await act(async () => {
      await result.current.onVoicePointerUp({ preventDefault });
    });

    expect(stopRecordingAndSend).toHaveBeenCalledWith({ id: 'session-1' });
    expect(result.current.isRecording).toBe(false);
  });

  it('cancels recording on pointer cancel', async () => {
    const startRecording = jest.fn().mockResolvedValue({ id: 'session-1' });
    const stopRecordingAndSend = jest.fn();
    const cancelRecording = jest.fn();

    const { result } = renderHook(() => useHoldToRecord({
      startRecording,
      stopRecordingAndSend,
      cancelRecording,
    }));

    const pointerEvent = {
      preventDefault: jest.fn(),
      pointerId: 1,
      currentTarget: { setPointerCapture: jest.fn() },
    };

    await act(async () => {
      await result.current.onVoicePointerDown(pointerEvent);
    });

    await act(async () => {
      jest.advanceTimersByTime(120);
      await Promise.resolve();
    });

    act(() => {
      result.current.onVoicePointerCancel();
    });

    expect(cancelRecording).toHaveBeenCalled();
    expect(stopRecordingAndSend).not.toHaveBeenCalled();
    expect(result.current.isRecording).toBe(false);
  });

  it('onVoiceClick only prevents default — no toggle', () => {
    const preventDefault = jest.fn();
    const { result } = renderHook(() => useHoldToRecord({
      startRecording: jest.fn(),
      stopRecordingAndSend: jest.fn(),
      cancelRecording: jest.fn(),
    }));

    act(() => {
      result.current.onVoiceClick({ preventDefault });
    });

    expect(preventDefault).toHaveBeenCalled();
  });
});