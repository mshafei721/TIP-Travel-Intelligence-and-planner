'use client';

import { ChevronDown, LogOut, Settings } from 'lucide-react';
import { useState } from 'react';
import Link from 'next/link';

export interface User {
  name: string;
  avatarUrl?: string;
}

export interface UserMenuProps {
  user: User;
  onLogout?: () => void;
  className?: string;
  isMobile?: boolean;
  onNavigate?: () => void;
}

export function UserMenu({
  user,
  onLogout,
  className = '',
  isMobile = false,
  onNavigate,
}: UserMenuProps) {
  const [isOpen, setIsOpen] = useState(false);

  const initials = user.name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  if (isMobile) {
    return (
      <div className={className}>
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-sm font-semibold text-white dark:bg-blue-500">
            {user.avatarUrl ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={user.avatarUrl} alt={user.name} className="h-10 w-10 rounded-full" />
            ) : (
              initials
            )}
          </div>
          <div>
            <p className="text-sm font-medium text-slate-900 dark:text-slate-100">{user.name}</p>
          </div>
        </div>

        <div className="mt-4 flex flex-col gap-2">
          <Link
            href="/profile"
            onClick={onNavigate}
            className="flex items-center gap-3 rounded-lg px-4 py-2.5 text-left text-sm font-medium text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            <Settings className="h-4 w-4" />
            Settings
          </Link>
          <button
            onClick={() => {
              onNavigate?.();
              onLogout?.();
            }}
            className="flex items-center gap-3 rounded-lg px-4 py-2.5 text-left text-sm font-medium text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 rounded-lg px-3 py-2 hover:bg-slate-100 dark:hover:bg-slate-800"
      >
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-xs font-semibold text-white dark:bg-blue-500">
          {user.avatarUrl ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={user.avatarUrl} alt={user.name} className="h-8 w-8 rounded-full" />
          ) : (
            initials
          )}
        </div>
        <span className="hidden text-sm font-medium text-slate-700 dark:text-slate-300 lg:inline">
          {user.name}
        </span>
        <ChevronDown className="h-4 w-4 text-slate-500" />
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setIsOpen(false)} />
          <div className="absolute right-0 top-full z-20 mt-2 w-56 rounded-lg border border-slate-200 bg-white shadow-lg dark:border-slate-700 dark:bg-slate-800">
            <div className="p-2">
              <Link
                href="/profile"
                onClick={() => setIsOpen(false)}
                className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm font-medium text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700"
              >
                <Settings className="h-4 w-4" />
                Settings
              </Link>
              <div className="my-1 h-px bg-slate-200 dark:bg-slate-700" />
              <button
                onClick={() => {
                  setIsOpen(false);
                  onLogout?.();
                }}
                className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm font-medium text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950"
              >
                <LogOut className="h-4 w-4" />
                Logout
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
