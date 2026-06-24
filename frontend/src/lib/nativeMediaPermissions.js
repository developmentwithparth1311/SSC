import { registerPlugin } from '@capacitor/core';

const SscMediaPermissions = registerPlugin('SscMediaPermissions', {
  web: () => import('./nativeMediaPermissionsWeb').then((m) => new m.SscMediaPermissionsWeb()),
});

export async function checkNativeMediaPermissions() {
  return SscMediaPermissions.checkPermissions();
}

export async function requestNativeMediaPermissions({ audio = true, video = false } = {}) {
  return SscMediaPermissions.requestPermissions({ audio, video });
}

export async function openNativeAppSettings() {
  return SscMediaPermissions.openAppSettings();
}