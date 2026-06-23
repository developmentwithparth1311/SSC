import { Capacitor, registerPlugin } from '@capacitor/core';

const SscTranslate = registerPlugin('SscTranslate', {
  web: () => import('./nativeTranslateWeb').then((m) => new m.SscTranslateWeb()),
});

export function isOnDeviceTranslationAvailable() {
  return Capacitor.isNativePlatform();
}

export async function getTranslationCapabilities() {
  if (!isOnDeviceTranslationAvailable()) {
    return { on_device: false, provider: 'web-unavailable' };
  }
  return SscTranslate.getCapabilities();
}

export async function translateOnDevice(text, sourceLanguage, targetLanguage) {
  if (!isOnDeviceTranslationAvailable()) {
    throw new Error('ON_DEVICE_UNAVAILABLE');
  }
  return SscTranslate.translate({
    text,
    source_language: sourceLanguage || undefined,
    target_language: targetLanguage,
  });
}