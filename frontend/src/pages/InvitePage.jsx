import React, { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { toast } from 'sonner';
import { LockKey, UserPlus } from '@phosphor-icons/react';
import { api } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { useLocale } from '../context/LocaleContext';
import { getStoredUiLang, t as translate } from '../lib/i18n';
import { savePendingInvite, clearPendingInvite } from '../lib/invites';

export default function InvitePage() {
  const { token } = useParams();
  const navigate = useNavigate();
  const { user, loading } = useAuth();
  const { t } = useLocale();
  const [preview, setPreview] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) return;
    (async () => {
      try {
        const { data } = await api.get(`/invites/${token}/preview`);
        setPreview(data);
      } catch (e) {
        setError(e?.response?.data?.detail || translate('invalidInvite', getStoredUiLang()));
      }
    })();
  }, [token]);

  useEffect(() => {
    if (loading || !token) return;
    if (user && (!user.username || !user.public_key)) {
      savePendingInvite(token);
      navigate('/setup', { replace: true });
    }
  }, [loading, user, token, navigate]);

  useEffect(() => {
    if (loading || error || !token || !user?.username || !user?.public_key) return;
    (async () => {
      setBusy(true);
      try {
        await api.post(`/invites/use/${token}`);
        clearPendingInvite();
        toast.success(t('inviteFriendPending', { user: preview?.from_username || 'user' }));
        navigate('/chat', { replace: true });
      } catch (e) {
        toast.error(e?.response?.data?.detail || t('couldNotUseInvite'));
        navigate('/chat', { replace: true });
      } finally {
        setBusy(false);
      }
    })();
  }, [loading, user, token, error, preview, navigate, t]);

  if (loading || (user?.username && user?.public_key && !error)) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0A0A0A] text-[#A1A1AA] font-mono text-xs">
        {busy ? t('inviteProcessing') : t('loading')}
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#0A0A0A] p-6">
        <div className="w-full max-w-sm text-center fade-up">
          <div className="w-12 h-12 rounded-md bg-[#FF3B30]/20 mx-auto flex items-center justify-center mb-4">
            <LockKey size={22} className="text-[#FF3B30]" />
          </div>
          <h1 className="font-mono text-sm tracking-[0.2em]">{t('inviteUnavailable')}</h1>
          <p className="text-sm text-[#A1A1AA] mt-3">{error}</p>
          <Link to="/" className="inline-block mt-6 text-xs font-mono text-[#00E5FF] hover:underline">{t('inviteBack')}</Link>
        </div>
      </div>
    );
  }

  const saveAndGo = (path) => {
    savePendingInvite(token);
    navigate(path);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0A0A0A] p-6">
      <div className="w-full max-w-sm bg-[#121212] tac-border rounded-md p-6 fade-up text-center">
        <div className="w-14 h-14 rounded-md bg-[#00E5FF]/15 mx-auto flex items-center justify-center mb-4">
          <UserPlus size={28} className="text-[#00E5FF]" weight="duotone" />
        </div>
        <h1 className="font-mono text-sm tracking-[0.2em]">{t('inviteLink')}</h1>
        <p className="text-sm text-[#A1A1AA] mt-3">
          {t('inviteFrom', { user: preview?.from_username || '…' })}
        </p>
        <p className="text-[10px] font-mono text-[#A1A1AA] mt-2 tracking-wider">
          {t('inviteMutualRequired')}
        </p>
        <div className="mt-6 flex flex-col gap-2">
          <button onClick={() => saveAndGo('/register')} data-testid="invite-register"
            className="w-full py-2.5 bg-[#00E5FF] text-black font-medium text-sm rounded-md hover:brightness-110">
            {t('inviteCreateAccount')}
          </button>
          <button onClick={() => saveAndGo('/login')} data-testid="invite-login"
            className="w-full py-2.5 tac-border rounded-md text-sm hover:bg-[#1A1A1A]">
            {t('inviteLogIn')}
          </button>
        </div>
      </div>
    </div>
  );
}