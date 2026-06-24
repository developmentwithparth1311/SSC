import React from 'react';
import { X, Warning } from '@phosphor-icons/react';
import { useLocale } from '../context/LocaleContext';

export default function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel,
  cancelLabel,
  danger = false,
  onConfirm,
  onCancel,
  testId = 'confirm-dialog',
}) {
  const { t } = useLocale();
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[70] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4" data-testid={testId}>
      <div className="w-full max-w-sm bg-[#121212] tac-border rounded-md p-4 fade-up">
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-center gap-2">
            <Warning size={18} className={danger ? 'text-[#FF3B30]' : 'text-[#FF9500]'} />
            <h3 className="font-mono text-xs tracking-wider">{title}</h3>
          </div>
          <button type="button" onClick={onCancel} className="text-[#A1A1AA] hover:text-white">
            <X size={16} />
          </button>
        </div>
        <p className="text-sm text-[#A1A1AA] leading-relaxed">{message}</p>
        <div className="flex gap-2 mt-5">
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 py-2.5 text-sm border border-[#27272A] rounded-md hover:bg-[#1A1A1A]"
            data-testid={`${testId}-cancel`}
          >
            {cancelLabel || t('cancel')}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className={`flex-1 py-2.5 text-sm font-medium rounded-md hover:brightness-110 ${
              danger ? 'bg-[#FF3B30] text-white' : 'bg-[#00E5FF] text-black'
            }`}
            data-testid={`${testId}-confirm`}
          >
            {confirmLabel || t('confirm')}
          </button>
        </div>
      </div>
    </div>
  );
}