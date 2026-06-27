import { useCallback, useRef, useState } from 'react';

const HOLD_DELAY_MS = 120;

/**
 * Hold to record, release to send — same UX on mobile, desktop, and Electron.
 */
export function useHoldToRecord({ startRecording, stopRecordingAndSend, cancelRecording }) {
  const [isRecording, setIsRecording] = useState(false);
  const holdTimerRef = useRef(null);
  const recordingSessionRef = useRef(null);
  const holdActiveRef = useRef(false);

  const clearHoldTimer = useCallback(() => {
    if (holdTimerRef.current) {
      clearTimeout(holdTimerRef.current);
      holdTimerRef.current = null;
    }
  }, []);

  const onVoicePointerDown = useCallback(async (e) => {
    e.preventDefault();
    if (e.currentTarget?.setPointerCapture) {
      try {
        e.currentTarget.setPointerCapture(e.pointerId);
      } catch {
        // ignore — capture unsupported on some browsers
      }
    }
    holdActiveRef.current = true;
    clearHoldTimer();
    holdTimerRef.current = setTimeout(async () => {
      if (!holdActiveRef.current) return;
      const session = await startRecording();
      if (session) {
        recordingSessionRef.current = session;
        setIsRecording(true);
      }
    }, HOLD_DELAY_MS);
  }, [startRecording, clearHoldTimer]);

  const onVoicePointerUp = useCallback(async (e) => {
    e.preventDefault();
    holdActiveRef.current = false;
    clearHoldTimer();
    if (recordingSessionRef.current) {
      const session = recordingSessionRef.current;
      recordingSessionRef.current = null;
      setIsRecording(false);
      await stopRecordingAndSend(session);
    }
  }, [stopRecordingAndSend, clearHoldTimer]);

  const onVoicePointerCancel = useCallback(() => {
    holdActiveRef.current = false;
    clearHoldTimer();
    if (recordingSessionRef.current) {
      recordingSessionRef.current = null;
      setIsRecording(false);
      cancelRecording();
    }
  }, [cancelRecording, clearHoldTimer]);

  /** Prevent click from toggling recording — hold/release only. */
  const onVoiceClick = useCallback((e) => {
    e.preventDefault();
  }, []);

  return {
    isRecording,
    setIsRecording,
    onVoicePointerDown,
    onVoicePointerUp,
    onVoicePointerCancel,
    onVoiceClick,
  };
}