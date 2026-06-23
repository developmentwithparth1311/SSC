import React from 'react';
import { ShieldCheck, LockKey } from '@phosphor-icons/react';
import { ProtocolVersion } from '../lib/signal/constants';
import { useLocale } from '../context/LocaleContext';

/**
 * Per-message encryption protocol label — Engine 8.6 migration UX.
 */
export default function EncryptionModeBadge({ protocol, compact = false }) {
  const { t } = useLocale();
  const isSignal = protocol === ProtocolVersion.SIGNAL_V1
    || protocol === ProtocolVersion.SIGNAL_GROUP_V1;

  if (compact) {
    return (
      <span
        className={`inline-flex items-center gap-0.5 font-mono text-[9px] tracking-wider uppercase ${
          isSignal ? 'text-[#34C759]' : 'text-[#FFD600]'
        }`}
        title={isSignal ? t('encryptionSignal') : t('encryptionLegacy')}
        data-testid={isSignal ? 'badge-signal' : 'badge-legacy'}
      >
        {isSignal ? <ShieldCheck size={9} weight="fill" /> : <LockKey size={9} />}
        {isSignal ? 'SIG' : 'RSA'}
      </span>
    );
  }

  return (
    <span
      className={`inline-flex items-center gap-1 font-mono text-[10px] tracking-wider uppercase ${
        isSignal ? 'text-[#34C759]' : 'text-[#FFD600]'
      }`}
      data-testid={isSignal ? 'badge-signal' : 'badge-legacy'}
    >
      {isSignal ? <ShieldCheck size={10} weight="fill" /> : <LockKey size={10} />}
      {isSignal ? t('encryptionSignal') : t('encryptionLegacy')}
    </span>
  );
}