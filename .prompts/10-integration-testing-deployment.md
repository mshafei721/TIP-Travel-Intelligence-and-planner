# Integration Testing & Deployment

> **Prerequisites**: All increments I1-I10 should be substantially complete

## Objective

Perform comprehensive integration testing, fix cross-feature bugs, and deploy to production.

---

## INTEGRATION TESTING CHECKLIST

### End-to-End User Flows

```
Flow 1: New User Onboarding
├── [ ] Sign up with email
├── [ ] Verify email
├── [ ] Complete traveler profile
├── [ ] Set preferences
└── [ ] View dashboard

Flow 2: Trip Creation & Report
├── [ ] Start trip wizard
├── [ ] Complete 4 steps
├── [ ] Submit trip
├── [ ] View generation progress
├── [ ] View completed report
├── [ ] All 9 sections display correctly
└── [ ] Actions work (share, export)

Flow 3: Itinerary Building
├── [ ] Open itinerary builder
├── [ ] Add activities
├── [ ] Drag and drop reorder
├── [ ] Map displays correctly
├── [ ] Save changes
└── [ ] Persist on reload

Flow 4: Collaboration
├── [ ] Generate share link
├── [ ] Access as guest
├── [ ] Invite collaborator
├── [ ] Collaborator can view/edit
├── [ ] Comments work
└── [ ] PDF export works

Flow 5: Trip Updates
├── [ ] Edit trip details
├── [ ] See affected sections
├── [ ] Confirm recalculation
├── [ ] Selective agents run
├── [ ] Report updates correctly
└── [ ] Version history saved

Flow 6: Templates & History
├── [ ] Save trip as template
├── [ ] Create trip from template
├── [ ] View travel history
├── [ ] See world map
├── [ ] Statistics accurate
└── [ ] Archive/unarchive works
```

---

## CROSS-FEATURE TESTING

### Authentication + All Features

```typescript
describe('Authentication Integration', () => {
  it('redirects to login when session expires')
  it('preserves form data on re-login')
  it('handles token refresh during long operations')
  it('shows correct user data across all pages')
})
```

### Dashboard + Trips + Reports

```typescript
describe('Dashboard Integration', () => {
  it('shows recent trips from trip list')
  it('shows upcoming trips correctly')
  it('updates when trip is created')
  it('shows correct statistics')
  it('recommendations reflect history')
})
```

### Agents + Report Display

```typescript
describe('Agent-Report Integration', () => {
  it('displays all 9 agent results')
  it('handles partial agent failure')
  it('shows confidence scores correctly')
  it('sources link correctly')
  it('recalculation updates display')
})
```

### API Rate Limiting & Errors

```typescript
describe('Error Handling', () => {
  it('handles API rate limits gracefully')
  it('shows user-friendly error messages')
  it('allows retry on transient errors')
  it('preserves state on network failure')
})
```

---

## PERFORMANCE TESTING

### Load Testing

```bash
# Using k6 or artillery
k6 run load-test.js

# Test scenarios:
# - 100 concurrent users creating trips
# - 50 concurrent report generations
# - 200 concurrent report views
```

### Performance Metrics

| Metric | Target | Test |
|--------|--------|------|
| Page Load (LCP) | < 2.5s | Lighthouse |
| Time to Interactive | < 3.5s | Lighthouse |
| API Response (p95) | < 500ms | k6 |
| Report Generation | < 60s | Manual |
| PDF Export | < 10s | Manual |

### Database Performance

```sql
-- Check slow queries
SELECT * FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Verify indexes are used
EXPLAIN ANALYZE SELECT * FROM trips WHERE user_id = '...';
```

---

## SECURITY TESTING

### Authentication Security

```
[ ] JWT tokens expire correctly
[ ] Refresh token rotation works
[ ] Session invalidation on password change
[ ] Rate limiting on login attempts
[ ] Secure password reset flow
```

### Authorization Security

```
[ ] RLS policies enforced
[ ] Users can only see own data
[ ] Collaborators have correct permissions
[ ] Public links don't expose private data
[ ] Admin endpoints protected
```

### Data Security

