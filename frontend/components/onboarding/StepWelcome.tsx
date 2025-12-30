'use client';

import { Globe, Plane, Shield, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface StepWelcomeProps {
  onNext: () => void;
}

export function StepWelcome({ onNext }: StepWelcomeProps) {
  return (
    <div className="flex flex-col items-center text-center">
      {/* Hero Icon */}
      <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600">
        <Globe className="h-10 w-10 text-white" />
      </div>

      {/* Welcome Message */}
      <h1 className="mb-3 text-3xl font-bold text-slate-900 dark:text-white">Welcome to TIP!</h1>
      <p className="mb-8 max-w-md text-lg text-slate-600 dark:text-slate-400">
        Let&apos;s set up your travel profile to personalize your experience and get accurate visa
        information.
      </p>

      {/* Feature Highlights */}
      <div className="mb-8 grid w-full max-w-md gap-4">
        <FeatureCard
          icon={<Shield className="h-5 w-5 text-blue-600" />}
          title="Accurate Visa Requirements"
          description="Get personalized visa information based on your nationality"
        />
        <FeatureCard
          icon={<Plane className="h-5 w-5 text-purple-600" />}
          title="Smart Trip Planning"
          description="AI-powered itineraries tailored to your preferences"
        />
        <FeatureCard
          icon={<Sparkles className="h-5 w-5 text-amber-600" />}
          title="Personalized Recommendations"
          description="Discover destinations that match your travel style"
        />
      </div>

      {/* CTA */}
      <Button onClick={onNext} size="lg" className="w-full max-w-md bg-blue-600 hover:bg-blue-700">
        Let&apos;s Get Started
      </Button>

      <p className="mt-4 text-sm text-slate-500 dark:text-slate-400">
        This will only take about 2 minutes
      </p>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="flex items-start gap-4 rounded-lg border border-slate-200 bg-white p-4 text-left dark:border-slate-700 dark:bg-slate-800">
      <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-slate-100 dark:bg-slate-700">
        {icon}
      </div>
      <div>
        <h3 className="font-medium text-slate-900 dark:text-white">{title}</h3>
        <p className="text-sm text-slate-500 dark:text-slate-400">{description}</p>
      </div>
    </div>
  );
}
