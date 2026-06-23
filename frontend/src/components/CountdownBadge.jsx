import React, { useEffect, useState } from 'react';

function formatRemaining(expiresAt) {
  const expMs = new Date(expiresAt).getTime();
  let diff = expMs - Date.now();
  if (diff < 0) diff = 0;
  const h = Math.floor(diff / 3600000);
  const m = Math.floor((diff % 3600000) / 60000);
  const s = Math.floor((diff % 60000) / 1000);
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

export default function CountdownBadge({ expiresAt }) {
  const [text, setText] = useState(() => formatRemaining(expiresAt));
  useEffect(() => {
    const t = setInterval(() => setText(formatRemaining(expiresAt)), 1000);
    return () => clearInterval(t);
  }, [expiresAt]);
  return <span className="font-mono text-[10px] text-[#A1A1AA] tracking-widest">{text}</span>;
}
