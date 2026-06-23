/**
 * Signal-style numeric safety numbers — Engine 8.2.
 * Port of Open Whisper Systems NumericFingerprintGenerator (5200 iterations, 60 digits).
 * Compatible with libsignal identity keys when signal_v1 is present.
 */
import { identityKeyToBytes } from './identityKey';

export const FINGERPRINT_ITERATIONS = 5200;
export const FINGERPRINT_VERSION = 0;
export const SAFETY_NUMBER_LENGTH = 60;

function combineBytes(...parts) {
  const total = parts.reduce((n, p) => n + p.length, 0);
  const out = new Uint8Array(total);
  let offset = 0;
  for (const part of parts) {
    out.set(part, offset);
    offset += part.length;
  }
  return out;
}

function shortToBytes(value) {
  const out = new Uint8Array(2);
  const view = new DataView(out.buffer);
  view.setInt16(0, value, false);
  return out;
}

function byteArray5ToLong(bytes, offset) {
  let result = 0;
  for (let i = 0; i < 5; i += 1) {
    result = (result << 8) | (bytes[offset + i] & 0xff);
  }
  return result;
}

function getDisplayStringFor(fingerprint) {
  const chunks = [0, 5, 10, 15, 20, 25].map((offset) => {
    const chunk = byteArray5ToLong(fingerprint, offset) % 100000;
    return String(chunk).padStart(5, '0');
  });
  return chunks.join('');
}

function stableIdBytes(userId) {
  return new TextEncoder().encode(String(userId || ''));
}

async function sha512(data) {
  const digest = await crypto.subtle.digest('SHA-512', data);
  return new Uint8Array(digest);
}

/** Matches Signal NumericFingerprintGenerator (5200 iterations). */
async function getFingerprint(iterations, stableIdentifier, identityKeyBytes) {
  const version = shortToBytes(FINGERPRINT_VERSION);
  let hash = combineBytes(version, identityKeyBytes, stableIdentifier);
  const publicKey = identityKeyBytes;

  for (let i = 0; i < iterations; i += 1) {
    const data = combineBytes(hash, publicKey);
    hash = await sha512(data);
  }
  return hash;
}

/**
 * @param {import('./identityKey').ResolvedIdentity} myIdentity
 * @param {string} myUserId
 * @param {import('./identityKey').ResolvedIdentity} peerIdentity
 * @param {string} peerUserId
 */
export async function computeSafetyNumberV3(myIdentity, myUserId, peerIdentity, peerUserId) {
  const myKeyBytes = await identityKeyToBytes(myIdentity);
  const peerKeyBytes = await identityKeyToBytes(peerIdentity);

  const localFingerprint = await getFingerprint(
    FINGERPRINT_ITERATIONS,
    stableIdBytes(myUserId),
    myKeyBytes,
  );
  const remoteFingerprint = await getFingerprint(
    FINGERPRINT_ITERATIONS,
    stableIdBytes(peerUserId),
    peerKeyBytes,
  );

  const localDisplay = getDisplayStringFor(localFingerprint);
  const remoteDisplay = getDisplayStringFor(remoteFingerprint);
  const canonical = localDisplay <= remoteDisplay
    ? localDisplay + remoteDisplay
    : remoteDisplay + localDisplay;

  const blocks = [];
  for (let i = 0; i < SAFETY_NUMBER_LENGTH; i += 5) {
    blocks.push(canonical.slice(i, i + 5));
  }

  return {
    display: blocks.join(' '),
    canonical,
    localDisplay,
    remoteDisplay,
    keyType: myIdentity.type,
  };
}

export function normalizeSafetyNumberInput(input) {
  return String(input || '').replace(/\D/g, '').slice(0, SAFETY_NUMBER_LENGTH);
}

export function safetyNumbersMatch(expectedCanonical, pasted) {
  const a = normalizeSafetyNumberInput(expectedCanonical);
  const b = normalizeSafetyNumberInput(pasted);
  return a.length === SAFETY_NUMBER_LENGTH && a === b;
}

/** QR payload — stays on device (no third-party QR API). */
export function buildVerifyQrPayload(canonical, peerUserId) {
  return `ssc-verify:v3:${normalizeSafetyNumberInput(canonical)}:${peerUserId || ''}`;
}

export function parseVerifyQrPayload(raw) {
  const text = String(raw || '').trim();
  if (!text.startsWith('ssc-verify:v3:')) return null;
  const parts = text.split(':');
  if (parts.length < 4) return null;
  const canonical = normalizeSafetyNumberInput(parts[2]);
  if (canonical.length !== SAFETY_NUMBER_LENGTH) return null;
  return { canonical, peerUserId: parts.slice(3).join(':') || '' };
}