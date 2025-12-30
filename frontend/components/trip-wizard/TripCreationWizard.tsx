'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { X } from 'lucide-react';
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
import { useToast } from '@/components/ui/toast';
import { apiRequest, getAuthToken } from '@/lib/api/auth-utils';
import { getTravelerProfile } from '@/lib/api/profile';
import { getCountryName } from '@/lib/data/countries';
import { useGenerationProgress } from '@/contexts/GenerationProgressContext';

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

export type TripPurposeType =
  | 'Tourism'
  | 'Business'
  | 'Adventure'
  | 'Education'
  | 'Family Visit'
  | 'Transit'
  | 'Work'
  | 'Study'
  | 'Medical'
  | 'Other';

export interface TripDetails {
  departureDate: string;
  returnDate: string;
  budget: number;
  currency: 'USD' | 'EUR' | 'GBP' | 'JPY' | 'AUD' | 'CAD';
  tripPurposes: TripPurposeType[];
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

type ResidencyStatusForm =
  | 'Citizen'
  | 'Permanent Resident'
  | 'Temporary Resident'
  | 'Student Visa'
  | 'Work Visa'
  | '';
type TravelStyleForm = 'Relaxed' | 'Balanced' | 'Packed' | 'Budget-Focused' | '';

// Map profile residency status to form values
function mapResidencyStatus(status: string): ResidencyStatusForm {
  const mapping: Record<string, ResidencyStatusForm> = {
    citizen: 'Citizen',
    permanent_resident: 'Permanent Resident',
    temporary_resident: 'Temporary Resident',
    visitor: 'Temporary Resident',
  };
  return mapping[status] || '';
}

// Map profile travel style to form values
function mapTravelStyle(style: string): TravelStyleForm {
  const mapping: Record<string, TravelStyleForm> = {
    budget: 'Budget-Focused',
    balanced: 'Balanced',
    luxury: 'Relaxed',
  };
  return mapping[style] || '';
}

export default function TripCreationWizard() {
  const router = useRouter();
  const toast = useToast();
  const { startGeneration } = useGenerationProgress();
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
      tripPurposes: [],
    },
    preferences: {
      travelStyle: '',
      interests: [],
      dietaryRestrictions: [],
      accessibilityNeeds: '',
    },
  });

  // Load draft and profile on mount
  useEffect(() => {
    let hasDraft = false;

    // First, try to load saved draft
    const savedDraft = localStorage.getItem(DRAFT_KEY);
    if (savedDraft) {
      try {
        const parsed = JSON.parse(savedDraft);
        setFormData(parsed.formData);
        setCurrentStep(parsed.currentStep || 1);
        hasDraft = true;
      } catch (error) {
        console.error('Failed to load draft:', error);
      }
    }

    // Then, load traveler profile and pre-fill empty fields
    const loadProfile = async () => {
      try {
        const profile = await getTravelerProfile();
        if (profile) {
          setFormData((prev) => {
            // Only pre-fill if no draft exists or if fields are empty
            const shouldPreFillTraveler = !hasDraft || !prev.travelerDetails.nationality;
            const shouldPreFillPrefs = !hasDraft || !prev.preferences.travelStyle;

            return {
              ...prev,
              travelerDetails: shouldPreFillTraveler
                ? {
                    ...prev.travelerDetails,
                    nationality:
                      getCountryName(profile.nationality) || prev.travelerDetails.nationality,
                    residenceCountry:
                      getCountryName(profile.residencyCountry) ||
                      prev.travelerDetails.residenceCountry,
                    residencyStatus:
                      mapResidencyStatus(profile.residencyStatus) ||
                      prev.travelerDetails.residencyStatus,
                  }
                : prev.travelerDetails,
              preferences: shouldPreFillPrefs
                ? {
                    ...prev.preferences,
                    travelStyle:
                      mapTravelStyle(profile.travelStyle) || prev.preferences.travelStyle,
                    dietaryRestrictions: profile.dietaryRestrictions?.length
                      ? profile.dietaryRestrictions
                      : prev.preferences.dietaryRestrictions,
                    accessibilityNeeds:
                      profile.accessibilityNeeds || prev.preferences.accessibilityNeeds,
                  }
                : prev.preferences,
            };
          });
        }
      } catch (error) {
        // Silently fail - profile pre-fill is optional
        console.warn('Could not load traveler profile for pre-fill:', error);
      }
    };

    loadProfile();
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
      toast.warning(
        'Please check all fields and correct any errors before submitting.',
        'Validation Error',
      );
      return;
    }

    setIsSubmitting(true);
    try {
      // Check if user is authenticated
      const token = await getAuthToken();
      if (!token) {
        toast.error('You must be logged in to create a trip.', 'Authentication Error');
        router.push('/login');
        return;
      }

      // Transform form data to match backend API contract
      const tripData = {
        traveler_details: {
          name: validation.data.travelerDetails.name,
          email: validation.data.travelerDetails.email,
          age: validation.data.travelerDetails.age,
          nationality: validation.data.travelerDetails.nationality,
          residencyCountry: validation.data.travelerDetails.residenceCountry,
          residencyStatus: validation.data.travelerDetails.residencyStatus,
          originCity: validation.data.travelerDetails.originCity,
          partySize: validation.data.travelerDetails.partySize,
          companionAges: validation.data.travelerDetails.partyAges,
        },
        destinations: validation.data.destinations.map((dest, index) => ({
          id: crypto.randomUUID(),
          country: dest.country,
          city: dest.city,
          order: index,
        })),
        trip_details: {
          departureDate: validation.data.tripDetails.departureDate,
          returnDate: validation.data.tripDetails.returnDate,
          budget: validation.data.tripDetails.budget,
          budgetCurrency: validation.data.tripDetails.currency,
          tripPurposes: validation.data.tripDetails.tripPurposes.map((p: string) =>
            p.toLowerCase().replace(/ /g, '_'),
          ),
        },
        preferences: {
          travelStyle: validation.data.preferences.travelStyle,
          interests: validation.data.preferences.interests,
          dietaryRestrictions: validation.data.preferences.dietaryRestrictions,
          accessibilityNeeds: validation.data.preferences.accessibilityNeeds,
        },
      };

      // API call to create trip with validated data
      const trip = await apiRequest<{ id: string }>('/api/trips', {
        method: 'POST',
        body: JSON.stringify(tripData),
      });

      // Clear draft and validation errors
      localStorage.removeItem(DRAFT_KEY);
      setValidationErrors(null);
      setShowValidationErrors(false);

      // Start generation modal and redirect to trips list
      startGeneration(trip.id);
      toast.success('Trip created! Generating your report...', 'Success');
      router.push('/trips');
    } catch (error) {
      console.error('Submission error:', error);
      toast.error(
        error instanceof Error ? error.message : 'Failed to create trip. Please try again.',
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  // Calculate progress percentage
  const progressPercentage = showSummary ? 100 : ((currentStep - 1) / TOTAL_STEPS) * 100;

  return (
    <div className="relative py-8">
      {/* Subtle background pattern (relative to container) */}
      <div
        className="absolute inset-0 opacity-[0.03] dark:opacity-[0.02] pointer-events-none rounded-lg"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%232563eb' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }}
      />

      <div className="relative max-w-4xl mx-auto px-4">
        {/* Close Button */}
        <Link
          href="/trips"
          className="absolute top-0 right-4 md:right-0 flex items-center gap-2 text-sm font-medium text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100 transition-colors"
          title="Cancel and return to trips"
        >
          <span className="hidden sm:inline">Cancel</span>
          <X className="h-5 w-5" />
        </Link>

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
