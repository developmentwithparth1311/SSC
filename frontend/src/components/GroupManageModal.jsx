import React, { useEffect, useMemo, useState } from 'react';
import { toast } from 'sonner';
import { X, UsersThree, MagnifyingGlass, SignOut } from '@phosphor-icons/react';
import { api } from '../lib/api';
import { useLocale } from '../context/LocaleContext';
import { getLocalGroupLabel, setLocalGroupLabel } from '../lib/groupLabels';
import Avatar from './Avatar';

export default function GroupManageModal({
  open,
  onClose,
  conversation,
  myUserId,
  contacts = [],
  onUpdated,
  onLeave,
}) {
  const { t } = useLocale();
  const [groupName, setGroupName] = useState('');
  const [q, setQ] = useState('');
  const [busy, setBusy] = useState(false);

  const isAdmin = conversation?.admin_id === myUserId;
  const members = conversation?.members || [];
  const memberIds = useMemo(
    () => new Set([myUserId, ...members.map((m) => m.user_id)]),
    [members, myUserId],
  );

  useEffect(() => {
    if (!open || !conversation) return;
    setGroupName(getLocalGroupLabel(conversation.conversation_id));
    setQ('');
  }, [open, conversation?.conversation_id]);

  const addable = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return contacts
      .filter((c) => !c.blocked && !memberIds.has(c.user_id))
      .filter((c) => !needle || c.username.toLowerCase().includes(needle))
      .sort((a, b) => a.username.localeCompare(b.username));
  }, [contacts, memberIds, q]);

  const saveName = () => {
    if (!conversation) return;
    const trimmed = groupName.trim();
    if (trimmed) setLocalGroupLabel(conversation.conversation_id, trimmed);
    toast.success(t('groupNameSaved'));
    onUpdated?.();
  };

  const addMember = async (username) => {
    if (!conversation || busy) return;
    setBusy(true);
    try {
      const { data } = await api.post(`/conversations/${conversation.conversation_id}/members`, {
        peer_usernames: [username],
      });
      toast.success(t('groupMemberAdded'));
      onUpdated?.(data);
    } catch (e) {
      toast.error(e?.response?.data?.detail || t('groupMemberAddFailed'));
    } finally {
      setBusy(false);
    }
  };

  const removeMember = async (userId) => {
    if (!conversation || busy) return;
    const isSelf = userId === myUserId;
    if (!window.confirm(isSelf ? t('groupLeaveConfirm') : t('groupRemoveMemberConfirm'))) return;
    setBusy(true);
    try {
      await api.delete(`/conversations/${conversation.conversation_id}/members/${userId}`);
      toast.success(isSelf ? t('leftGroup') : t('groupMemberRemoved'));
      if (isSelf) {
        onLeave?.();
        onClose?.();
      } else {
        onUpdated?.();
      }
    } catch (e) {
      toast.error(e?.response?.data?.detail || t('groupMemberRemoveFailed'));
    } finally {
      setBusy(false);
    }
  };

  if (!open || !conversation) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-xl flex items-start justify-center pt-16 px-4" onClick={onClose}>
      <div className="w-full max-w-md bg-[#121212] tac-border rounded-md p-4 fade-up max-h-[85vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <UsersThree size={18} className="text-[#00E5FF]" weight="duotone" />
            <h3 className="font-mono text-xs tracking-[0.25em]">{t('groupManageTitle')}</h3>
          </div>
          <button type="button" onClick={onClose} className="text-[#A1A1AA] hover:text-white" data-testid="group-manage-close">
            <X size={16} />
          </button>
        </div>

        <p className="text-[10px] font-mono text-[#71717A] mb-3">{t('groupPrivacyHint')}</p>

        <label className="text-[10px] font-mono uppercase tracking-wider text-[#A1A1AA] block mb-1">{t('groupRenameLabel')}</label>
        <div className="flex gap-2 mb-4">
          <input
            value={groupName}
            onChange={(e) => setGroupName(e.target.value)}
            placeholder={t('groupNamePlaceholder')}
            className="flex-1 h-10 px-3 text-sm rounded-md bg-[#1A1A1A] tac-border"
            maxLength={64}
            data-testid="group-manage-name"
          />
          <button
            type="button"
            onClick={saveName}
            className="px-3 text-xs font-mono tac-border rounded-md hover:bg-[#1A1A1A]"
            data-testid="group-manage-save-name"
          >
            {t('saveLabel')}
          </button>
        </div>

        <p className="text-[10px] font-mono uppercase tracking-wider text-[#A1A1AA] mb-2">{t('groupMembersTitle')}</p>
        <ul className="space-y-1 mb-4">
          {members.map((m) => (
            <li key={m.user_id} className="flex items-center justify-between gap-2 px-2 py-2 rounded-md bg-[#1A1A1A]">
              <div className="flex items-center gap-2 min-w-0">
                <Avatar user={m} size="sm" />
                <span className="text-sm truncate">@{m.username}</span>
                {conversation.admin_id === m.user_id && (
                  <span className="text-[9px] font-mono text-[#00E5FF]">{t('groupAdminBadge')}</span>
                )}
              </div>
              {(isAdmin && m.user_id !== myUserId) || m.user_id === myUserId ? (
                <button
                  type="button"
                  disabled={busy}
                  onClick={() => removeMember(m.user_id)}
                  className="text-[10px] font-mono text-[#FF453A] hover:underline shrink-0"
                  data-testid={`group-remove-${m.user_id}`}
                >
                  {m.user_id === myUserId ? t('leaveGroup') : t('groupRemoveMember')}
                </button>
              ) : null}
            </li>
          ))}
        </ul>

        {isAdmin && (
          <>
            <p className="text-[10px] font-mono uppercase tracking-wider text-[#A1A1AA] mb-2">{t('groupAddMembersTitle')}</p>
            <div className="flex items-center gap-2 bg-[#1A1A1A] rounded-md px-3 py-2 tac-border mb-2">
              <MagnifyingGlass size={14} className="text-[#A1A1AA]" />
              <input
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder={t('groupSearchPlaceholder')}
                className="bg-transparent flex-1 outline-none border-0 text-sm"
                data-testid="group-manage-search"
              />
            </div>
            <div className="max-h-40 overflow-y-auto mb-2">
              {addable.length === 0 ? (
                <p className="text-[11px] font-mono text-[#71717A] py-3 text-center">{t('groupNoAddableContacts')}</p>
              ) : (
                addable.map((c) => (
                  <button
                    key={c.user_id}
                    type="button"
                    disabled={busy}
                    onClick={() => addMember(c.username)}
                    className="w-full text-left px-3 py-2 rounded-md hover:bg-[#1A1A1A] text-sm"
                    data-testid={`group-add-${c.username}`}
                  >
                    @{c.username}
                  </button>
                ))
              )}
            </div>
          </>
        )}

        <button
          type="button"
          disabled={busy}
          onClick={() => removeMember(myUserId)}
          className="w-full py-2.5 text-xs font-mono tracking-wider border border-[#FF453A]/40 text-[#FF453A] rounded-md hover:bg-[#FF453A]/10 flex items-center justify-center gap-2"
          data-testid="group-manage-leave"
        >
          <SignOut size={14} /> {t('leaveGroup')}
        </button>
      </div>
    </div>
  );
}