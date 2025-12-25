'use client';

import { Menu, X } from 'lucide-react';
import { useState } from 'react';
import Link from 'next/link';
import { MainNav, type NavigationItem } from './MainNav';
import { UserMenu, type User } from './UserMenu';

export type { NavigationItem, User };

export interface AppShellProps {
  children: React.ReactNode;
  navigationItems: NavigationItem[];
  user?: User;
  onLogout?: () => void;
}

export function AppShell({ children, navigationItems, user, onLogout }: AppShellProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Top Navigation */}
      <header className="sticky top-0 z-50 border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
        <div className="mx-auto max-w-7xl">
          <div className="flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
            {/* Logo */}
            <Link
              href="/"
              className="flex items-center gap-2 text-xl font-bold text-blue-600 dark:text-blue-400"
            >
              <svg
                className="h-8 w-8"
                viewBox="0 0 32 32"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M16 2L4 8v12c0 7.4 5.2 11.5 12 13 6.8-1.5 12-5.6 12-13V8l-12-6z"
                  fill="currentColor"
                  opacity="0.2"
                />
                <path
                  d="M16 2L4 8v12c0 7.4 5.2 11.5 12 13 6.8-1.5 12-5.6 12-13V8l-12-6z"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
                <path
                  d="M12 16l3 3 6-6"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              <span className="hidden sm:inline">TIP</span>
            </Link>

            {/* Desktop Navigation */}
            <MainNav items={navigationItems} className="hidden md:flex" />

            {/* Right Side: User Menu + Mobile Toggle */}
            <div className="flex items-center gap-4">
              {user && <UserMenu user={user} onLogout={onLogout} className="hidden md:flex" />}

              {/* Mobile Menu Button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden rounded-lg p-2 text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
                aria-label="Toggle menu"
              >
                {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Mobile Menu Panel */}
      <div
        className={`fixed right-0 top-16 z-40 h-[calc(100vh-4rem)] w-64 transform border-l border-slate-200 bg-white transition-transform duration-300 ease-in-out dark:border-slate-800 dark:bg-slate-900 md:hidden ${
          mobileMenuOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="flex flex-col p-4">
          {user && (
            <>
              <UserMenu
                user={user}
                onLogout={onLogout}
                className="mb-6 border-b border-slate-200 pb-6 dark:border-slate-800"
                isMobile
              />
            </>
          )}

          <MainNav items={navigationItems} isMobile />
        </div>
      </div>

      {/* Content Area */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">{children}</main>
    </div>
  );
}
