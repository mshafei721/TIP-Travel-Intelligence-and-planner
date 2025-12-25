'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { type z } from 'zod';
import StepIndicator from './StepIndicator';
import ProgressBar from './ProgressBar';
import Step1TravelerDetails from './Step1TravelerDetails';
import Step2Destination from './Step2Destination';
import Step3TripDetails from './Step3TripDetails';
import Step4Preferences from './Step4Preferences';
import TripSummary from './TripSummary';
import AutoSaveIndicator from './AutoSaveIndicator';
import NavigationButtons from './NavigationButtons';
import { validateStep, validateCompleteForm } from '@/lib/validation/trip-wizard-schemas';

// TypeScript interfaces matching the spec
export interface TravelerDetails {
  name: string;
  email: string;
  age?: number;
  nationality: string;
  residenceCountry: string;
  originCity: string;
  residencyStatus:
    | 'Citizen'
    | 'Permanent Resident'
    | 'Temporary Resident'
    | 'Student Visa'
    | 'Work Visa'
    | '';
  partySize: number;
  partyAges: number[];
  contactPreferences: string[];
}

export interface Destination {
  country: string;
  city: string;
}

export interface TripDetails {
  departureDate: string;
  returnDate: string;
  budget: number;
  currency: 'USD' | 'EUR' | 'GBP' | 'JPY' | 'AUD' | 'CAD';
  tripPurpose: 'Tourism' | 'Business' | 'Education' | 'Family Visit' | 'Medical' | 'Other' | '';
}

export interface TripPreferences {
  travelStyle: 'Relaxed' | 'Balanced' | 'Packed' | 'Budget-Focused' | '';
  interests: string[];
  dietaryRestrictions: string[];
  accessibilityNeeds: string;
}

export interface TripFormData {
  travelerDetails: TravelerDetails;
  destinations: Destination[];
  tripDetails: TripDetails;
  preferences: TripPreferences;
}

const TOTAL_STEPS = 4;
const DRAFT_KEY = 'trip-wizard-draft';

