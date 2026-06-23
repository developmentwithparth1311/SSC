import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Phone, VideoCamera, MicrophoneSlash, Microphone, VideoCameraSlash, X } from '@phosphor-icons/react';
import { sendSignaling, unpackIncomingSignaling } from '../lib/signal/webrtcSignaling';

/**
 * GroupCallModal — full-mesh WebRTC for up to ~6 participants in a group.
 * Each connected peer is a separate RTCPeerConnection.
 *
 * Signaling: relayed via existing WebSocket "call-offer/answer/ice-candidate/call-end".
 * To start, we send a "call-initiate" to all other members. They open the same modal
 * in "incoming" mode, accept, and the offers flow naturally.
 */
const DEFAULT_ICE = [
  { urls: 'stun:stun.l.google.com:19302' },
  { urls: 'stun:stun1.l.google.com:19302' },
  { urls: 'stun:stun2.l.google.com:19302' },
];

async function getRTCConfig() {
  try {
    const { getBackendUrl } = await import('../lib/platform');
    const base = getBackendUrl();
    const res = await fetch(`${base}/api/config`);
    const cfg = await res.json();
    if (Array.isArray(cfg.ice_servers) && cfg.ice_servers.length) {
      return { iceServers: cfg.ice_servers, iceCandidatePoolSize: 10 };
    }
  } catch {}
  return { iceServers: DEFAULT_ICE, iceCandidatePoolSize: 10 };
}

