/**
 * Zod Validation Schemas for Trip Creation Wizard
 *
 * These schemas provide comprehensive validation for all 4 steps of the trip wizard:
 * - Step 1: Traveler Details
 * - Step 2: Destinations
 * - Step 3: Trip Details
 * - Step 4: Preferences
 */

import { z } from 'zod'

// ============================================================================
// STEP 1: Traveler Details Schema
// ============================================================================

export const travelerDetailsSchema = z.object({
  // Required fields
  name: z.string()
    .min(2, 'Name must be at least 2 characters')
    .max(100, 'Name must be less than 100 characters')
    .regex(/^[a-zA-Z\s'-]+$/, 'Name can only contain letters, spaces, hyphens, and apostrophes'),

  email: z.string()
    .email('Please enter a valid email address')
    .min(5, 'Email must be at least 5 characters')
    .max(255, 'Email must be less than 255 characters')
    .toLowerCase()
    .trim(),

  nationality: z.string()
    .min(1, 'Nationality is required'),

  residenceCountry: z.string()
    .min(1, 'Country of residence is required'),

  originCity: z.string()
    .min(2, 'Origin city must be at least 2 characters')
    .max(100, 'Origin city must be less than 100 characters'),

  residencyStatus: z.enum([
    'Citizen',
    'Permanent Resident',
    'Temporary Resident',
    'Student Visa',
    'Work Visa'
  ], {
    message: 'Residency status is required'
  }),

  partySize: z.number()
    .int('Party size must be a whole number')
    .min(1, 'Party size must be at least 1')
    .max(20, 'Party size cannot exceed 20 people'),

  // Optional fields
  age: z.number()
    .int('Age must be a whole number')
    .min(0, 'Age must be 0 or greater')
    .max(120, 'Age must be less than 120')
    .optional(),

  partyAges: z.array(
    z.number()
      .int('Age must be a whole number')
      .min(0, 'Age must be 0 or greater')
      .max(120, 'Age must be less than 120')
  ).default([]),

  contactPreferences: z.array(z.string()).default([]),
}).refine(
  (data) => {
    // If party size > 1, party ages array should have (partySize - 1) entries
    if (data.partySize > 1) {
      return data.partyAges.length === data.partySize - 1
    }
    return true
  },
  {
    message: 'Please provide ages for all additional travelers',
    path: ['partyAges']
  }
)

// Type inference from schema
export type TravelerDetailsFormData = z.infer<typeof travelerDetailsSchema>

// ============================================================================
// STEP 2: Destinations Schema
// ============================================================================

const destinationSchema = z.object({
  country: z.string()
    .min(1, 'Country is required')
    .max(100, 'Country name must be less than 100 characters'),

  city: z.string()
    .min(1, 'City is required')
    .max(100, 'City name must be less than 100 characters'),
})

export const destinationsSchema = z.array(destinationSchema)
  .min(1, 'At least one destination is required')
  .max(10, 'Maximum 10 destinations allowed')
  .refine(
    (destinations) => {
      // Check for duplicate destinations (same country + city combination)
      const uniqueKeys = new Set(
        destinations.map(d => `${d.country.toLowerCase()}|${d.city.toLowerCase()}`)
      )
      return uniqueKeys.size === destinations.length
    },
    {
      message: 'Duplicate destinations are not allowed',
    }
  )

// Type inference from schema
export type DestinationsFormData = z.infer<typeof destinationsSchema>

// ============================================================================
// STEP 3: Trip Details Schema
// ============================================================================

export const tripDetailsSchema = z.object({
  departureDate: z.string()
    .min(1, 'Departure date is required')
    .refine(
      (date) => {
        const parsedDate = new Date(date)
        return !isNaN(parsedDate.getTime())
      },
      { message: 'Invalid departure date format' }
    )
    .refine(
      (date) => {
        const today = new Date()
        today.setHours(0, 0, 0, 0)
        const parsedDate = new Date(date)
        return parsedDate >= today
      },
      { message: 'Departure date cannot be in the past' }
    ),

  returnDate: z.string()
    .min(1, 'Return date is required')
    .refine(
      (date) => {
        const parsedDate = new Date(date)
        return !isNaN(parsedDate.getTime())
      },
      { message: 'Invalid return date format' }
    ),

  budget: z.number()
    .positive('Budget must be greater than 0')
    .max(1000000, 'Budget cannot exceed 1,000,000')
    .refine(
      (value) => {
        // Ensure budget has at most 2 decimal places
        return (value * 100) % 1 === 0
      },
      { message: 'Budget can have at most 2 decimal places' }
    ),

  currency: z.enum(['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD'], {
    message: 'Currency is required'
  }),

  tripPurpose: z.enum([
    'Tourism',
    'Business',
    'Education',
    'Family Visit',
    'Medical',
    'Other'
  ], {
    message: 'Trip purpose is required'
  }),
}).refine(
  (data) => {
    // Return date must be after departure date
    const departure = new Date(data.departureDate)
    const returnDate = new Date(data.returnDate)
    return returnDate > departure
  },
  {
    message: 'Return date must be after departure date',
    path: ['returnDate']
  }
).refine(
  (data) => {
    // Trip duration should be reasonable (max 1 year)
    const departure = new Date(data.departureDate)
    const returnDate = new Date(data.returnDate)
    const daysDiff = (returnDate.getTime() - departure.getTime()) / (1000 * 60 * 60 * 24)
    return daysDiff <= 365
  },
  {
    message: 'Trip duration cannot exceed 1 year',
    path: ['returnDate']
  }
)

// Type inference from schema
export type TripDetailsFormData = z.infer<typeof tripDetailsSchema>

// ============================================================================
// STEP 4: Preferences Schema
// ============================================================================

export const preferencesSchema = z.object({
  travelStyle: z.enum([
    'Relaxed',
    'Balanced',
    'Packed',
    'Budget-Focused'
  ], {
    message: 'Travel style is required'
  }),

  interests: z.array(z.string())
    .min(1, 'Please select at least one interest')
    .max(10, 'Maximum 10 interests allowed'),

  dietaryRestrictions: z.array(z.string())
    .default([])
    .refine(
      (restrictions) => restrictions.length <= 10,
      { message: 'Maximum 10 dietary restrictions allowed' }
    ),

  accessibilityNeeds: z.string()
    .max(500, 'Accessibility needs must be less than 500 characters')
    .default(''),
})

// Type inference from schema
export type PreferencesFormData = z.infer<typeof preferencesSchema>

// ============================================================================
// COMPLETE TRIP FORM SCHEMA
// ============================================================================

export const completeTripFormSchema = z.object({
  travelerDetails: travelerDetailsSchema,
  destinations: destinationsSchema,
  tripDetails: tripDetailsSchema,
  preferences: preferencesSchema,
})

// Type inference from complete schema
export type CompleteTripFormData = z.infer<typeof completeTripFormSchema>

// ============================================================================
// VALIDATION HELPER FUNCTIONS
// ============================================================================

/**
 * Validates a specific step of the trip wizard
 * @param step - Step number (1-4)
 * @param data - Data to validate
 * @returns Validation result with success flag and errors
 */
export function validateStep(
  step: number,
  data: unknown
): { success: boolean; errors?: z.ZodError } {
  let schema: z.ZodSchema

  switch (step) {
    case 1:
      schema = travelerDetailsSchema
      break
    case 2:
      schema = destinationsSchema
      break
    case 3:
      schema = tripDetailsSchema
      break
    case 4:
      schema = preferencesSchema
      break
    default:
      throw new Error(`Invalid step number: ${step}`)
  }

  const result = schema.safeParse(data)

  return {
    success: result.success,
    errors: result.success ? undefined : result.error,
  }
}

/**
 * Gets user-friendly error messages for a specific field
 * @param errors - Zod validation errors
 * @param fieldPath - Field path (e.g., 'name', 'partyAges')
 * @returns Array of error messages for the field
 */
export function getFieldErrors(
  errors: z.ZodError | undefined,
  fieldPath: string
): string[] {
  if (!errors) return []

  return errors.issues
    .filter((error) => error.path.join('.') === fieldPath)
    .map((error) => error.message)
}

/**
 * Checks if a specific field has errors
 * @param errors - Zod validation errors
 * @param fieldPath - Field path
 * @returns True if field has errors
 */
export function hasFieldError(
  errors: z.ZodError | undefined,
  fieldPath: string
): boolean {
  return getFieldErrors(errors, fieldPath).length > 0
}

/**
 * Validates the entire trip form (all steps)
 * @param data - Complete trip form data
 * @returns Validation result
 */
export function validateCompleteForm(
  data: unknown
): { success: boolean; errors?: z.ZodError; data?: CompleteTripFormData } {
  const result = completeTripFormSchema.safeParse(data)

  return {
    success: result.success,
    errors: result.success ? undefined : result.error,
    data: result.success ? result.data : undefined,
  }
}
