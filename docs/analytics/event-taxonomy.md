# TIP Analytics Event Taxonomy

**Last Updated:** December 31, 2025
**Version:** 1.0

## Overview

This document defines the standardized event taxonomy for TIP analytics. All analytics events should follow these naming conventions and property contracts to ensure consistency across the application.

## Event Naming Convention

- Use `snake_case` for event names
- Use past tense verbs (created, submitted, generated)
- Be specific and descriptive
- Prefix with category for related events

## Event Categories

### 1. Trip Lifecycle Events

| Event Name | Description | Required Properties |
|------------|-------------|---------------------|
| `trip_created` | User creates a new trip | destination_city, destination_country, trip_duration_days, travelers_count, trip_purposes, has_return_flight |
| `trip_updated` | User modifies an existing trip | trip_id, updated_fields |
| `trip_deleted` | User deletes a trip | trip_id |
| `trip_viewed` | User views trip details | trip_id |

### 2. Report Generation Events

| Event Name | Description | Required Properties |
|------------|-------------|---------------------|
| `report_generation_started` | Report generation begins | trip_id |
| `report_generated` | Report generation completes | trip_id, duration_ms, success, sections_count, error_code? |
| `report_generation_failed` | Report generation fails | trip_id, error_code, duration_ms |
| `report_section_viewed` | User views a report section | trip_id, section_type |

### 3. User Engagement Events

| Event Name | Description | Required Properties |
|------------|-------------|---------------------|
| `feedback_submitted` | User submits feedback | type (bug/feature), has_attachment, route |
| `share_link_created` | User creates a share link | trip_id, link_type |
| `template_saved` | User saves a trip template | trip_id, template_name |
| `template_used` | User creates trip from template | template_id |

### 4. Navigation Events

| Event Name | Description | Required Properties |
|------------|-------------|---------------------|
| `wizard_step_completed` | User completes a wizard step | step_number, step_name, total_steps |
| `wizard_abandoned` | User leaves wizard incomplete | step_number, step_name, total_steps |

### 5. Error Events

| Event Name | Description | Required Properties |
|------------|-------------|---------------------|
| `api_error` | API request fails | endpoint, status_code, error_code, request_id? |
| `client_error` | Client-side error occurs | error_name, error_message, context, url |

## Property Definitions

### Standard Properties (Auto-captured by PostHog)

- `$pageview` - Automatic page view tracking
- `$current_url` - Current page URL
- `$referrer` - Referrer URL
- `$device_type` - Device type (desktop/mobile/tablet)
- `$browser` - Browser name
- `$os` - Operating system

### Custom Properties

#### TripCreatedProperties
```typescript
interface TripCreatedProperties {
  destination_city: string;      // e.g., "Paris"
  destination_country: string;   // e.g., "France"
  trip_duration_days: number;    // e.g., 7
  travelers_count: number;       // e.g., 2
  trip_purposes: string[];       // e.g., ["leisure", "culture"]
  has_return_flight: boolean;    // true/false
}
```

#### ReportGeneratedProperties
```typescript
interface ReportGeneratedProperties {
  trip_id: string;               // UUID
  duration_ms: number;           // Generation time in ms
  success: boolean;              // true/false
  sections_count: number;        // Number of sections generated
  error_code?: string;           // Error code if failed
}
```

#### FeedbackSubmittedProperties
```typescript
interface FeedbackSubmittedProperties {
  type: 'bug' | 'feature';       // Feedback type
  has_attachment: boolean;       // Whether screenshot attached
  route: string;                 // Current route when submitted
}
```

#### WizardStepProperties
```typescript
interface WizardStepProperties {
  step_number: number;           // Current step (1-indexed)
  step_name: string;             // e.g., "destination"
  total_steps: number;           // Total wizard steps
}
```

#### ApiErrorProperties
```typescript
interface ApiErrorProperties {
  endpoint: string;              // API endpoint
  status_code: number;           // HTTP status code
  error_code: string;            // Application error code
  request_id?: string;           // Request ID for tracing
}
```

## Usage Examples

### Tracking Trip Creation
```typescript
import { trackTripCreated } from '@/lib/analytics';

trackTripCreated({
  destination_city: 'Paris',
  destination_country: 'France',
  trip_duration_days: 7,
  travelers_count: 2,
  trip_purposes: ['leisure', 'culture'],
  has_return_flight: true,
});
```

### Tracking Report Generation
```typescript
import { trackReportGenerated, trackReportGenerationStarted } from '@/lib/analytics';

// Start
trackReportGenerationStarted(tripId);

// Complete
trackReportGenerated({
  trip_id: tripId,
  duration_ms: 45000,
  success: true,
  sections_count: 10,
});
```

### Tracking Errors
```typescript
import { trackApiError, trackClientError } from '@/lib/analytics';

// API error
trackApiError({
  endpoint: '/api/trips',
  status_code: 500,
  error_code: 'INTERNAL_ERROR',
  request_id: 'req-123',
});

// Client error
trackClientError(error, 'TripWizard.handleSubmit');
```

## PII Handling

The analytics module automatically sanitizes sensitive data before sending to PostHog. The following fields are automatically removed:

- `email`
- `password`
- `token`
- `api_key`
- `phone`
- `address`
- `credit_card`
- `ssn`

Long string values (>500 characters) are automatically truncated.

## Dashboard Metrics

### Acquisition Dashboard
- New users (daily/weekly/monthly)
- Activation rate (users who create first trip)
- Source attribution

### Funnel Dashboard
- Landing → Sign up → Trip created → Report generated
- Drop-off points
- Conversion rates

### Reliability Dashboard
- Report success rate
- Average generation time
- Error occurrences by type

### Retention Dashboard
- D1, D7, D30 retention
- Return trip creation rate
- Active user segments

## Implementation Checklist

- [x] PostHog SDK integrated
- [x] Event constants defined
- [x] Type-safe capture functions
- [x] PII sanitization
- [x] User identification
- [ ] All events instrumented in UI
- [ ] Dashboards created in PostHog
- [ ] Alerts configured

## Changelog

### v1.0 (2025-12-31)
- Initial event taxonomy
- Core event definitions
- Property contracts defined