export default function GroupCallModal({
  mode, direction, members, me, user, conversationId, socket, signal, onClose,
}) {
  // members: [{user_id, username}] EXCLUDING me
  const [peers, setPeers] = useState({}); // user_id -> { pc, stream, username }
  const peersRef = useRef({});
  const localStreamRef = useRef(null);
  const localVideoRef = useRef(null);
  const [muted, setMuted] = useState(false);
  const [videoOff, setVideoOff] = useState(false);
  const [duration, setDuration] = useState(0);
  const startRef = useRef(null);
  const [status, setStatus] = useState(direction === 'outgoing' ? 'calling' : 'incoming');

  const signalingCtx = useMemo(() => ({
    ourUserId: me?.user_id,
    user,
    isGroup: true,
    members: [...(members || []), me].filter(Boolean),
    conversationId,
  }), [me, user, members, conversationId]);

  const relaySignaling = async (msg) => {
    if (!socket) return;
    await sendSignaling(socket, { ...msg, group: true }, signalingCtx);
  };

  useEffect(() => {
    setup();
    return () => cleanup();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    startRef.current = Date.now();
    const t = setInterval(() => setDuration(Math.floor((Date.now() - startRef.current) / 1000)), 1000);
    return () => clearInterval(t);
  }, []);

  const createPeerConnection = async (peerId, peerUsername) => {
    const rtcConfig = await getRTCConfig();
    const pc = new RTCPeerConnection(rtcConfig);
    pc.onicecandidate = (e) => {
      if (e.candidate) relaySignaling({ type: 'ice-candidate', to: peerId, candidate: e.candidate });
    };
    pc.ontrack = (e) => {
      setPeers((cur) => ({ ...cur, [peerId]: { ...(cur[peerId] || {}), stream: e.streams[0], username: peerUsername } }));
    };
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach((t) => pc.addTrack(t, localStreamRef.current));
    }
    peersRef.current[peerId] = { pc, username: peerUsername };
    return pc;
  };

  const setup = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true, video: mode === 'video' ? { width: 480, height: 360 } : false,
      });
      localStreamRef.current = stream;
      if (localVideoRef.current) localVideoRef.current.srcObject = stream;
    } catch (e) {
      alert('Cannot access camera/microphone: ' + e.message);
      onClose && onClose();
      return;
    }

    if (direction === 'outgoing') {
      // create offer for each member
      for (const m of members) {
        const pc = await createPeerConnection(m.user_id, m.username);
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);
        await relaySignaling({
          type: 'call-offer', to: m.user_id, mode, sdp: offer,
          members: members.map((mm) => ({ user_id: mm.user_id, username: mm.username })),
        });
      }
      setStatus('connected');
    } else if (direction === 'incoming' && signal?.from && signal?.sdp) {
      // accept the initial offer
      const pc = await createPeerConnection(signal.from, signal.from_username || 'peer');
      await pc.setRemoteDescription(new RTCSessionDescription(signal.sdp));
      const answer = await pc.createAnswer();
      await pc.setLocalDescription(answer);
      await relaySignaling({ type: 'call-answer', to: signal.from, sdp: answer });
      // ALSO initiate offers to all other members (full mesh)
      for (const m of (signal.members || [])) {
        if (m.user_id === me.user_id || m.user_id === signal.from || peersRef.current[m.user_id]) continue;
        const pc2 = await createPeerConnection(m.user_id, m.username);
        const offer = await pc2.createOffer();
        await pc2.setLocalDescription(offer);
        await relaySignaling({ type: 'call-offer', to: m.user_id, mode, sdp: offer });
      }
      setStatus('connected');
    }
  };

  // listen for signaling
  useEffect(() => {
    const handler = async (e) => {
      let data = e.detail;
      if (!data?.group) return;
      try {
        data = await unpackIncomingSignaling(data, {
          myUserId: me?.user_id,
          peerUserId: data.from,
        });
      } catch {
        return;
      }
      const fromId = data.from;
      if (data.type === 'call-offer' && fromId !== me.user_id) {
        let entry = peersRef.current[fromId];
        if (!entry) {
          const pc = await createPeerConnection(fromId, data.from_username || 'peer');
          entry = peersRef.current[fromId];
        }
        await entry.pc.setRemoteDescription(new RTCSessionDescription(data.sdp));
        const answer = await entry.pc.createAnswer();
        await entry.pc.setLocalDescription(answer);
        await relaySignaling({ type: 'call-answer', to: fromId, sdp: answer });
      } else if (data.type === 'call-answer') {
        const entry = peersRef.current[fromId];
        if (entry) {
          try { await entry.pc.setRemoteDescription(new RTCSessionDescription(data.sdp)); } catch {}
        }
      } else if (data.type === 'ice-candidate') {
        const entry = peersRef.current[fromId];
        if (entry) {
          try { await entry.pc.addIceCandidate(new RTCIceCandidate(data.candidate)); } catch {}
        }
      } else if (data.type === 'call-end') {
        const entry = peersRef.current[fromId];
        if (entry) { try { entry.pc.close(); } catch {} delete peersRef.current[fromId]; }
        setPeers((cur) => { const n = { ...cur }; delete n[fromId]; return n; });
      }
    };
    window.addEventListener('ssc-signal', handler);
    return () => window.removeEventListener('ssc-signal', handler);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const cleanup = () => {
    Object.values(peersRef.current).forEach((p) => { try { p.pc.close(); } catch {} });
    peersRef.current = {};
    try { localStreamRef.current?.getTracks().forEach((t) => t.stop()); } catch {}
  };

  const end = () => {
    Object.keys(peersRef.current).forEach((uid) => socket.send({ type: 'call-end', to: uid, group: true }));
    onClose && onClose();
  };

  const toggleMute = () => {
    const t = localStreamRef.current?.getAudioTracks?.()[0];
    if (t) { t.enabled = !t.enabled; setMuted(!t.enabled); }
  };
  const toggleVideo = () => {
    const t = localStreamRef.current?.getVideoTracks?.()[0];
    if (t) { t.enabled = !t.enabled; setVideoOff(!t.enabled); }
  };

  const fmt = (s) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
  const tiles = [{ user_id: me.user_id, username: me.username, isLocal: true }, ...Object.entries(peers).map(([uid, p]) => ({ user_id: uid, username: p.username, stream: p.stream }))];
  const cols = tiles.length <= 2 ? 1 : tiles.length <= 4 ? 2 : 3;

  return (
    <div className="fixed inset-0 z-50 bg-black/95 backdrop-blur-xl flex flex-col items-center justify-center p-4">
      <div className="absolute top-3 left-3 px-2 py-1 bg-black/60 rounded font-mono text-[10px] tracking-widest text-[#A1A1AA]">
        GROUP_CALL · E2E · {fmt(duration)} · {tiles.length} ON CALL
      </div>
      <div className="w-full max-w-5xl grid gap-2" style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}>
        {tiles.map((t) => (
          <div key={t.user_id} className="aspect-video bg-[#121212] rounded-md tac-border relative overflow-hidden" data-testid={`group-call-tile-${t.username}`}>
            {mode === 'video' ? (
              t.isLocal ? (
                <video ref={localVideoRef} autoPlay muted playsInline className="w-full h-full object-cover" />
              ) : (
                <video autoPlay playsInline className="w-full h-full object-cover" ref={(el) => { if (el && t.stream) el.srcObject = t.stream; }} />
              )
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <div className="w-16 h-16 rounded-md bg-[#232323] flex items-center justify-center font-mono text-lg">
                  {t.username?.slice(0, 2).toUpperCase()}
                </div>
              </div>
            )}
            <div className="absolute bottom-2 left-2 px-2 py-1 bg-black/60 rounded text-[10px] font-mono tracking-widest">
              @{t.username}{t.isLocal ? ' (YOU)' : ''}
            </div>
          </div>
        ))}
      </div>
      <div className="mt-6 flex items-center gap-3">
        <button onClick={toggleMute} data-testid="group-call-mute" className={`w-12 h-12 rounded-full flex items-center justify-center ${muted ? 'bg-[#FF3B30]' : 'bg-[#1A1A1A] tac-border'} hover:brightness-110`}>
          {muted ? <MicrophoneSlash size={20} /> : <Microphone size={20} />}
        </button>
        {mode === 'video' && (
          <button onClick={toggleVideo} data-testid="group-call-video" className={`w-12 h-12 rounded-full flex items-center justify-center ${videoOff ? 'bg-[#FF3B30]' : 'bg-[#1A1A1A] tac-border'} hover:brightness-110`}>
            {videoOff ? <VideoCameraSlash size={20} /> : <VideoCamera size={20} />}
          </button>
        )}
        <button onClick={end} data-testid="group-call-end" className="w-14 h-14 rounded-full bg-[#FF3B30] flex items-center justify-center hover:brightness-110">
          <Phone size={22} weight="fill" className="rotate-[135deg] text-white" />
        </button>
      </div>
    </div>
  );
}