export default function TripCreationWizard() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [showSummary, setShowSummary] = useState(false);
  const [showSaveIndicator, setShowSaveIndicator] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [validationErrors, setValidationErrors] = useState<z.ZodError | null>(null);
  const [showValidationErrors, setShowValidationErrors] = useState(false);

  // Form data state
  const [formData, setFormData] = useState<TripFormData>({
    travelerDetails: {
      name: '',
      email: '',
      age: undefined,
      nationality: '',
      residenceCountry: '',
      originCity: '',
      residencyStatus: '',
      partySize: 1,
      partyAges: [],
      contactPreferences: [],
    },
    destinations: [{ country: '', city: '' }],
    tripDetails: {
      departureDate: '',
      returnDate: '',
      budget: 0,
      currency: 'USD',
      tripPurpose: '',
    },
    preferences: {
      travelStyle: '',
      interests: [],
      dietaryRestrictions: [],
      accessibilityNeeds: '',
    },
  });

  // Load draft on mount
  useEffect(() => {
    const savedDraft = localStorage.getItem(DRAFT_KEY);
    if (savedDraft) {
      try {
        const parsed = JSON.parse(savedDraft);
        setFormData(parsed.formData);
        setCurrentStep(parsed.currentStep || 1);
      } catch (error) {
        console.error('Failed to load draft:', error);
      }
    }
  }, []);

  // Auto-save draft
  const saveDraft = useCallback(() => {
    const draft = {
      formData,
      currentStep,
      savedAt: new Date().toISOString(),
    };
    localStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
    setShowSaveIndicator(true);
    setTimeout(() => setShowSaveIndicator(false), 3000);
  }, [formData, currentStep]);

  // Update form data
  const updateFormData = <K extends keyof TripFormData>(section: K, data: TripFormData[K]) => {
    setFormData((prev) => ({
      ...prev,
      [section]: data,
    }));
  };

  // Navigation
  const handleNext = () => {
    // Get data for current step
    let stepData: unknown;
    switch (currentStep) {
      case 1:
        stepData = formData.travelerDetails;
        break;
      case 2:
        stepData = formData.destinations;
        break;
      case 3:
        stepData = formData.tripDetails;
        break;
      case 4:
        stepData = formData.preferences;
        break;
      default:
        stepData = null;
    }

    // Validate current step
    const validation = validateStep(currentStep, stepData);

    if (!validation.success) {
      // Show validation errors
      setValidationErrors(validation.errors || null);
      setShowValidationErrors(true);

      // Scroll to top to show errors
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }

    // Clear validation errors
    setValidationErrors(null);
    setShowValidationErrors(false);

    // Save draft
    saveDraft();

    // Proceed to next step
    if (currentStep < TOTAL_STEPS) {
      setCurrentStep((prev) => prev + 1);
    } else {
      setShowSummary(true);
    }
  };

  const handleBack = () => {
    // Clear validation errors when going back
    setValidationErrors(null);
    setShowValidationErrors(false);

    if (showSummary) {
      setShowSummary(false);
    } else if (currentStep > 1) {
      setCurrentStep((prev) => prev - 1);
    }
  };

  const handleEditFromSummary = (step: number) => {
    setShowSummary(false);
    setCurrentStep(step);
    // Clear validation errors
    setValidationErrors(null);
    setShowValidationErrors(false);
  };

  const handleSubmit = async () => {
    // Validate complete form before submission
    const validation = validateCompleteForm(formData);

    if (!validation.success) {
      // Show validation errors
      setValidationErrors(validation.errors || null);
      setShowValidationErrors(true);
      alert('Please check all fields and correct any errors before submitting.');
      return;
    }

    setIsSubmitting(true);
    try {
      // API call to create trip with validated data
      const response = await fetch('/api/trips', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(validation.data),
      });

      if (!response.ok) throw new Error('Failed to create trip');

      const trip = await response.json();

      // Clear draft and validation errors
      localStorage.removeItem(DRAFT_KEY);
      setValidationErrors(null);
      setShowValidationErrors(false);

      // Redirect to trip dashboard or report generation page
      router.push(`/trips/${trip.id}`);
    } catch (error) {
      console.error('Submission error:', error);
      alert('Failed to create trip. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Calculate progress percentage
  const progressPercentage = showSummary ? 100 : ((currentStep - 1) / TOTAL_STEPS) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-amber-50/20 dark:from-slate-950 dark:via-slate-900 dark:to-slate-900">
      {/* Topographic background pattern */}
      <div
        className="fixed inset-0 opacity-[0.03] dark:opacity-[0.02] pointer-events-none"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%232563eb' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }}
      />

      <div className="relative max-w-4xl mx-auto px-4 py-8 md:py-12">
        {/* Header */}
        <div className="text-center mb-8 md:mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900 dark:text-slate-50 mb-3 tracking-tight">
            Plan Your Journey
          </h1>
          <p className="text-base text-slate-600 dark:text-slate-400 font-light">
            Share your travel details for personalized intelligence
          </p>
        </div>

        {/* Progress Bar */}
        <ProgressBar progress={progressPercentage} />

        {/* Step Indicator */}
        {!showSummary && <StepIndicator currentStep={currentStep} totalSteps={TOTAL_STEPS} />}

        {/* Main Content Area */}
        <div className="mt-8 md:mt-12">
          {/* Validation Error Banner */}
          {showValidationErrors && validationErrors && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900 rounded-lg animate-slideIn">
              <div className="flex items-start">
                <svg
                  className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5 mr-3 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-red-800 dark:text-red-200 mb-1">
                    Please correct the following errors:
                  </h3>
                  <ul className="text-sm text-red-700 dark:text-red-300 list-disc list-inside space-y-1">
                    {validationErrors.issues.map((error, index) => (
                      <li key={index}>
                        {error.path.length > 0 && (
                          <span className="font-medium">{error.path.join('.')}: </span>
                        )}
                        {error.message}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Step Pages */}
          {!showSummary && (
            <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-800 p-6 md:p-10">
              {currentStep === 1 && (
                <Step1TravelerDetails
                  data={formData.travelerDetails}
                  onChange={(data) => updateFormData('travelerDetails', data)}
                />
              )}
              {currentStep === 2 && (
                <Step2Destination
                  data={formData.destinations}
                  onChange={(data) => updateFormData('destinations', data)}
                />
              )}
              {currentStep === 3 && (
                <Step3TripDetails
                  data={formData.tripDetails}
                  onChange={(data) => updateFormData('tripDetails', data)}
                />
              )}
              {currentStep === 4 && (
                <Step4Preferences
                  data={formData.preferences}
                  onChange={(data) => updateFormData('preferences', data)}
                />
              )}
            </div>
          )}

          {/* Summary Page */}
          {showSummary && <TripSummary formData={formData} onEdit={handleEditFromSummary} />}

          {/* Navigation Buttons */}
          {!showSummary && (
            <NavigationButtons
              currentStep={currentStep}
              totalSteps={TOTAL_STEPS}
              onBack={handleBack}
              onNext={handleNext}
              canGoBack={currentStep > 1}
              canGoNext={true} // Validation happens in handleNext before proceeding
            />
          )}

          {showSummary && (
            <NavigationButtons
              currentStep={TOTAL_STEPS + 1}
              totalSteps={TOTAL_STEPS}
              onBack={handleBack}
              onNext={handleSubmit}
              canGoBack={true}
              canGoNext={!isSubmitting}
              isSubmitting={isSubmitting}
              nextLabel="Confirm & Generate Report"
            />
          )}
        </div>

        {/* Auto-save indicator */}
        <AutoSaveIndicator show={showSaveIndicator} />
      </div>

      <style jsx>{`
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-slideIn {
          animation: slideIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}
