import { contextBridge, ipcRenderer } from 'electron';

const libsignalMethods = [
  'getPinnedVersion',
  'generatePreKeyBundle',
  'hasSession',
  'establishSession',
  'encryptSignalMessage',
  'decryptSignalMessage',
  'createGroupSenderKeyDistribution',
  'processGroupSenderKeyDistribution',
  'hasGroupSenderKey',
  'encryptGroupMessage',
  'decryptGroupMessage',
];

const libsignal = Object.fromEntries(
  libsignalMethods.map((method) => [
    method,
    (args) => ipcRenderer.invoke('libsignal', { method, args: args || {} }),
  ]),
);

contextBridge.exposeInMainWorld('sscDesktop', {
  isDesktop: true,
  platform: process.platform,
  libsignal,
});