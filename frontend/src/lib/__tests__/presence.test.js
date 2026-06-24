import { formatPeerPresence, isPeerOnline } from '../presence';

describe('presence', () => {
  it('treats explicit online flag as authoritative', () => {
    expect(isPeerOnline({ online: true, last_seen: null })).toBe(true);
    expect(isPeerOnline({ online: false, last_seen: new Date().toISOString() })).toBe(false);
  });

  it('formats online peers', () => {
    expect(formatPeerPresence({ online: true })).toBe('online now');
  });

  it('formats offline peers without last_seen', () => {
    expect(formatPeerPresence({ online: false, last_seen: null })).toBe('offline');
  });
});