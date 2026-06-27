import { toast } from 'sonner';
import { messagingGateI18nKey } from './messagingGate';

export function toastMessagingGateFailure(gate, t) {
  if (!gate || gate.ok) return;
  const key = messagingGateI18nKey(gate.reason);
  const msg = t(key);
  console.warn('[SSC] messaging blocked:', gate.reason, gate.detail || '');
  toast.error(gate.detail ? `${msg} (${gate.detail})` : msg);
}

export function toastEncryptFailure(err, t) {
  const detail = err?.response?.data?.detail || err?.message;
  console.error('[SSC] encrypt/send failed:', detail || err);
  if (detail) {
    toast.error(detail);
  } else {
    toast.error(t('encryptionErrEncrypt'));
  }
}