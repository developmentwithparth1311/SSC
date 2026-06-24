import { webcrypto } from 'crypto';
import { TextEncoder, TextDecoder } from 'util';
import { persistNativeSession } from '../nativeSessionStore';
import {
  bootstrapSessionFromDevice,
  persistSessionToken,
  getSessionToken,
  clearSessionToken,
  hasNativeSessionToken,
} from '../sessionStore';

jest.mock('../platform', () => ({
  isInstalledClient: () => true,
}));

beforeAll(() => {
  global.crypto = webcrypto;
  global.TextEncoder = TextEncoder;
  global.TextDecoder = TextDecoder;
});

describe('sessionStore', () => {
  beforeEach(() => {
    localStorage.clear();
    clearSessionToken();
  });

  it('bootstraps session from encrypted device store on cold start', async () => {
    await persistNativeSession('jwt-cold-start');
    expect(getSessionToken()).toBeNull();
    const restored = await bootstrapSessionFromDevice();
    expect(restored).toBe('jwt-cold-start');
    expect(getSessionToken()).toBe('jwt-cold-start');
    expect(hasNativeSessionToken()).toBe(true);
  });

  it('clearSessionToken removes memory and device wrap', async () => {
    persistSessionToken('jwt-clear');
    await new Promise((r) => setTimeout(r, 20));
    expect(getSessionToken()).toBe('jwt-clear');
    clearSessionToken();
    expect(getSessionToken()).toBeNull();
    expect(await bootstrapSessionFromDevice()).toBeNull();
  });
});