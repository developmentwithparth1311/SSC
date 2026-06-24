import React, { useEffect, useRef, useState } from 'react';
import { toast } from 'sonner';
import { Phone, VideoCamera, MicrophoneSlash, Microphone, VideoCameraSlash } from '@phosphor-icons/react';
import { useLocale } from '../context/LocaleContext';
import { getBackendUrl } from '../lib/platform';
import { sendSignaling, unpackIncomingSignaling } from '../lib/signal/webrtcSignaling';
import {
  acquireLocalMediaStream,
  bindLocalPreview,
  bindRemoteStream,
} from '../lib/callMedia';
import Avatar from './Avatar';

/**
 * CallModal handles WebRTC voice/video calls.
 * Props:
 *  - mode: 'video' | 'audio'
 *  - direction: 'outgoing' | 'incoming'
 *  - peer: { user_id, username }
 *  - socket: ChatSocket instance
 *  - signal: incoming signaling payload (offer or null)
 *  - onClose: () => void
 */
const DEFAULT_ICE = [
  { urls: 'stun:stun.l.google.com:19302' },
  { urls: 'stun:stun1.l.google.com:19302' },
  { urls: 'stun:stun2.l.google.com:19302' },
];

async function getRTCConfig() {
  try {
    const base = getBackendUrl();
    const res = await fetch(`${base}/api/config`);
    const cfg = await res.json();
    if (Array.isArray(cfg.ice_servers) && cfg.ice_servers.length) {
      return { iceServers: cfg.ice_servers, iceCandidatePoolSize: 10 };
    }
  } catch {}
  return { iceServers: DEFAULT_ICE, iceCandidatePoolSize: 10 };
}

