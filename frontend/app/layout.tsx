import type { Metadata } from 'next';
import { DM_Sans, IBM_Plex_Mono } from 'next/font/google';
import { ThemeProvider } from '@/components/providers/ThemeProvider';
import { PostHogProvider } from '@/components/providers/PostHogProvider';
import './globals.css';

const dmSans = DM_Sans({
  variable: '--font-sans',
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
});

const ibmPlexMono = IBM_Plex_Mono({
  variable: '--font-mono',
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
});

export const metadata: Metadata = {
  title: 'TIP - Travel Intelligence & Planner',
  description:
    'AI-powered travel intelligence platform providing accurate visa requirements, destination insights, and personalized itineraries.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${dmSans.variable} ${ibmPlexMono.variable} antialiased`}>
        <PostHogProvider>
          <ThemeProvider>{children}</ThemeProvider>
        </PostHogProvider>
      </body>
    </html>
  );
}
