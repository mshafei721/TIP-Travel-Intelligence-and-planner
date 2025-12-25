'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export interface NavigationItem {
  label: string;
  href: string;
}

export interface MainNavProps {
  items: NavigationItem[];
  className?: string;
  isMobile?: boolean;
}

export function MainNav({ items, className = '', isMobile = false }: MainNavProps) {
  const pathname = usePathname();

  if (isMobile) {
    return (
      <nav className="flex flex-col gap-2">
        {items.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`rounded-lg px-4 py-2.5 text-left text-base font-medium transition-colors ${
                isActive
                  ? 'bg-blue-50 text-blue-600 dark:bg-blue-950 dark:text-blue-400'
                  : 'text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    );
  }

  return (
    <nav className={`flex items-center gap-1 ${className}`}>
      {items.map((item) => {
        const isActive = pathname === item.href;
        return (
          <Link
            key={item.href}
            href={item.href}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              isActive
                ? 'bg-blue-50 text-blue-600 dark:bg-blue-950 dark:text-blue-400'
                : 'text-slate-700 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-slate-100'
            }`}
          >
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
