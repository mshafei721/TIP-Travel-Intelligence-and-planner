'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { StepWelcome } from './StepWelcome';
import { StepResidency, type ResidencyData } from './StepResidency';
import { StepPreferences, type PreferencesData } from './StepPreferences';
import { StepComplete } from './StepComplete';
import { updateTravelerProfile } from '@/lib/api/profile';
import { useToast } from '@/components/ui/toast';
import type { TravelStyle } from '@/types/profile';

type Step = 'welcome' | 'residency' | 'preferences' | 'complete';

const STEPS: Step[] = ['welcome', 'residency', 'preferences', 'complete'];

export function OnboardingWizard() {
  const router = useRouter();
  const toast = useToast();
  const [currentStep, setCurrentStep] = useState<Step>('welcome');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Form data
  const [residencyData, setResidencyData] = useState<ResidencyData>({
    nationality: '',
    residencyCountry: '',
    residencyStatus: '',
    dateOfBirth: '',
  });

  const [preferencesData, setPreferencesData] = useState<PreferencesData>({
    travelStyle: 'balanced' as TravelStyle,
    dietaryRestrictions: [],
    accessibilityNeeds: '',
  });

  const currentStepIndex = STEPS.indexOf(currentStep);

  const goToNext = () => {
    const nextIndex = currentStepIndex + 1;
    if (nextIndex < STEPS.length) {
      setCurrentStep(STEPS[nextIndex]);
    }
  };

  const goToBack = () => {
    const prevIndex = currentStepIndex - 1;
    if (prevIndex >= 0) {
      setCurrentStep(STEPS[prevIndex]);
    }
  };

  const handleComplete = async () => {
    setIsSubmitting(true);
    try {
      await updateTravelerProfile({
        nationality: residencyData.nationality,
        residencyCountry: residencyData.residencyCountry,
        residencyStatus: residencyData.residencyStatus,
        dateOfBirth: residencyData.dateOfBirth || null,
        travelStyle: preferencesData.travelStyle,
        dietaryRestrictions: preferencesData.dietaryRestrictions,
        accessibilityNeeds: preferencesData.accessibilityNeeds || null,
      });

      toast.success('Profile created successfully!');
      router.push('/dashboard');
    } catch (error) {
      console.error('Failed to save profile:', error);
      toast.error('Failed to save profile. Please try again.');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-slate-50 to-white px-4 py-8 dark:from-slate-900 dark:to-slate-800">
      {/* Progress Indicator */}
      {currentStep !== 'welcome' && (
        <div className="mb-8 flex items-center gap-2">
          {STEPS.slice(1).map((step, index) => (
            <div key={step} className="flex items-center">
              <div
                className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium transition-all ${
                  STEPS.indexOf(step) <= currentStepIndex
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-200 text-slate-500 dark:bg-slate-700 dark:text-slate-400'
                }`}
              >
                {index + 1}
              </div>
              {index < STEPS.slice(1).length - 1 && (
                <div
                  className={`mx-2 h-0.5 w-12 transition-all ${
                    STEPS.indexOf(step) < currentStepIndex
                      ? 'bg-blue-600'
                      : 'bg-slate-200 dark:bg-slate-700'
                  }`}
                />
              )}
            </div>
          ))}
        </div>
      )}

      {/* Step Content */}
      <div className="w-full max-w-lg">
        {currentStep === 'welcome' && <StepWelcome onNext={goToNext} />}

        {currentStep === 'residency' && (
          <StepResidency
            data={residencyData}
            onChange={setResidencyData}
            onNext={goToNext}
            onBack={goToBack}
          />
        )}

        {currentStep === 'preferences' && (
          <StepPreferences
            data={preferencesData}
            onChange={setPreferencesData}
            onNext={goToNext}
            onBack={goToBack}
          />
        )}

        {currentStep === 'complete' && (
          <StepComplete onComplete={handleComplete} isLoading={isSubmitting} />
        )}
      </div>

      {/* Skip Option */}
      {currentStep !== 'complete' && currentStep !== 'welcome' && (
        <button
          onClick={() => router.push('/dashboard')}
          className="mt-6 text-sm text-slate-500 underline-offset-4 hover:text-slate-700 hover:underline dark:text-slate-400 dark:hover:text-slate-300"
        >
          Skip for now
        </button>
      )}
    </div>
  );
}
