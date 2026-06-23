import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { api } from '../lib/api';
import { unwrapPrivateKey } from '../lib/crypto';
import { unsubscribePush } from '../lib/push';
import { unsubscribeNativePush } from '../lib/native-push';

const AuthCtx = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [privateKey, setPrivateKey] = useState(null);

  const refreshUser = useCallback(async () => {
    try {
      const { data } = await api.get('/auth/me');
      setUser(data);
      return data;
    } catch {
      setUser(null);
      return null;
    }
  }, []);

  const restorePrivateKeyFromSession = useCallback(async () => {
    if (privateKey || sessionStorage.getItem('ssc_pk_unlocked') !== '1') return;
    const raw = sessionStorage.getItem('ssc_pk_jwk');
    if (!raw) return;
    try {
      const jwk = JSON.parse(raw);
      const pk = await crypto.subtle.importKey(
        'jwk', jwk, { name: 'RSA-OAEP', hash: 'SHA-256' }, true, ['decrypt'],
      );
      setPrivateKey(pk);
    } catch {
      sessionStorage.removeItem('ssc_pk_jwk');
      sessionStorage.removeItem('ssc_pk_unlocked');
    }
  }, [privateKey]);

  useEffect(() => {
    // Note: Emergent OAuth removed. This was for platform-specific flow.
    // AuthCallback handles session exchange first.
    if (typeof window !== 'undefined' && window.location.hash?.includes('session_id=')) {
      setLoading(false);
      return;
    }
    refreshUser()
      .then((u) => { if (u) return restorePrivateKeyFromSession(); })
      .finally(() => setLoading(false));
  }, [refreshUser, restorePrivateKeyFromSession]);

  const loginWithToken = async (token, userObj) => {
    localStorage.setItem('ssc_token', token);
    setUser(userObj);
  };

  const persistPrivateKey = async (pk) => {
    setPrivateKey(pk);
    try {
      const jwk = await crypto.subtle.exportKey('jwk', pk);
      sessionStorage.setItem('ssc_pk_jwk', JSON.stringify(jwk));
      sessionStorage.setItem('ssc_pk_unlocked', '1');
    } catch {
      sessionStorage.removeItem('ssc_pk_jwk');
      sessionStorage.removeItem('ssc_pk_unlocked');
    }
    return pk;
  };

  const unlockPrivateKey = async (password) => {
    if (!user?.encrypted_private_key || !user?.pk_salt) {
      throw new Error('No encryption key on this account');
    }
    if (!crypto?.subtle) {
      throw new Error('WebCrypto unavailable on this device');
    }
    const pk = await unwrapPrivateKey(user.encrypted_private_key, user.pk_salt, password);
    return persistPrivateKey(pk);
  };

  const setPK = (pk) => setPrivateKey(pk);

  const logout = async () => {
    try { await unsubscribePush(); } catch {}
    try {
      const nativeToken = localStorage.getItem('ssc_native_push_token');
      await unsubscribeNativePush(nativeToken);
    } catch {}
    try { await api.post('/auth/logout'); } catch {}
    localStorage.removeItem('ssc_token');
    localStorage.removeItem('ssc_native_push_token');
    sessionStorage.removeItem('ssc_pk_jwk');
    sessionStorage.removeItem('ssc_pk_unlocked');
    sessionStorage.clear();
    setUser(null);
    setPrivateKey(null);
  };

  const panicWipe = async () => {
    try { await api.post('/panic-wipe'); } catch {}
    localStorage.removeItem('ssc_token');
    localStorage.removeItem('ssc_native_push_token');
    sessionStorage.clear();
    window.location.href = '/login?panic=1';
  };

  return (
    <AuthCtx.Provider value={{ user, setUser, privateKey, setPK, loading, refreshUser, loginWithToken, unlockPrivateKey, persistPrivateKey, logout, panicWipe }}>
      {children}
    </AuthCtx.Provider>
  );
}

export const useAuth = () => useContext(AuthCtx);
