import { WebPlugin } from '@capacitor/core';

/** Web/PWA — prekey upload deferred until native or WASM bridge (8.4+). */
export class SscLibsignalWeb extends WebPlugin {
  async getPinnedVersion() {
    return { version: '0.96.2', source: 'web-unavailable' };
  }

  async generatePreKeyBundle() {
    throw new Error('Signal prekeys require the SSC Android app');
  }

  async hasSession() {
    return { has_session: false, skipped: true, reason: 'web' };
  }

  async establishSession() {
    throw new Error('Signal sessions require the SSC Android app');
  }

  async encryptSignalMessage() {
    throw new Error('Signal encrypt requires the SSC Android app');
  }

  async decryptSignalMessage() {
    throw new Error('Signal decrypt requires the SSC Android app');
  }
}