import { WebPlugin } from '@capacitor/core';

/** Web/PWA — on-device translation not available; use server only in dev if enabled. */
export class SscTranslateWeb extends WebPlugin {
  async getCapabilities() {
    return { on_device: false, provider: 'web-unavailable', requires_model_download: false };
  }

  async translate() {
    throw new Error('On-device translation requires the SSC Android app');
  }
}