import React, { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { X, Shield, ShieldCheck, Copy, Check } from '@phosphor-icons/react';
import { api } from '../lib/api';
import { useAuth } from '../context/AuthContext';

export default function TwoFAModal({ open, onClose }) {
  const { user, refreshUser } = useAuth();
  const [step, setStep] = useState('idle'); // idle | setup | verify | disable
  const [secret, setSecret] = useState('');
  const [otpauth, setOtpauth] = useState('');
  const [backups, setBackups] = useState([]);
  const [code, setCode] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);
  const [backupsCopied, setBackupsCopied] = useState(false);

  useEffect(() => {
    if (open) {
      setCode(''); setPassword(''); setSecret(''); setOtpauth(''); setBackups([]); setBackupsCopied(false);
      setStep(user?.totp_enabled ? 'disable' : 'idle');
    }
  }, [open, user]);

  const start = async () => {
    setBusy(true);
    try {
      const { data } = await api.post('/auth/2fa/setup');
      setSecret(data.secret); setOtpauth(data.otpauth_url);
      setBackups(data.backup_codes || []);
      setStep('verify');
    } catch {
      toast.error('Could not start 2FA setup');
    } finally { setBusy(false); }
  };

  const verify = async (e) => {
    e?.preventDefault();
    setBusy(true);
    try {
      await api.post('/auth/2fa/verify', { code });
      await refreshUser();
      setBackups([]);
      toast.success('2FA enabled');
      onClose && onClose();
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Invalid code');
    } finally { setBusy(false); }
  };

  const disable = async (e) => {
    e?.preventDefault();
    setBusy(true);
    try {
      await api.post('/auth/2fa/disable', { code, password });
      await refreshUser();
      toast.success('2FA disabled');
      onClose && onClose();
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Invalid code');
    } finally { setBusy(false); }
  };

  const regenerateBackups = async () => {
    setBusy(true);
    try {
      const { data } = await api.post('/auth/2fa/backups');
      setBackups(data.backup_codes || []);
      setStep('verify'); // reuse to show
      toast.success('New backup codes generated');
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed');
    } finally { setBusy(false); }
  };

  const copySecret = async () => {
    try { await navigator.clipboard.writeText(secret); setCopied(true); setTimeout(() => setCopied(false), 2000); } catch {}
  };

  // Generate QR via Google Chart API (works without extra deps) — totp URL only, no PII
  const qrSrc = otpauth ? `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(otpauth)}&bgcolor=121212&color=00E5FF` : '';

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-xl flex items-center justify-center p-4" onClick={onClose}>
      <div className="w-full max-w-md bg-[#121212] tac-border rounded-md p-5 fade-up" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <ShieldCheck size={18} className="text-[#00E5FF]" weight="duotone" />
            <h3 className="font-mono text-xs tracking-[0.25em]">TWO_FACTOR_AUTH</h3>
          </div>
          <button onClick={onClose} className="text-[#A1A1AA] hover:text-white" data-testid="2fa-close"><X size={16} /></button>
        </div>

        {step === 'idle' && (
          <>
            <p className="text-sm text-[#A1A1AA]">Add an extra layer of security with a TOTP authenticator app (Google Authenticator, Authy, 1Password, etc.).</p>
            <button onClick={start} disabled={busy} data-testid="2fa-enable-button"
              className="w-full mt-5 py-2.5 bg-[#00E5FF] text-black font-medium text-sm rounded-md hover:brightness-110 transition disabled:opacity-40">
              {busy ? 'PREPARING…' : 'ENABLE 2FA'}
            </button>
          </>
        )}

        {step === 'verify' && (
          <form onSubmit={verify}>
            <p className="text-sm text-[#A1A1AA]">Scan the QR code or paste the secret into your authenticator app, then enter the 6-digit code.</p>
            <div className="mt-4 bg-[#1A1A1A] tac-border rounded-md p-3 flex items-center gap-4">
              {qrSrc && <img src={qrSrc} alt="2FA QR" className="w-[140px] h-[140px] rounded" data-testid="2fa-qr" />}
              <div className="flex-1 min-w-0">
                <div className="text-[10px] font-mono text-[#A1A1AA] tracking-widest">SECRET</div>
                <div className="font-mono text-xs break-all">{secret}</div>
                <button type="button" onClick={copySecret} className="mt-2 px-2 py-1 text-xs font-mono tac-border bg-[#121212] hover:bg-[#1A1A1A] rounded flex items-center gap-1" data-testid="2fa-copy-secret">
                  {copied ? <Check size={12} /> : <Copy size={12} />} {copied ? 'COPIED' : 'COPY'}
                </button>
              </div>
            </div>
            {backups.length > 0 && (
              <div className="mt-3">
                <div className="text-[10px] font-mono text-[#A1A1AA] tracking-widest">BACKUP CODES (save these!)</div>
                <div className="font-mono text-xs bg-[#1A1A1A] p-2 rounded break-all mt-1">{backups.join(' ')}</div>
                <button type="button" onClick={async () => { try { await navigator.clipboard.writeText(backups.join(' ')); setBackupsCopied(true); setTimeout(() => setBackupsCopied(false), 2000); } catch {} }} className="mt-1 px-2 py-1 text-xs font-mono tac-border bg-[#121212] hover:bg-[#1A1A1A] rounded flex items-center gap-1" data-testid="2fa-copy-backups">
                  {backupsCopied ? <Check size={12} /> : <Copy size={12} />} {backupsCopied ? 'COPIED' : 'COPY BACKUPS'}
                </button>
              </div>
            )}
            <input value={code} onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))} placeholder="000000"
              className="w-full mt-4 px-3 py-2.5 text-center font-mono text-2xl tracking-[0.4em]" data-testid="2fa-verify-input" />
            <button type="submit" disabled={code.length !== 6 || busy} data-testid="2fa-verify-button"
              className="w-full mt-3 py-2.5 bg-[#00E5FF] text-black font-medium text-sm rounded-md hover:brightness-110 transition disabled:opacity-40">
              {busy ? 'VERIFYING…' : 'CONFIRM 2FA'}
            </button>
          </form>
        )}

        {step === 'disable' && (
          <form onSubmit={disable}>
            <p className="text-sm text-[#A1A1AA]">2FA is currently <span className="text-[#34C759] font-mono">ENABLED</span>. Enter your password and a current code to turn it off.</p>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Account password"
              className="w-full mt-4 px-3 py-2.5 text-sm" data-testid="2fa-disable-password" autoComplete="current-password" />
            <input value={code} onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))} placeholder="000000"
              className="w-full mt-3 px-3 py-2.5 text-center font-mono text-2xl tracking-[0.4em]" data-testid="2fa-disable-input" />
            <button type="submit" disabled={code.length !== 6 || !password || busy} data-testid="2fa-disable-button"
              className="w-full mt-3 py-2.5 bg-[#FF3B30] text-white font-medium text-sm rounded-md hover:brightness-110 transition disabled:opacity-40">
              {busy ? 'DISABLING…' : 'DISABLE 2FA'}
            </button>
            <button type="button" onClick={regenerateBackups} disabled={busy} className="w-full mt-2 py-2 text-xs font-mono tac-border hover:bg-[#1A1A1A]">
              REGENERATE BACKUP CODES
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
