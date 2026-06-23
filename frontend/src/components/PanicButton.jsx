import React, { useEffect, useRef, useState } from 'react';
import { Warning } from '@phosphor-icons/react';
import { useLocale } from '../context/LocaleContext';

/**
 * PanicButton: press & hold 1.5s -> wipes everything
 * Visual countdown via conic-gradient.
 */
export default function PanicButton({ onWipe }) {
  const { t } = useLocale();
  const [progress, setProgress] = useState(0);
  const [pressing, setPressing] = useState(false);
  const timerRef = useRef(null);
  const startRef = useRef(0);
  const DURATION = 1500;

  const start = () => {
    if (pressing) return;
    setPressing(true);
    startRef.current = Date.now();
    timerRef.current = setInterval(() => {
      const elapsed = Date.now() - startRef.current;
      const p = Math.min(1, elapsed / DURATION);
      setProgress(p);
      if (p >= 1) {
        clearInterval(timerRef.current);
        document.body.classList.add('panic-flash');
        setTimeout(() => document.body.classList.remove('panic-flash'), 1100);
        setPressing(false);
        setProgress(0);
        onWipe && onWipe();
      }
    }, 30);
  };

  const cancel = () => {
    if (timerRef.current) clearInterval(timerRef.current);
    setPressing(false);
    setProgress(0);
  };

  useEffect(() => () => timerRef.current && clearInterval(timerRef.current), []);

  return (
    <button
      data-testid="panic-wipe-button"
      onMouseDown={start} onMouseUp={cancel} onMouseLeave={cancel}
      onTouchStart={start} onTouchEnd={cancel}
      className="relative h-9 px-3 rounded-md bg-[#FF3B30] text-white font-mono text-xs tracking-[0.25em] flex items-center gap-2 hover:brightness-110 transition select-none overflow-hidden"
      title={t('panicTitle')}
    >
      <span
        className="absolute inset-0 rounded-md lp-fill"
        style={{ ['--p']: `${Math.round(progress * 100)}%`, opacity: 0.35 }}
      />
      <Warning size={14} weight="bold" className="relative z-10" />
      <span className="relative z-10">{pressing ? t('panicHold') : t('panic')}</span>
    </button>
  );
}