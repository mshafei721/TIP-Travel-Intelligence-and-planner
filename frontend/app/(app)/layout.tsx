'use client';

import { AppShell } from '@/components/shell';

const navigationItems = [
  { label: 'Dashboard', href: '/dashboard' },
  { label: 'My Trips', href: '/trips' },
  { label: 'Create Trip', href: '/trips/create' },
  { label: 'Profile', href: '/profile' },
];

// Mock user - will be replaced with real auth in Milestone 2
const mockUser = {
  name: 'Demo User',
  // avatarUrl: undefined, // Will show initials
};

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const handleLogout = () => {
    // TODO: Implement logout logic in Milestone 2
    console.log('Logout clicked');
  };

  return (
    <AppShell navigationItems={navigationItems} user={mockUser} onLogout={handleLogout}>
      {children}
    </AppShell>
  );
}
