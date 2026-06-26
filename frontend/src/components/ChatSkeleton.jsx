import React from 'react';

export function ConversationListSkeleton({ rows = 5 }) {
  return (
    <div className="animate-pulse" data-testid="conversations-skeleton">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="px-4 py-3 border-b border-[#27272A] flex items-center gap-3">
          <div className="w-10 h-10 rounded-md bg-[#1A1A1A]" />
          <div className="flex-1 space-y-2">
            <div className="h-3 w-2/5 bg-[#1A1A1A] rounded" />
            <div className="h-2 w-3/5 bg-[#141414] rounded" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function MessagesSkeleton({ rows = 6 }) {
  return (
    <div className="px-3 md:px-6 py-3 flex flex-col gap-4 animate-pulse" data-testid="messages-skeleton">
      {Array.from({ length: rows }).map((_, i) => (
        <div
          key={i}
          className={`h-12 rounded-md bg-[#1A1A1A] ${i % 2 === 0 ? 'w-3/5 self-start' : 'w-2/5 self-end'}`}
        />
      ))}
    </div>
  );
}