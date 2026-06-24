import { WebPlugin } from '@capacitor/core';

/** Browser / desktop dev shell — permissions come from getUserMedia prompts. */
export class SscMediaPermissionsWeb extends WebPlugin {
  async checkPermissions() {
    return { microphone: 'prompt', camera: 'prompt' };
  }

  async requestPermissions() {
    return { microphone: 'prompt', camera: 'prompt' };
  }

  async openAppSettings() {
    // No-op on web
  }
}