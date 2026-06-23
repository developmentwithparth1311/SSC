import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { api } from '../lib/api';
import { useAuth } from '../context/AuthContext';

export default function AuthCallback() {
  const navigate = useNavigate();
  const { setUser, loginWithToken } = useAuth();
  const hasProcessed = useRef(false);
  const [msg, setMsg] = useState('ESTABLISHING SECURE SESSION…');

  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const hash = window.location.hash || '';
    const match = hash.match(/session_id=([^&]+)/);
    if (!match) {
      navigate('/login');
      return;
    }
    const session_id = match[1];

    (async () => {
      try {
        const { data } = await api.post('/auth/google/session', { session_id });
        await loginWithToken(data.token, data.user);
        // clean URL
        window.history.replaceState(null, '', '/chat');
        if (data.needs_username) {
          setMsg('PICKING SECURE HANDLE…');
          navigate('/setup', { state: { user: data.user } });
        } else {
          // need to ensure encryption keys exist
          if (!data.user.public_key) {
            navigate('/setup', { state: { user: data.user } });
          } else {
            navigate('/chat', { state: { user: data.user } });
          }
        }
      } catch (e) {
        toast.error('Google sign-in failed');
        navigate('/login');
      }
    })();
  }, [loginWithToken, navigate, setUser]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0A0A0A] text-[#A1A1AA] font-mono text-xs tracking-[0.25em]">
      <div className="flex items-center gap-3">
        <span className="w-1.5 h-1.5 rounded-full bg-[#00E5FF] pulse-glow" />
        {msg}
      </div>
    </div>
  );
}
