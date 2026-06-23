/** Format last_seen ISO string for display. */
export function formatLastSeen(lastSeen) {
  if (!lastSeen) return 'offline';
  const diff = Date.now() - new Date(lastSeen).getTime();
  if (diff < 0 || Number.isNaN(diff)) return 'offline';
  if (diff < 5 * 60 * 1000) return 'online now';
  if (diff < 60 * 60 * 1000) {
    const m = Math.floor(diff / 60000);
    return `last seen ${m}m ago`;
  }
  if (diff < 24 * 60 * 60 * 1000) {
    const h = Math.floor(diff / 3600000);
    return `last seen ${h}h ago`;
  }
  const d = Math.floor(diff / 86400000);
  return `last seen ${d}d ago`;
}

/** Peer online — prefer server `online` flag (Engine 4); fall back to last_seen. */
export function isPeerOnline(peerOrLastSeen) {
  if (peerOrLastSeen && typeof peerOrLastSeen === 'object') {
    if (peerOrLastSeen.online === true) return true;
    if (peerOrLastSeen.online === false) return false;
    return isOnline(peerOrLastSeen.last_seen);
  }
  return isOnline(peerOrLastSeen);
}

export function isOnline(lastSeen) {
  if (!lastSeen) return false;
  return Date.now() - new Date(lastSeen).getTime() < 5 * 60 * 1000;
}

export function formatPeerPresence(peer) {
  if (!peer) return 'offline';
  if (isPeerOnline(peer)) return 'online now';
  return formatLastSeen(peer.last_seen);
}