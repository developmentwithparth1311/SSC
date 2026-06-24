/**
 * Client session token storage — Engine 5.
 * Web (5.3): HttpOnly cookie only — never localStorage.
 * Native (5.4): in-memory only — never localStorage; re-login after app kill.
 */
import { isInstalledClient } from './platform';

import { LEGACY_JWT_KEY } from './sessionConstants';

let nativeMemoryToken = null;

/** Browser dev shell uses cookie auth; installed clients use in-memory Bearer token. */
export function usesCookieAuth() {
  return !isInstalledClient();
}

/** Purge legacy JWT from localStorage (pre-5.3 web / pre-5.4 native installs). */
export function purgeLegacyJwtFromStorage() {
  if (typeof localStorage === 'undefined') return;
  localStorage.removeItem(LEGACY_JWT_KEY);
}

/** @deprecated Use purgeLegacyJwtFromStorage */
export function purgeLegacyWebJwtFromStorage() {
  purgeLegacyJwtFromStorage();
}

export function persistSessionToken(token) {
  if (!token || usesCookieAuth()) return;
  nativeMemoryToken = token;
}

export function getSessionToken() {
  if (usesCookieAuth()) return null;
  return nativeMemoryToken;
}

export function clearSessionToken() {
  nativeMemoryToken = null;
  purgeLegacyJwtFromStorage();
}

export function hasNativeSessionToken() {
  return !usesCookieAuth() && !!nativeMemoryToken;
}

/** Whether Bearer header is required for API calls on this platform. */
export function usesBearerAuth() {
  return !usesCookieAuth();
}