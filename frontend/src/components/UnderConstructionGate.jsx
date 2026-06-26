import React, { useEffect, useState } from 'react';
import { HardHat, LockKey, TrafficCone, EnvelopeSimple, Key } from '@phosphor-icons/react';
import { useLocale } from '../context/LocaleContext';
import LanguagePicker from './LanguagePicker';
import MarketingPage from './MarketingPage';
import {
  isSitePreviewAccessConfigured,
  isSitePreviewLocked,
  verifySitePreviewPassword,
} from '../lib/siteGate';

const CONTACT_EMAIL = 'contact@supersecurechat.com';

function ProgressBar({ label, hint }) {
  const [value, setValue] = useState(68);

  useEffect(() => {
    const id = window.setInterval(() => {
      setValue((v) => {
        if (v >= 74) return 68;
        return v + 1;
      });
    }, 1400);
    return () => window.clearInterval(id);
  }, []);

  return (
    <div className="mt-8" data-testid="construction-progress">
      <div className="flex items-center justify-between text-xs text-[#71717A] mb-2">
        <span>{label}</span>
        <span>{value}% · {hint}</span>
      </div>
      <div className="h-2 rounded-full bg-[#1A1A1A] border border-[#27272A] overflow-hidden">
        <div
          className="h-full rounded-full bg-gradient-to-r from-[#00E5FF] to-[#34C759] transition-all duration-700 ease-out"
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}

export default function UnderConstructionGate({ onBypass }) {
  const { t } = useLocale();
  const [accessOpen, setAccessOpen] = useState(false);
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(false);
  const [error, setError] = useState('');
  const [locked, setLocked] = useState(() => isSitePreviewLocked());
  const accessEnabled = isSitePreviewAccessConfigured();

  useEffect(() => {
    const meta = document.querySelector('meta[name="robots"]');
    if (meta) {
      meta.setAttribute('content', 'noindex, nofollow');
      return undefined;
    }
    const el = document.createElement('meta');
    el.name = 'robots';
    el.content = 'noindex, nofollow';
    document.head.appendChild(el);
    return () => el.remove();
  }, []);

  const bullets = [
    t('constructionBullet1'),
    t('constructionBullet2'),
    t('constructionBullet3'),
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    if (isSitePreviewLocked()) {
      setLocked(true);
      setError(t('constructionPasswordLocked'));
      return;
    }
    if (!verifySitePreviewPassword(password)) {
      setLocked(isSitePreviewLocked());
      setPassword('');
      setError(t('constructionPasswordWrong'));
      return;
    }
    onBypass?.({ persist: remember });
  };

  return (
    <MarketingPage gate={false} className="bg-[#0A0A0A] text-[#F0F0F0] relative overflow-hidden">
      <div
        aria-hidden
        className="absolute top-0 left-0 right-0 h-1.5 construction-stripes pointer-events-none"
      />
      <div className="fixed -top-32 right-0 w-[420px] h-[420px] rounded-full bg-[#FFD600] opacity-[0.05] blur-3xl pointer-events-none" />
      <div className="fixed bottom-0 left-0 w-[380px] h-[380px] rounded-full bg-[#00E5FF] opacity-[0.06] blur-3xl pointer-events-none" />

      <header className="relative z-10 max-w-3xl mx-auto px-6 pt-8 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3" data-testid="construction-logo">
          <div className="w-10 h-10 rounded-lg bg-[#00E5FF] flex items-center justify-center">
            <LockKey size={22} weight="bold" className="text-black" />
          </div>
          <div>
            <div className="text-sm font-semibold">Super Secure Chat</div>
            <div className="text-[11px] text-[#71717A]">supersecurechat.com</div>
          </div>
        </div>
        <LanguagePicker className="w-28 hidden sm:flex" />
      </header>

      <main className="relative z-10 flex-1 flex items-center justify-center px-6 py-12">
        <div
          className="w-full max-w-xl rounded-2xl border border-[#27272A] bg-[#121212]/95 p-8 md:p-10 shadow-2xl fade-up"
          data-testid="under-construction-gate"
        >
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 rounded-xl bg-[#FFD600]/15 flex items-center justify-center shrink-0 construction-bob">
              <HardHat size={32} className="text-[#FFD600]" weight="duotone" />
            </div>
            <div>
              <p className="text-xs font-medium uppercase tracking-widest text-[#FFD600]">
                {t('constructionLabel')}
              </p>
              <h1 className="mt-2 text-2xl md:text-3xl font-semibold tracking-tight leading-tight">
                {t('constructionHeadline')}
              </h1>
            </div>
          </div>

          <p className="mt-6 text-[#A1A1AA] leading-relaxed">
            {t('constructionBody')}
          </p>

          <ul className="mt-6 space-y-3">
            {bullets.map((line) => (
              <li key={line} className="flex items-start gap-3 text-sm text-[#D4D4D8]">
                <TrafficCone size={18} className="text-[#00E5FF] shrink-0 mt-0.5" weight="duotone" />
                <span>{line}</span>
              </li>
            ))}
          </ul>

          <ProgressBar label={t('constructionProgressLabel')} hint={t('constructionProgressHint')} />

          <div className="mt-8 rounded-xl border border-[#27272A] bg-[#0F0F10] px-4 py-4 flex items-start gap-3">
            <EnvelopeSimple size={20} className="text-[#00E5FF] shrink-0 mt-0.5" />
            <div>
              <p className="text-sm text-[#A1A1AA]">{t('constructionContact')}</p>
              <a
                href={`mailto:${CONTACT_EMAIL}`}
                className="mt-1 inline-block text-[#00E5FF] font-medium hover:brightness-110 transition"
                data-testid="construction-contact-email"
              >
                {CONTACT_EMAIL}
              </a>
            </div>
          </div>

          {accessEnabled ? (
            <div className="mt-8 pt-6 border-t border-[#27272A]/80">
              {!accessOpen ? (
                <div className="text-center">
                  <button
                    type="button"
                    onClick={() => setAccessOpen(true)}
                    className="text-xs text-[#52525B] hover:text-[#A1A1AA] transition underline-offset-4 hover:underline"
                    data-testid="construction-access-trigger"
                  >
                    {t('constructionAccessLink')}
                  </button>
                </div>
              ) : (
                <form
                  onSubmit={handleSubmit}
                  className="space-y-4 fade-up"
                  data-testid="construction-access-form"
                >
                  <div className="flex items-center justify-center gap-2 text-sm text-[#A1A1AA]">
                    <Key size={16} className="text-[#FFD600]" />
                    {t('constructionAccessHint')}
                  </div>
                  <label className="block text-left">
                    <span className="text-xs text-[#71717A]">{t('constructionPasswordLabel')}</span>
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder={t('constructionPasswordPlaceholder')}
                      autoComplete="off"
                      disabled={locked}
                      className="mt-2 w-full px-4 py-3 text-base"
                      data-testid="construction-password-input"
                    />
                  </label>
                  <label className="flex items-center gap-2 text-xs text-[#71717A] cursor-pointer">
                    <input
                      type="checkbox"
                      checked={remember}
                      onChange={(e) => setRemember(e.target.checked)}
                      disabled={locked}
                      className="rounded border-[#3F3F46]"
                    />
                    {t('constructionRememberDevice')}
                  </label>
                  {error ? (
                    <p className="text-sm text-[#FF6B6B] text-center" data-testid="construction-password-error">
                      {error}
                    </p>
                  ) : null}
                  <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
                    <button
                      type="submit"
                      className="btn-primary w-full sm:w-auto"
                      disabled={locked || !password.trim()}
                      data-testid="construction-password-submit"
                    >
                      {t('constructionPasswordSubmit')}
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setAccessOpen(false);
                        setPassword('');
                        setError('');
                      }}
                      className="btn-secondary w-full sm:w-auto"
                    >
                      {t('constructionAccessDismiss')}
                    </button>
                  </div>
                </form>
              )}
            </div>
          ) : null}
        </div>
      </main>

      <footer className="relative z-10 px-6 pb-8 text-center text-xs text-[#52525B]">
        © {new Date().getFullYear()} Super Secure Chat · {t('constructionFooter')}
      </footer>
    </MarketingPage>
  );
}