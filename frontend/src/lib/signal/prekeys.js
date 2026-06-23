import { api } from '../api';
import { LIBSIGNAL_PINNED_VERSION } from './constants';
import { generatePreKeyBundle, isNativeLibsignalAvailable } from './nativeLibsignal';

let uploadPromise = null;

export async function uploadPreKeyBundle(bundle) {
  const payload = {
    registration_id: bundle.registration_id,
    device_id: bundle.device_id || 1,
    identity_key_public: bundle.identity_key_public,
    signed_prekey_id: bundle.signed_prekey_id,
    signed_prekey_public: bundle.signed_prekey_public,
    signed_prekey_signature: bundle.signed_prekey_signature,
    kyber_prekey_id: bundle.kyber_prekey_id,
    kyber_prekey_public: bundle.kyber_prekey_public,
    kyber_prekey_signature: bundle.kyber_prekey_signature,
    one_time_prekeys: bundle.one_time_prekeys,
    libsignal_version: bundle.libsignal_version || LIBSIGNAL_PINNED_VERSION,
  };
  const { data } = await api.put('/keys/prekey-bundle', payload);
  return data;
}

export async function fetchMyPreKeyStatus() {
  const { data } = await api.get('/keys/prekey-bundle/me');
  return data;
}

export async function ensurePreKeysUploaded() {
  if (!isNativeLibsignalAvailable()) {
    return { skipped: true, reason: 'web' };
  }
  if (uploadPromise) return uploadPromise;

  uploadPromise = (async () => {
    try {
      const status = await fetchMyPreKeyStatus();
      if (status?.ready) {
        return { uploaded: false, already: true };
      }
      const bundle = await generatePreKeyBundle();
      const result = await uploadPreKeyBundle(bundle);
      return { uploaded: true, result };
    } finally {
      uploadPromise = null;
    }
  })();

  return uploadPromise;
}