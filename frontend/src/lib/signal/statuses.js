/**
 * Stories / statuses — Engine 8.12 (signal_status_v1 Sender Keys).
 */
import { api } from '../api';
import { ProtocolVersion } from './constants';
import {
  createGroupSenderKeyDistribution,
  encryptGroupMessage as nativeEncryptGroup,
  processGroupSenderKeyDistribution,
} from './nativeLibsignal';
import { decryptGroupText } from './groupMessages';
import { canUseSignalMessaging, decryptSignalText, encryptSignalText } from './messages';
import { isNativeLibsignalAvailable } from './nativeLibsignal';
import { ensureSignalSession } from './x3dh';

export const STATUS_SKDM_MESSAGE_TYPE = 'status_skdm';
const STATUS_SKDM_ENVELOPE_TYPE = 'ssc_status_skdm';
const STATUS_SKDM_SENT_PREFIX = 'ssc_status_skdm_sent:';

export function isSignalStatusV1(status) {
  return (status?.protocol || ProtocolVersion.LEGACY_RSA) === ProtocolVersion.SIGNAL_STATUS_V1;
}

/** Stable per-author sender-key distribution id for status broadcast. */
export async function distributionIdForAuthor(authorId) {
  const data = new TextEncoder().encode(`ssc-status:${authorId}`);
  const hash = await crypto.subtle.digest('SHA-256', data);
  const bytes = new Uint8Array(hash).slice(0, 16);
  bytes[6] = (bytes[6] & 0x0f) | 0x50;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;
  const hex = [...bytes].map((b) => b.toString(16).padStart(2, '0')).join('');
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}

function statusSkdmSentKey(authorId) {
  return `${STATUS_SKDM_SENT_PREFIX}${authorId}`;
}

function getStatusSkdmSentSet(authorId) {
  try {
    return new Set(JSON.parse(localStorage.getItem(statusSkdmSentKey(authorId)) || '[]'));
  } catch {
    return new Set();
  }
}

function markStatusSkdmSent(authorId, contactId) {
  const sent = getStatusSkdmSentSet(authorId);
  sent.add(contactId);
  localStorage.setItem(statusSkdmSentKey(authorId), JSON.stringify([...sent]));
}

function buildStatusSkdmEnvelope({ authorId, distributionId, skdm }) {
  return JSON.stringify({
    t: STATUS_SKDM_ENVELOPE_TYPE,
    v: 1,
    author: authorId,
    dist: distributionId,
    skdm,
  });
}

function parseStatusSkdmEnvelope(plaintext) {
  try {
    const obj = JSON.parse(plaintext || '{}');
    if (obj?.t !== STATUS_SKDM_ENVELOPE_TYPE || !obj?.skdm || !obj?.author) return null;
    return obj;
  } catch {
    return null;
  }
}

export async function canUseSignalStatuses(contacts, ourUserId, user) {
  if (!isNativeLibsignalAvailable() || !user?.signal_prekeys_ready) return false;
  const audience = (contacts || []).filter((c) => !c.blocked && c.user_id !== ourUserId);
  if (audience.length === 0) return false;
  for (const c of audience) {
    if (!c.signal_prekeys_ready) return false;
    const ready = await canUseSignalMessaging(c.user_id, ourUserId, true);
    if (!ready) return false;
  }
  return true;
}

async function getOrCreateDmConversation(username) {
  const { data } = await api.post('/conversations', { peer_username: username });
  return data.conversation_id;
}

async function fanOutStatusSkdm({ authorId, distributionId, skdm, contacts, ourUserId }) {
  const sent = getStatusSkdmSentSet(authorId);
  const targets = contacts.filter(
    (c) => !c.blocked && c.user_id !== ourUserId && !sent.has(c.user_id),
  );
  for (const contact of targets) {
    await ensureSignalSession(contact.user_id, ourUserId);
    const envelope = buildStatusSkdmEnvelope({ authorId, distributionId, skdm });
    const enc = await encryptSignalText(contact.user_id, ourUserId, envelope);
    const conversationId = await getOrCreateDmConversation(contact.username);
    await api.post('/messages', {
      conversation_id: conversationId,
      protocol: ProtocolVersion.SIGNAL_V1,
      ciphertext: enc.ciphertext,
      signal_message_type: enc.signal_message_type,
      message_type: STATUS_SKDM_MESSAGE_TYPE,
      distribution_id: distributionId,
    });
    markStatusSkdmSent(authorId, contact.user_id);
  }
}

export async function ensureStatusSenderKeysDistributed({ authorId, contacts, ourUserId }) {
  const distributionId = await distributionIdForAuthor(authorId);
  const sent = getStatusSkdmSentSet(authorId);
  const pending = contacts.filter(
    (c) => !c.blocked && c.user_id !== ourUserId && !sent.has(c.user_id),
  );
  if (pending.length === 0) {
    return distributionId;
  }
  const { skdm } = await createGroupSenderKeyDistribution(ourUserId, distributionId);
  await fanOutStatusSkdm({ authorId, distributionId, skdm, contacts, ourUserId });
  return distributionId;
}

export async function encryptStatusText(authorId, ourUserId, plaintext) {
  const distributionId = await distributionIdForAuthor(authorId);
  return nativeEncryptGroup(ourUserId, distributionId, plaintext ?? '');
}

export async function decryptStatusText(authorId, status) {
  if (!isSignalStatusV1(status)) {
    throw new Error('not a signal_status_v1 status');
  }
  const shim = {
    protocol: ProtocolVersion.SIGNAL_GROUP_V1,
    ciphertext: status.ciphertext,
    signal_message_type: status.signal_message_type,
  };
  const result = await decryptGroupText(authorId, shim);
  return result;
}

export async function processIncomingStatusSkdmMessage(msg, { myUserId, peerUserId }) {
  if (msg?.message_type !== STATUS_SKDM_MESSAGE_TYPE) return false;
  if ((msg?.protocol || ProtocolVersion.LEGACY_RSA) !== ProtocolVersion.SIGNAL_V1) return false;
  const remoteId = msg.sender_id === myUserId ? peerUserId : msg.sender_id;
  if (!remoteId || !myUserId) return false;
  const plaintext = await decryptSignalText(remoteId, myUserId, msg);
  const envelope = parseStatusSkdmEnvelope(plaintext);
  if (!envelope) return false;
  await processGroupSenderKeyDistribution(envelope.author, envelope.skdm);
  return true;
}