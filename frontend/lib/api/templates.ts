/**
 * Templates API Client
 *
 * API functions for trip template management
 */

import type {
  CreateTripFromTemplateRequest,
  PublicTemplate,
  TripTemplate,
  TripTemplateCreate,
  TripTemplateUpdate,
} from '@/types/profile';
import { getAuthToken } from './auth-utils';

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

/**
 * Generic API request helper
 */
async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = await getAuthToken();

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: 'An unexpected error occurred',
    }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  // Handle 204 No Content responses
  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

// ============================================
// Templates API Functions
// ============================================

/**
 * List all trip templates for the authenticated user
 */
export async function listTemplates(): Promise<TripTemplate[]> {
  return apiRequest<TripTemplate[]>('/api/templates');
}

/**
 * Get a specific trip template by ID
 */
export async function getTemplate(templateId: string): Promise<TripTemplate> {
  return apiRequest<TripTemplate>(`/api/templates/${templateId}`);
}

/**
 * Create a new trip template
 */
export async function createTemplate(data: TripTemplateCreate): Promise<TripTemplate> {
  return apiRequest<TripTemplate>('/api/templates', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Update an existing trip template
 */
export async function updateTemplate(
  templateId: string,
  data: TripTemplateUpdate,
): Promise<TripTemplate> {
  return apiRequest<TripTemplate>(`/api/templates/${templateId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

/**
 * Delete a trip template
 */
export async function deleteTemplate(templateId: string): Promise<void> {
  return apiRequest<void>(`/api/templates/${templateId}`, {
    method: 'DELETE',
  });
}

// ============================================
// Public Templates API Functions
// ============================================

/**
 * List public templates (no authentication required)
 */
export async function listPublicTemplates(options?: {
  tag?: string;
  destination?: string;
  limit?: number;
  offset?: number;
}): Promise<PublicTemplate[]> {
  const params = new URLSearchParams();
  if (options?.tag) params.append('tag', options.tag);
  if (options?.destination) params.append('destination', options.destination);
  if (options?.limit) params.append('limit', options.limit.toString());
  if (options?.offset) params.append('offset', options.offset.toString());

  const queryString = params.toString();
  const endpoint = queryString ? `/api/templates/public?${queryString}` : '/api/templates/public';

  return apiRequest<PublicTemplate[]>(endpoint);
}

/**
 * Get featured public templates
 */
export async function getFeaturedTemplates(limit = 6): Promise<PublicTemplate[]> {
  return apiRequest<PublicTemplate[]>(`/api/templates/public/featured?limit=${limit}`);
}

/**
 * Clone a template to user's library
 */
export async function cloneTemplate(templateId: string): Promise<TripTemplate> {
  return apiRequest<TripTemplate>(`/api/templates/${templateId}/clone`, {
    method: 'POST',
  });
}

/**
 * Create a trip from a template
 */
export async function createTripFromTemplate(
  templateId: string,
  data?: CreateTripFromTemplateRequest,
): Promise<Record<string, unknown>> {
  return apiRequest<Record<string, unknown>>(`/api/trips/from-template/${templateId}`, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  });
}

// ============================================
// Validation Helpers
// ============================================

/**
 * Validate template name (non-empty, max 100 chars)
 */
export function isValidTemplateName(name: string): boolean {
  return name.trim().length > 0 && name.trim().length <= 100;
}

/**
 * Validate template has at least one destination
 */
type TemplateDestination = TripTemplate['destinations'][number];

export function hasDestinations(
  destinations: TripTemplate['destinations'] | null | undefined,
): destinations is TripTemplate['destinations'] {
  return Array.isArray(destinations) && destinations.length > 0;
}

/**
 * Validate destination object has required fields
 */
export function isValidDestination(destination: unknown): destination is TemplateDestination {
  if (typeof destination !== 'object' || destination === null) {
    return false;
  }

  if (!('country' in destination)) {
    return false;
  }

  return (
    typeof (destination as TemplateDestination).country === 'string' &&
    (destination as TemplateDestination).country.length > 0
  );
}
