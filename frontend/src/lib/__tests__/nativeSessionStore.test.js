import { webcrypto } from 'crypto';
import { TextEncoder, TextDecoder } from 'util';
import {
  persistNativeSession,
  restoreNativeSession,
  clearNativeSession,
  NATIVE_SESSION_WRAP_KEY,
} from '../nativeSessionStore';

jest.mock('../platform', () => ({
  isInstalledClient: () => true,
}));

beforeAll(() => {
  global.crypto = webcrypto;
  global.TextEncoder = TextEncoder;
  global.TextDecoder = TextDecoder;
});

describe('nativeSessionStore', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('persists and restores JWT without plaintext in localStorage', async () => {
    const jwt = 'eyJhbGciOiJIUzI1NiJ9.test.signature';
    await persistNativeSession(jwt);
    expect(localStorage.getItem(NATIVE_SESSION_WRAP_KEY)).toBeTruthy();
    expect(localStorage.getItem(NATIVE_SESSION_WRAP_KEY)).not.toContain(jwt);
    expect(localStorage.getItem('ssc_token')).toBeNull();
    expect(await restoreNativeSession()).toBe(jwt);
  });

  it('clears wrapped session', async () => {
    await persistNativeSession('token-abc');
    clearNativeSession();
    expect(localStorage.getItem(NATIVE_SESSION_WRAP_KEY)).toBeNull();
    expect(await restoreNativeSession()).toBeNull();
  });
});