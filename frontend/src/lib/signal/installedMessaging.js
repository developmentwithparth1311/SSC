/**
 * Installed clients use Signal only — no vault/password UX (Engine 8 unified identity).
 */
import { isInstalledClient } from '../platform';
import { evaluateMessagingGate } from '../../chat/messagingGate';

/** True when this device must never fall back to RSA vault messaging. */
export function usesSignalOnlyMessaging() {
  return isInstalledClient();
}

/**
 * Upload prekeys, refresh user, establish session — then decide Signal send path.
 * @returns {Promise<boolean>} useSignal when ok; false when blocked
 */
export async function prepareInstalledMessaging(opts) {
  const gate = await evaluateMessagingGate(opts);
  return gate.ok && gate.useSignal;
}

export { evaluateMessagingGate as prepareInstalledMessagingDetailed };