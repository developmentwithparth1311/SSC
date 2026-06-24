/**
 * Incoming-call ringtone — Web Audio oscillator pattern (no asset file).
 * Loops until stopIncomingRingtone().
 */

let audioCtx = null;
let gainNode = null;
let oscA = null;
let oscB = null;
let pulseTimer = null;
let ringing = false;

function ensureContext() {
  if (!audioCtx) {
    const Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return null;
    audioCtx = new Ctx();
  }
  if (audioCtx.state === 'suspended') {
    audioCtx.resume().catch(() => {});
  }
  return audioCtx;
}

function startOscillators() {
  const ctx = ensureContext();
  if (!ctx || ringing) return;
  ringing = true;

  gainNode = ctx.createGain();
  gainNode.gain.value = 0;
  gainNode.connect(ctx.destination);

  oscA = ctx.createOscillator();
  oscB = ctx.createOscillator();
  oscA.type = 'sine';
  oscB.type = 'sine';
  oscA.frequency.value = 440;
  oscB.frequency.value = 480;
  oscA.connect(gainNode);
  oscB.connect(gainNode);
  oscA.start();
  oscB.start();

  let on = false;
  const pulse = () => {
    if (!ringing || !gainNode) return;
    on = !on;
    gainNode.gain.setTargetAtTime(on ? 0.22 : 0, ctx.currentTime, 0.02);
  };
  pulse();
  pulseTimer = window.setInterval(pulse, 900);
}

export function startIncomingRingtone() {
  try {
    startOscillators();
  } catch {
    // Autoplay policy or missing Web Audio — ring UI still shows
  }
}

export function stopIncomingRingtone() {
  ringing = false;
  if (pulseTimer) {
    clearInterval(pulseTimer);
    pulseTimer = null;
  }
  try {
    oscA?.stop();
    oscB?.stop();
  } catch {}
  oscA = null;
  oscB = null;
  gainNode = null;
  if (audioCtx) {
    audioCtx.close().catch(() => {});
    audioCtx = null;
  }
}