import React, { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { X, ShieldCheck, Check, QrCode, Camera } from '@phosphor-icons/react';
import { publicKeyFingerprint } from '../lib/crypto';

/**
 * Verified Handshake — shows a Safety Number (fingerprint of both public keys),
 * a QR code containing the same number, and lets the user mark the peer as verified.
 * Verification is stored locally per device (localStorage).
 */
export default function VerifyHandshakeModal({ open, onClose, me, peer }) {
  const [code, setCode] = useState('');
  const [verified, setVerified] = useState(false);

  useEffect(() => {
    if (!open || !me?.public_key || !peer?.public_key) return;
    (async () => {
      try {
        const myPub = typeof me.public_key === 'string' ? JSON.parse(me.public_key) : me.public_key;
        const peerPub = typeof peer.public_key === 'string' ? JSON.parse(peer.public_key) : peer.public_key;
        const a = await publicKeyFingerprint(myPub);
        const b = await publicKeyFingerprint(peerPub);
        // canonicalize order so both sides see the same number
        const [first, second] = a < b ? [a, b] : [b, a];
        // group into 5-digit blocks (numeric, easier to compare verbally)
        const combined = (first + second).replace(/[^a-fA-F0-9]/g, '').toUpperCase();
        const blocks = [];
        for (let i = 0; i < 60; i += 5) blocks.push(combined.slice(i, i + 5));
        setCode(blocks.join(' '));
      } catch (e) {
        setCode('');
      }
    })();
    setVerified(!!localStorage.getItem(`ssc_verified_${peer?.user_id}`));
  }, [open, me, peer]);

  const markVerified = () => {
    localStorage.setItem(`ssc_verified_${peer.user_id}`, '1');
    setVerified(true);
    toast.success('Identity verified');
    window.dispatchEvent(new Event('ssc-verified-change'));
  };
  const unverify = () => {
    localStorage.removeItem(`ssc_verified_${peer.user_id}`);
    setVerified(false);
    window.dispatchEvent(new Event('ssc-verified-change'));
  };

  const qrSrc = code ? `https://api.qrserver.com/v1/create-qr-code/?size=240x240&bgcolor=121212&color=00E5FF&qzone=1&data=${encodeURIComponent('SSC:' + code.replace(/ /g, ''))}` : '';

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-xl flex items-center justify-center p-4" onClick={onClose}>
      <div className="w-full max-w-md bg-[#121212] tac-border rounded-md p-5 fade-up" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <ShieldCheck size={18} weight="duotone" className={verified ? 'text-[#34C759]' : 'text-[#00E5FF]'} />
            <h3 className="font-mono text-xs tracking-[0.25em]">VERIFY_IDENTITY</h3>
          </div>
          <button onClick={onClose} className="text-[#A1A1AA] hover:text-white" data-testid="verify-close"><X size={16} /></button>
        </div>

        <p className="text-xs text-[#A1A1AA] mb-4">
          Compare this 60-character safety number with <span className="text-white">@{peer?.username}</span> in person, via voice/video call, or another trusted channel.
          If they match, you have proven you're talking to the real person — not a man-in-the-middle.
        </p>

        <div className="flex justify-center mb-3">
          {qrSrc ? <img src={qrSrc} alt="safety number QR" className="w-[240px] h-[240px] rounded-md tac-border" data-testid="verify-qr" /> : <div className="w-[240px] h-[240px] bg-[#1A1A1A] rounded-md flex items-center justify-center"><QrCode size={32} className="text-[#A1A1AA]" /></div>}
        </div>

        <div className="bg-[#1A1A1A] tac-border rounded-md p-3 mb-4">
          <div className="text-[10px] font-mono text-[#A1A1AA] tracking-widest mb-1">SAFETY_NUMBER</div>
          <div className="font-mono text-sm leading-relaxed select-all break-words" data-testid="verify-safety-number">{code || '…'}</div>
        </div>

        {verified ? (
          <div>
            <div className="flex items-center justify-center gap-2 text-[#34C759] font-mono text-xs tracking-widest mb-3" data-testid="verified-status">
              <Check size={14} weight="bold" /> IDENTITY_VERIFIED
            </div>
            <button onClick={unverify} data-testid="verify-unverify-button" className="w-full py-2 text-xs font-mono text-[#A1A1AA] hover:text-[#FF3B30]">CLEAR_VERIFICATION</button>
          </div>
        ) : (
          <button onClick={markVerified} data-testid="verify-mark-button"
            className="w-full py-2.5 bg-[#34C759] text-black font-medium text-sm rounded-md hover:brightness-110 transition">
            MARK AS VERIFIED
          </button>
        )}
      </div>
    </div>
  );
}
