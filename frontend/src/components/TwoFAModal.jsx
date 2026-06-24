import React, { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { X, ShieldCheck, Copy, Check } from '@phosphor-icons/react';
import QRCode from 'qrcode';
import { api } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { useLocale } from '../context/LocaleContext';

export default function TwoFAModal({ open, onClose }) {
  const { user, refreshUser } = useAuth();
  const { t } = useLocale();
  const [step, setStep] = useState('idle');
  const [secret, setSecret] = useState('');
  const [otpauth, setOtpauth] = useState('');
  const [qrDataUrl, setQrDataUrl] = useState('');
  const [backups, setBackups] = useState([]);
  const [code, setCode] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);
  const [backupsCopied, setBackupsCopied] = useState(false);

  useEffect(() => {
    if (open) {
      setCode('');
      setPassword('');
      setSecret('');
      setOtpauth('');
      setQrDataUrl('');
      setBackups([]);
      setBackupsCopied(false);
      setStep(user?.totp_enabled ? 'disable' : 'idle');
    }
  }, [open, user]);

  useEffect(() => {
    if (!otpauth) {
      setQrDataUrl('');
      return;
    }
    QRCode.toDataURL(otpauth, {
      width: 200,
      margin: 1,
      color: { dark: '#00E5FF', light: '#121212' },
    }).then(setQrDataUrl).catch(() => setQrDataUrl(''));
  }, [otpauth]);

  const start = async () => {
    setBusy(true);
    try {
      const { data } = await api.post('/auth/2fa/setup');
      setSecret(data.secret);
      setOtpauth(data.otpauth_url);
      setBackups(data.backup_codes || []);
      setStep('verify');
    } catch {
      toast.error(t('twoFaSetupFailed'));
    } finally {
      setBusy(false);
    }
  };

  const verify = async (e) => {
    e?.preventDefault();
    setBusy(true);
    try {
      await api.post('/auth/2fa/verify', { code });
      await refreshUser();
      setBackups([]);
      toast.success(t('twoFaEnabled'));
      onClose?.();
    } catch (err) {
      toast.error(err?.response?.data?.detail || t('twoFaInvalidCode'));
    } finally {
      setBusy(false);
    }
  };

  const disable = async (e) => {
    e?.preventDefault();
    setBusy(true);
    try {
      await api.post('/auth/2fa/disable', { code, password });
      await refreshUser();
      toast.success(t('twoFaDisabled'));
      onClose?.();
    } catch (err) {
      toast.error(err?.response?.data?.detail || t('twoFaInvalidCode'));
    } finally {
      setBusy(false);
    }
  };

  const regenerateBackups = async () => {
    setBusy(true);
    try {
      const { data } = await api.post('/auth/2fa/backups');
      setBackups(data.backup_codes || []);
      setStep('backups');
      toast.success(t('twoFaBackupsRegenerated'));
    } catch (err) {
      toast.error(err?.response?.data?.detail || t('twoFaBackupsFailed'));
    } finally {
      setBusy(false);
    }
  };

  const copySecret = async () => {
    try {
      await navigator.clipboard.writeText(secret);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {}
  };

  const copyBackups = async () => {
    try {
      await navigator.clipboard.writeText(backups.join(' '));
      setBackupsCopied(true);
      setTimeout(() => setBackupsCopied(false), 2000);
    } catch {}
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[55] bg-black/80 backdrop-blur-xl flex items-center justify-center p-4" onClick={onClose}>
      <div className="w-full max-w-md bg-[#121212] tac-border rounded-md p-5 fade-up max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <ShieldCheck size={18} className="text-[#00E5FF]" weight="duotone" />
            <h3 className="font-mono text-xs tracking-[0.25em]">{t('twoFaTitle')}</h3>
          </div>
          <button onClick={onClose} className="text-[#A1A1AA] hover:text-white" data-testid="2fa-close"><X size={16} /></button>
        </div>

        {step === 'idle' && (
          <>
            <p className="text-sm text-[#A1A1AA]">{t('twoFaIntro')}</p>
            <button onClick={start} disabled={busy} data-testid="2fa-enable-button"
              className="w-full mt-5 py-2.5 bg-[#00E5FF] text-black font-medium text-sm rounded-md hover:brightness-110 transition disabled:opacity-40">
              {busy ? t('twoFaPreparing') : t('settingsEnable2fa')}
            </button>
          </>
        )}

        {step === 'verify' && (
          <form onSubmit={verify}>
            <p className="text-sm text-[#A1A1AA]">{t('twoFaScanHint')}</p>
            <div className="mt-4 bg-[#1A1A1A] tac-border rounded-md p-3 flex items-center gap-4">
              {qrDataUrl && <img src={qrDataUrl} alt="" className="w-[140px] h-[140px] rounded" data-testid="2fa-qr" />}
              <div className="flex-1 min-w-0">
                <div className="text-[10px] font-mono text-[#A1A1AA] tracking-widest">{t('twoFaSecret')}</div>
                <div className="font-mono text-xs break-all">{secret}</div>
                <button type="button" onClick={copySecret} className="mt-2 px-2 py-1 text-xs font-mono tac-border bg-[#121212] hover:bg-[#1A1A1A] rounded flex items-center gap-1" data-testid="2fa-copy-secret">
                  {copied ? <Check size={12} /> : <Copy size={12} />} {copied ? t('copied') : t('copy')}
                </button>
              </div>
            </div>
            {backups.length > 0 && (
              <div className="mt-3">
                <div className="text-[10px] font-mono text-[#A1A1AA] tracking-widest">{t('twoFaBackupCodes')}</div>
                <div className="font-mono text-xs bg-[#1A1A1A] p-2 rounded break-all mt-1">{backups.join(' ')}</div>
                <button type="button" onClick={copyBackups} className="mt-1 px-2 py-1 text-xs font-mono tac-border bg-[#121212] hover:bg-[#1A1A1A] rounded flex items-center gap-1" data-testid="2fa-copy-backups">
                  {backupsCopied ? <Check size={12} /> : <Copy size={12} />} {backupsCopied ? t('copied') : t('twoFaCopyBackups')}
                </button>
              </div>
            )}
            <input value={code} onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))} placeholder="000000"
              className="w-full mt-4 px-3 py-2.5 text-center font-mono text-2xl tracking-[0.4em] bg-[#1A1A1A] border border-[#27272A] rounded-md" data-testid="2fa-verify-input" />
            <button type="submit" disabled={code.length !== 6 || busy} data-testid="2fa-verify-button"
              className="w-full mt-3 py-2.5 bg-[#00E5FF] text-black font-medium text-sm rounded-md hover:brightness-110 transition disabled:opacity-40">
              {busy ? t('twoFaVerifying') : t('twoFaConfirm')}
            </button>
          </form>
        )}

        {step === 'backups' && (
          <div>
            <p className="text-sm text-[#A1A1AA]">{t('twoFaBackupsSaveHint')}</p>
            <div className="font-mono text-xs bg-[#1A1A1A] p-3 rounded break-all mt-3">{backups.join(' ')}</div>
            <button type="button" onClick={copyBackups} className="mt-2 px-2 py-1 text-xs font-mono tac-border bg-[#121212] hover:bg-[#1A1A1A] rounded flex items-center gap-1" data-testid="2fa-copy-backups-regen">
              {backupsCopied ? <Check size={12} /> : <Copy size={12} />} {backupsCopied ? t('copied') : t('twoFaCopyBackups')}
            </button>
            <button type="button" onClick={() => setStep('disable')} className="w-full mt-4 py-2.5 text-sm border border-[#27272A] rounded-md hover:bg-[#1A1A1A]">
              {t('close')}
            </button>
          </div>
        )}

        {step === 'disable' && (
          <form onSubmit={disable}>
            <p className="text-sm text-[#A1A1AA]">{t('twoFaDisableHint')}</p>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder={t('password')}
              className="w-full mt-4 px-3 py-2.5 text-sm bg-[#1A1A1A] border border-[#27272A] rounded-md" data-testid="2fa-disable-password" autoComplete="current-password" />
            <input value={code} onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))} placeholder="000000"
              className="w-full mt-3 px-3 py-2.5 text-center font-mono text-2xl tracking-[0.4em] bg-[#1A1A1A] border border-[#27272A] rounded-md" data-testid="2fa-disable-input" />
            <button type="submit" disabled={code.length !== 6 || !password || busy} data-testid="2fa-disable-button"
              className="w-full mt-3 py-2.5 bg-[#FF3B30] text-white font-medium text-sm rounded-md hover:brightness-110 transition disabled:opacity-40">
              {busy ? t('twoFaDisabling') : t('twoFaDisable')}
            </button>
            <button type="button" onClick={regenerateBackups} disabled={busy} data-testid="2fa-regenerate-backups"
              className="w-full mt-2 py-2 text-xs font-mono tac-border hover:bg-[#1A1A1A] rounded-md">
              {t('twoFaRegenerateBackups')}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}