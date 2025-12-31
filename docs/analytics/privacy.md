# TIP Analytics Privacy & Governance Guide

**Last Updated:** December 31, 2025
**Version:** 1.0

## Overview

This document outlines the privacy controls, data governance practices, and compliance measures for TIP's analytics and error tracking systems.

## Services Used

| Service | Purpose | Data Sent | Compliance |
|---------|---------|-----------|------------|
| PostHog | Product Analytics | Events, Properties, User IDs | SOC 2 Type II, GDPR, HIPAA |
| Sentry | Error Tracking | Errors, Stack Traces, Context | SOC 2, GDPR |

## PII Handling

### Data We DO NOT Collect

The following data is **automatically removed** before being sent to analytics:

- Email addresses
- Passwords or tokens
- API keys
- Phone numbers
- Physical addresses
- Credit card information
- Social Security numbers
- Full names (in free-form text)

### Data We DO Collect

**PostHog Events:**
- Anonymized user IDs (UUID)
- Event names and properties
- Page views and navigation paths
- Device type, browser, OS
- Aggregated metrics (counts, durations)

**Sentry Errors:**
- Error messages and stack traces
- Request paths (not query parameters)
- Browser and device information
- Application version/release
- User ID (for error correlation only)

## Sanitization Implementation

### Frontend (TypeScript)

Location: `frontend/lib/analytics/events.ts`

```typescript
const sensitiveKeys = [
  'email', 'password', 'token', 'api_key',
  'phone', 'address', 'credit_card', 'ssn'
];

// Automatic sanitization before capture
function sanitizeProperties(props) {
  for (const key of Object.keys(props)) {
    if (sensitiveKeys.some(s => key.toLowerCase().includes(s))) {
      delete props[key];
    }
    // Truncate long strings
    if (typeof props[key] === 'string' && props[key].length > 500) {
      props[key] = props[key].substring(0, 500) + '...';
    }
  }
  return props;
}
```

### Backend (Python)

Location: `backend/app/core/sentry.py`

```python
# Headers automatically scrubbed
SENSITIVE_HEADERS = ['authorization', 'cookie', 'x-api-key']

def before_send(event, hint):
    # Remove sensitive data
    if 'request' in event:
        headers = event['request'].get('headers', {})
        for header in SENSITIVE_HEADERS:
            headers.pop(header, None)
    return event
```

## Sampling Rates

### Production Defaults

| Metric | Rate | Rationale |
|--------|------|-----------|
| Sentry Errors | 100% | All errors captured |
| Sentry Traces | 10% | Performance sampling |
| Sentry Profiles | 10% | Performance profiling |
| PostHog Events | 100% | All events captured |
| PostHog Replays | 10% normal, 100% on error | Debugging priority |

### Development Defaults

| Metric | Rate | Rationale |
|--------|------|-----------|
| All Analytics | 100% | Full visibility for testing |
| Session Replay | Disabled | Not needed locally |

## User Consent

### Consent Types

TIP tracks the following consent types (stored in `user_consent` table):

| Type | Required | Description |
|------|----------|-------------|
| `terms_of_service` | Yes | Agreement to ToS |
| `privacy_policy` | Yes | Agreement to Privacy Policy |
| `data_processing` | Yes | GDPR Article 6 consent |
| `analytics` | No | Product analytics opt-in |
| `marketing` | No | Marketing communications |

### Implementation

Users can manage consent via:
- Settings page: `/settings`
- API endpoint: `PUT /api/profile/consent`
- Email unsubscribe links

### Opt-Out Handling

When a user opts out of analytics:

1. PostHog: `posthog.opt_out_capturing()`
2. Sentry: Feedback widget disabled
3. Server: No analytics events sent for that user

## Data Retention

| Data Type | Retention Period | Deletion Method |
|-----------|-----------------|-----------------|
| Analytics Events | 12 months | Auto-expire in PostHog |
| Error Events | 90 days | Auto-expire in Sentry |
| Session Replays | 30 days | Auto-expire |
| Audit Logs | 3 years | Compliance requirement |

## Access Controls

### PostHog Access

- View-only: All team members
- Admin: Engineering leads only
- Dashboard creation: Product + Engineering

### Sentry Access

- Alert routing: Engineering team
- Issue assignment: By area ownership
- Admin: Platform team only

## GDPR Compliance

### Right to Access (Article 15)

Users can request their analytics data via:
- API: `GET /api/profile/data-export`
- Includes: PostHog events, Sentry errors linked to their ID

### Right to Erasure (Article 17)

When a user deletes their account:
1. PostHog: `posthog.reset()` clears local data
2. Backend: User ID removed from future events
3. Historical data: Anonymized (ID replaced with hash)

### Data Portability (Article 20)

Export includes:
- All trip data
- Profile information
- Consent history
- (Analytics data available via PostHog export on request)

## Cost Management

### Monthly Limits (Free Tier)

| Service | Limit | Current Usage |
|---------|-------|---------------|
| PostHog | 1M events | Monitor weekly |
| Sentry | 5K errors | Alert at 80% |

### Cost Reduction Strategies

1. **Event Sampling**: Reduce `tracesSampleRate` if costs rise
2. **Replay Limits**: Only capture on errors
3. **Log Levels**: Filter INFO breadcrumbs in Sentry
4. **Client-side Dedup**: Prevent duplicate error reports

## Alert Configuration

### Sentry Alerts

| Alert | Condition | Action |
|-------|-----------|--------|
| Error Spike | >2x baseline in 30 min | Page on-call |
| New Issue | First occurrence | Slack #errors |
| Regression | Resolved issue recurs | Email team |

### PostHog Alerts

| Alert | Condition | Action |
|-------|-----------|--------|
| Funnel Drop | >20% drop in trip creation | Email product |
| Error Rate | >5% API errors | Slack #alerts |

## Audit Trail

All analytics configuration changes are logged:

- Who made the change
- What was changed
- When it occurred
- Reason (if provided)

Audit logs available in: `admin/audit-logs`

## Review Schedule

| Review Type | Frequency | Owner |
|-------------|-----------|-------|
| Privacy Audit | Quarterly | Legal + Engineering |
| Cost Review | Monthly | Platform Team |
| Data Minimization | Bi-annually | Security Team |
| Consent Flow | Annually | Product + Legal |

## Contact

- Privacy Officer: dpo@tip-travel.com
- Security Team: security@tip-travel.com
- Platform Team: platform@tip-travel.com

## Changelog

### v1.0 (2025-12-31)
- Initial privacy governance document
- Defined PII handling
- Set sampling rates
- Established retention policies
