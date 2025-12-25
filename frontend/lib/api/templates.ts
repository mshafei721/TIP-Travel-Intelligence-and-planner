/**
 * Templates API Client
 *
 * API functions for trip template management
 */

import type { TripTemplate, TripTemplateCreate, TripTemplateUpdate } from '@/types/profile';

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

/**
 * Get authentication token from Supabase session
 */
async function getAuthToken(): Promise<string | null> {
  if (typeof window === 'undefined') return null;

  try {
    // Dynamically import Supabase client (browser-only)
    const { createClient } = await import('@/lib/supabase/client');
    const supabase = createClient();

    const {
      data: { session },
      error,
    } = await supabase.auth.getSession();

    if (error || !session) {
      console.warn('Failed to get Supabase session:', error);
      return null;
    }

    return session.access_token;
  } catch (error) {
    console.error('Error getting auth token:', error);
    return null;
  }
}

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
export function hasDestinations(destinations: unknown[]): boolean {
  return Array.isArray(destinations) && destinations.length > 0;
}

/**
 * Validate destination object has required fields
 */
export function isValidDestination(destination: unknown): boolean {
  if (typeof destination !== 'object' || destination === null) {
    return false;
  }

  const dest = destination as Record<string, unknown>;
  return typeof dest.country === 'string' && dest.country.length > 0;
}
