/**
 * Backend API Client
 *
 * Wrapper around fetch for calling FastAPI backend endpoints.
 * Features:
 * - Request timeout using AbortController
 * - Exponential backoff retry for transient errors
 * - Proper error handling with typed errors
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

// Configuration
const DEFAULT_TIMEOUT_MS = 30000; // 30 seconds
const MAX_RETRIES = 3;
const INITIAL_RETRY_DELAY_MS = 1000; // 1 second
const RETRY_STATUS_CODES = [408, 429, 500, 502, 503, 504]; // Status codes worth retrying

interface ApiError {
  detail: string;
  code?: string;
  request_id?: string;
}

export class ApiTimeoutError extends Error {
  constructor(message = 'Request timed out') {
    super(message);
    this.name = 'ApiTimeoutError';
  }
}

export class ApiNetworkError extends Error {
  constructor(message = 'Network error occurred') {
    super(message);
    this.name = 'ApiNetworkError';
  }
}

export class ApiResponseError extends Error {
  status: number;
  code?: string;
  requestId?: string;

  constructor(message: string, status: number, code?: string, requestId?: string) {
    super(message);
    this.name = 'ApiResponseError';
    this.status = status;
    this.code = code;
    this.requestId = requestId;
  }
}

interface RequestConfig extends RequestInit {
  timeout?: number;
  retries?: number;
  skipRetry?: boolean;
}

/**
 * Sleep for a specified duration
 */
const sleep = (ms: number): Promise<void> => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Calculate exponential backoff delay with jitter
 */
const getRetryDelay = (attempt: number): number => {
  const exponentialDelay = INITIAL_RETRY_DELAY_MS * Math.pow(2, attempt);
  const jitter = Math.random() * 1000; // Add up to 1 second of random jitter
  return Math.min(exponentialDelay + jitter, 30000); // Cap at 30 seconds
};

/**
 * Check if an error is retryable
 */
const isRetryableError = (error: unknown, status?: number): boolean => {
  // Retry on network errors
  if (error instanceof TypeError && error.message.includes('fetch')) {
    return true;
  }
  // Retry on timeout
  if (error instanceof ApiTimeoutError) {
    return true;
  }
  // Retry on specific status codes
  if (status && RETRY_STATUS_CODES.includes(status)) {
    return true;
  }
  return false;
};

export class ApiClient {
  private baseUrl: string;
  private getToken: () => Promise<string | null>;

  constructor(getToken: () => Promise<string | null>) {
    this.baseUrl = `${API_BASE_URL}/api`;
    this.getToken = getToken;
  }

  private async request<T>(endpoint: string, options: RequestConfig = {}): Promise<T> {
    const {
      timeout = DEFAULT_TIMEOUT_MS,
      retries = MAX_RETRIES,
      skipRetry = false,
      ...fetchOptions
    } = options;

    const token = await this.getToken();

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...fetchOptions.headers,
    };

    let lastError: Error | null = null;
    let lastStatus: number | undefined;

    for (let attempt = 0; attempt <= retries; attempt++) {
      // Create AbortController for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      try {
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
          ...fetchOptions,
          headers,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);
        lastStatus = response.status;

        if (!response.ok) {
          const error: ApiError = await response.json().catch(() => ({
            detail: 'An unexpected error occurred',
          }));

          // Check if we should retry
          if (!skipRetry && attempt < retries && isRetryableError(null, response.status)) {
            lastError = new ApiResponseError(
              error.detail,
              response.status,
              error.code,
              error.request_id,
            );
            const delay = getRetryDelay(attempt);
            console.warn(
              `Request to ${endpoint} failed with status ${response.status}. Retrying in ${Math.round(delay)}ms... (attempt ${attempt + 1}/${retries})`,
            );
            await sleep(delay);
            continue;
          }

          throw new ApiResponseError(
            error.detail || `HTTP ${response.status}`,
            response.status,
            error.code,
            error.request_id,
          );
        }

        // Handle empty responses (204 No Content)
        if (response.status === 204) {
          return {} as T;
        }

        return response.json();
      } catch (error) {
        clearTimeout(timeoutId);

        // Handle abort (timeout)
        if (error instanceof Error && error.name === 'AbortError') {
          lastError = new ApiTimeoutError(`Request to ${endpoint} timed out after ${timeout}ms`);
        } else if (error instanceof TypeError) {
          // Network error
          lastError = new ApiNetworkError(
            `Network error while calling ${endpoint}: ${error.message}`,
          );
        } else if (error instanceof ApiResponseError) {
          lastError = error;
        } else {
          lastError = error as Error;
        }

        // Check if we should retry
        if (!skipRetry && attempt < retries && isRetryableError(lastError, lastStatus)) {
          const delay = getRetryDelay(attempt);
          console.warn(
            `Request to ${endpoint} failed: ${lastError.message}. Retrying in ${Math.round(delay)}ms... (attempt ${attempt + 1}/${retries})`,
          );
          await sleep(delay);
          continue;
        }

        throw lastError;
      }
    }

    // Should not reach here, but throw last error if we do
    throw lastError || new Error('Request failed after all retries');
  }

  async get<T>(endpoint: string, options?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  async post<T>(endpoint: string, data: unknown, options?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async patch<T>(endpoint: string, data: unknown, options?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async put<T>(endpoint: string, data: unknown, options?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete<T>(endpoint: string, options?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }
}