export default function CallModal({ mode, direction, peer, user, socket, signal, onClose }) {
  const { t } = useLocale();
  const pcRef = useRef(null);
  const localStreamRef = useRef(null);
  const localVideoRef = useRef(null);
  const remoteVideoRef = useRef(null);
  const remoteAudioRef = useRef(null);
  const [status, setStatus] = useState(direction === 'outgoing' ? 'calling' : 'ringing');
  const [muted, setMuted] = useState(false);
  const [videoOff, setVideoOff] = useState(false);
  const [duration, setDuration] = useState(0);
  const startedAtRef = useRef(null);

  useEffect(() => {
    setupCall();
    return () => cleanup();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (status !== 'connected') return;
    startedAtRef.current = Date.now();
    const timer = setInterval(
      () => setDuration(Math.floor((Date.now() - startedAtRef.current) / 1000)),
      500,
    );
    return () => clearInterval(timer);
  }, [status]);

  const setupCall = async () => {
    const rtcConfig = await getRTCConfig();
    const pc = new RTCPeerConnection(rtcConfig);
    pcRef.current = pc;

    const signalingCtx = { peerUserId: peer.user_id, ourUserId: user?.user_id, peer, user, isGroup: false };

    pc.onicecandidate = (e) => {
      if (e.candidate) {
        sendSignaling(socket, { type: 'ice-candidate', to: peer.user_id, candidate: e.candidate }, signalingCtx);
      }
    };
    pc.ontrack = (e) => {
      bindRemoteStream({
        videoEl: mode === 'video' ? remoteVideoRef.current : null,
        audioEl: remoteAudioRef.current,
        stream: e.streams[0],
      });
    };
    pc.onconnectionstatechange = () => {
      if (pc.connectionState === 'connected') setStatus('connected');
      if (['disconnected', 'failed', 'closed'].includes(pc.connectionState)) onClose && onClose();
    };

    try {
      const stream = await acquireLocalMediaStream(mode);
      localStreamRef.current = stream;
      bindLocalPreview(localVideoRef.current, stream);
      stream.getTracks().forEach((track) => pc.addTrack(track, stream));
    } catch (e) {
      toast.error(t('callMediaError'));
      onClose && onClose();
      return;
    }

    if (direction === 'outgoing') {
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      await sendSignaling(socket, { type: 'call-offer', to: peer.user_id, mode, sdp: offer }, signalingCtx);
    } else if (signal?.sdp) {
      await pc.setRemoteDescription(new RTCSessionDescription(signal.sdp));
      const answer = await pc.createAnswer();
      await pc.setLocalDescription(answer);
      await sendSignaling(socket, { type: 'call-answer', to: peer.user_id, sdp: answer }, signalingCtx);
      setStatus('connected');
    }
  };

  // listen for signaling pushed by parent (via window event hack)
  useEffect(() => {
    const handler = async (e) => {
      let data = e.detail;
      const pc = pcRef.current;
      if (!pc) return;
      try {
        data = await unpackIncomingSignaling(data, {
          myUserId: user?.user_id,
          peerUserId: peer.user_id,
        });
      } catch {
        return;
      }
      if (data.type === 'call-answer' && data.from === peer.user_id) {
        await pc.setRemoteDescription(new RTCSessionDescription(data.sdp));
        setStatus('connected');
      } else if (data.type === 'ice-candidate' && data.from === peer.user_id) {
        try { await pc.addIceCandidate(new RTCIceCandidate(data.candidate)); } catch {}
      } else if (data.type === 'call-end' && data.from === peer.user_id) {
        onClose && onClose();
      } else if (data.type === 'call-reject' && data.from === peer.user_id) {
        onClose && onClose();
      }
    };
    window.addEventListener('ssc-signal', handler);
    return () => window.removeEventListener('ssc-signal', handler);
  }, [peer.user_id, user?.user_id, onClose]);

  const cleanup = () => {
    try { pcRef.current?.close(); } catch {}
    try { localStreamRef.current?.getTracks().forEach((track) => track.stop()); } catch {}
    if (remoteAudioRef.current) remoteAudioRef.current.srcObject = null;
    if (remoteVideoRef.current) remoteVideoRef.current.srcObject = null;
  };

  const endCall = () => {
    socket.send({ type: 'call-end', to: peer.user_id });
    onClose && onClose();
  };

  const toggleMute = () => {
    const track = localStreamRef.current?.getAudioTracks?.()[0];
    if (track) { track.enabled = !track.enabled; setMuted(!track.enabled); }
  };
  const toggleVideo = () => {
    const track = localStreamRef.current?.getVideoTracks?.()[0];
    if (track) { track.enabled = !track.enabled; setVideoOff(!track.enabled); }
  };

  const fmt = (s) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;

  return (
    <div className="fixed inset-0 z-[9998] bg-black/90 backdrop-blur-xl flex flex-col items-center justify-center safe-top safe-bottom">
      <audio ref={remoteAudioRef} autoPlay playsInline className="sr-only" data-testid="call-remote-audio" />
      <div className="relative w-full max-w-3xl aspect-video bg-[#121212] rounded-md tac-border overflow-hidden">
        {mode === 'video' ? (
          <video ref={remoteVideoRef} autoPlay playsInline muted className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center">
            <div className="mb-4">
              <Avatar user={peer} size="lg" className="!w-32 !h-32 !text-3xl !rounded-md" />
            </div>
            <div className="font-mono text-lg">@{peer.username}</div>
          </div>
        )}
        {mode === 'video' && (
          <video ref={localVideoRef} autoPlay muted playsInline className="absolute top-3 right-3 w-32 h-24 object-cover rounded-md tac-border" />
        )}
        <div className="absolute top-3 left-3 px-2 py-1 bg-black/60 rounded font-mono text-[10px] tracking-widest text-[#A1A1AA]">
          {status === 'connected' ? `E2E · ${fmt(duration)}` : status.toUpperCase()}
        </div>
      </div>
      <div className="mt-6 flex items-center gap-3">
        <button onClick={toggleMute} data-testid="call-mute-button" className={`w-12 h-12 rounded-full flex items-center justify-center ${muted ? 'bg-[#FF3B30]' : 'bg-[#1A1A1A] tac-border'} hover:brightness-110`}>
          {muted ? <MicrophoneSlash size={20} /> : <Microphone size={20} />}
        </button>
        {mode === 'video' && (
          <button onClick={toggleVideo} data-testid="call-video-button" className={`w-12 h-12 rounded-full flex items-center justify-center ${videoOff ? 'bg-[#FF3B30]' : 'bg-[#1A1A1A] tac-border'} hover:brightness-110`}>
            {videoOff ? <VideoCameraSlash size={20} /> : <VideoCamera size={20} />}
          </button>
        )}
        <button onClick={endCall} data-testid="call-end-button" className="w-14 h-14 rounded-full bg-[#FF3B30] flex items-center justify-center hover:brightness-110">
          <Phone size={22} weight="fill" className="rotate-[135deg] text-white" />
        </button>
      </div>
    </div>
  );
}