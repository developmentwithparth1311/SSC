import { toast } from 'sonner';
import { SignalingNotReadyError, signalingErrorI18nKey } from '../lib/signal/webrtcSignaling';

/** @returns {boolean} true when error was handled */
export function toastSignalingFailure(err, t) {
  if (!(err instanceof SignalingNotReadyError)) return false;
  const key = signalingErrorI18nKey(err.reason);
  console.warn('[SSC] outbound signaling blocked:', err.reason, err.detail || '');
  toast.error(t(key));
  return true;
}