```
[ ] No sensitive data in logs
[ ] API keys not exposed to frontend
[ ] HTTPS enforced
[ ] CORS properly configured
[ ] SQL injection prevented
[ ] XSS prevented
```

---

## DEPLOYMENT CHECKLIST

### Pre-Deployment

```
[ ] All tests passing (>80% coverage)
[ ] No console errors in browser
[ ] No TypeScript errors
[ ] Linting passing
[ ] Build succeeds locally
[ ] Environment variables documented
```

### Vercel (Frontend)

```bash
# Environment variables to set:
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_API_URL=https://tip-backend.up.railway.app
NEXT_PUBLIC_MAPBOX_TOKEN=

# Deployment
vercel --prod
```

### Railway (Backend)

```bash
# Environment variables:
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
REDIS_URL=                    # From Railway Redis
ANTHROPIC_API_KEY=
CELERY_BROKER_URL=${REDIS_URL}
CELERY_RESULT_BACKEND=${REDIS_URL}
CORS_ORIGINS=https://tip.vercel.app

# Services to deploy:
# 1. Backend API
# 2. Celery Worker
# 3. Celery Beat (optional)
# 4. Redis (add-on)

railway up
```

### Supabase

```
[ ] Production project created
[ ] All migrations applied
[ ] RLS policies enabled
[ ] Edge functions deployed (if any)
[ ] Backups configured
[ ] Rate limits configured
```

---

## POST-DEPLOYMENT VERIFICATION

### Smoke Tests

```
[ ] Homepage loads
[ ] Can sign up new user
[ ] Can log in
[ ] Dashboard loads
[ ] Can create trip
[ ] Report generates
[ ] PDF exports
[ ] Share link works
```

### Monitoring Setup

```yaml
# Vercel Analytics
- Core Web Vitals tracking
- Error tracking

# Railway Metrics
- CPU/Memory usage
- Request latency
- Error rates

# Supabase Dashboard
- Query performance
- API usage
- Storage usage

# Uptime Monitoring (optional)
- Ping endpoints every 5 minutes
- Alert on downtime
```

### Logging

```python
# Backend logging configuration
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
        },
    },
    'loggers': {
        'app': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'celery': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    },
}
```

---

## ROLLBACK PLAN

### If Frontend Issues

```bash
# Vercel automatic rollback
vercel rollback [deployment-url]

# Or redeploy previous commit
git checkout [previous-commit]
vercel --prod
```

### If Backend Issues

```bash
# Railway rollback
railway rollback

# Or redeploy previous commit
git checkout [previous-commit]
railway up
```

### If Database Issues

```sql
-- Supabase point-in-time recovery
-- Contact support or use dashboard
```

---

## DOCUMENTATION UPDATES

### Update README

```markdown
## Production URLs

- **App**: https://tip.vercel.app
- **API**: https://tip-backend.up.railway.app
- **Docs**: https://tip.vercel.app/docs

## Local Development

```bash
# Clone and setup
git clone https://github.com/...
cp .env.example .env
# Add your API keys

# Start services
.\docker.ps1 up

# Frontend
cd frontend && npm run dev

# Backend
cd backend && uvicorn app.main:app --reload
```
```

### Update CLAUDE.md

```markdown
## Deployment

- Frontend: Vercel (auto-deploy from main)
- Backend: Railway (manual deploy)
- Database: Supabase (managed)
```

---

## FINAL CHECKLIST

### Before Launch

```
[ ] All E2E tests passing
[ ] Performance targets met
[ ] Security audit complete
[ ] Documentation updated
[ ] Error monitoring active
[ ] Backup configured
[ ] Rollback tested
```

### After Launch

```
[ ] Monitor error rates
[ ] Check performance metrics
[ ] Review user feedback
[ ] Fix critical bugs immediately
[ ] Plan iteration improvements
```

---

## DELIVERABLES

- [ ] All E2E tests written and passing
- [ ] Performance benchmarks documented
- [ ] Security checklist complete
- [ ] Production deployment successful
- [ ] Monitoring configured
- [ ] Documentation updated
- [ ] README with production URLs
- [ ] Rollback plan documented
