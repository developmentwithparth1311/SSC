import React, { useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { toast } from 'sonner';
import { useAuth } from '../context/AuthContext';
import { getPendingInvite } from '../lib/invites';
import { completeGoogleAuth } from '../lib/google-auth';

/** Handles OAuth redirect: /auth/google?token=...&needs_setup=0|1 */
export default function GoogleAuthCallback() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const { loginWithToken } = useAuth();
  const done = useRef(false);

  useEffect(() => {
    if (done.current) return;
    done.current = true;

    const token = params.get('token');
    const needsSetup = params.get('needs_setup') === '1';

    if (!token) {
      toast.error('Google sign-in failed — no token');
      navigate('/login');
      return;
    }

    (async () => {
      try {
        localStorage.setItem('ssc_token', token);
        const { api } = await import('../lib/api');
        const { data: user } = await api.get('/auth/me');
        await completeGoogleAuth(
          { token, user, needs_username: needsSetup },
          { loginWithToken, navigate, getPendingInvite },
        );
        toast.success('Signed in with Google');
      } catch {
        toast.error('Google sign-in failed');
        navigate('/login');
      }
    })();
  }, [loginWithToken, navigate, params]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0A0A0A] text-[#A1A1AA] font-mono text-xs tracking-[0.25em]">
      <div className="flex items-center gap-3">
        <span className="w-1.5 h-1.5 rounded-full bg-[#00E5FF] pulse-glow" />
        COMPLETING GOOGLE SIGN-IN…
      </div>
    </div>
  );
}