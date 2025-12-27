# TIP Rollback Playbook

> **Last Updated**: 2025-12-27
> **Owner**: DevOps Team
> **Status**: Active

---

## Overview

This playbook documents the rollback procedures for TIP (Travel Intelligence & Planner) across all deployment targets: Vercel (frontend), Railway (backend), and Supabase (database).

---

## 1. Frontend Rollback (Vercel)

### Instant Rollback (< 1 minute)

Vercel maintains deployment history allowing instant rollback to any previous deployment.

#### Steps:

1. **Access Vercel Dashboard**
   - URL: https://vercel.com/mohammed-elshafeis-projects/tip-travel-intelligence-and-planner
   - Navigate to "Deployments" tab

2. **Find the Target Deployment**
   - Locate the last known working deployment
   - Look for green checkmark status
   - Note the deployment time and commit hash

3. **Execute Rollback**
   - Click the three-dot menu (⋮) on the target deployment
   - Select "Promote to Production"
   - Confirm the action

4. **Verify Rollback**
   ```bash
   # Test the production URL
   curl -I https://tip-travel-intelligence-and-planner.vercel.app

   # Check response headers for deployment ID
   # Should match the promoted deployment
   ```

### Rollback via CLI

```bash
# Install Vercel CLI if not present
npm i -g vercel

# Login
vercel login

# List deployments
vercel ls tip-travel-intelligence-and-planner

# Promote specific deployment to production
vercel promote [deployment-url] --yes
```

---

## 2. Backend Rollback (Railway)

### Via Railway Dashboard (< 2 minutes)

1. **Access Railway Dashboard**
   - URL: https://railway.app/project/[project-id]
   - Navigate to the "TIP-Travel-Intelligence-and-planner" service

2. **View Deployments**
   - Click on "Deployments" tab
   - Find the last stable deployment

3. **Rollback**
   - Click the target deployment
   - Select "Redeploy" or use "Rollback" option

4. **Verify**
   ```bash
   # Check health endpoint
   curl https://tip-travel-intelligence-and-planner-production.up.railway.app/api/health

   # Expected response: {"status": "healthy", ...}
   ```

### Via Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# View deployment history
railway logs --deployment [deployment-id]

# Rollback to previous deployment
railway redeploy --deployment [deployment-id]
```

---

## 3. Database Rollback (Supabase)

### Migration Rollback

#### Option A: Forward-Fix (Recommended)

Create a new migration that reverses the problematic changes:

```bash
# Connect to database
psql $DATABASE_URL

# Create reversal migration
-- Example: If migration added a column
ALTER TABLE trips DROP COLUMN IF EXISTS new_column;
```

#### Option B: Point-in-Time Recovery (Pro Plan)

1. **Access Supabase Dashboard**
   - URL: https://supabase.com/dashboard/project/bsfmmxjoxwbcsbpjkmcn
   - Navigate to "Database" → "Backups"

2. **Select Recovery Point**
   - Choose timestamp before the incident
   - Note: This restores to a NEW database, not in-place

3. **Execute Recovery**
   - Click "Restore"
   - Wait for new database to be provisioned
   - Update connection strings in Railway

#### Option C: Manual Data Restore

If you have SQL dumps:

```bash
# Restore from SQL dump
psql $DATABASE_URL < backup_YYYYMMDD.sql

# Verify row counts
psql $DATABASE_URL -c "SELECT 'trips' as table, COUNT(*) FROM trips UNION ALL SELECT 'user_profiles', COUNT(*) FROM user_profiles;"
```

---

## 4. Full Stack Rollback Procedure

When rolling back all components together:

### Order of Operations

1. **Stop traffic** (optional - for critical issues)
   - Enable Vercel maintenance mode or redirect

2. **Rollback Backend FIRST**
   - Ensures API compatibility
   - Railway deployment rollback

3. **Rollback Database** (if needed)
   - Only if data migration caused issues
   - Use forward-fix when possible

4. **Rollback Frontend LAST**
   - Vercel instant rollback
   - Verify against rolled-back backend

5. **Verify full stack**
   ```bash
   # Health check
   curl https://tip-travel-intelligence-and-planner-production.up.railway.app/api/health

   # Frontend loads
   curl -I https://tip-travel-intelligence-and-planner.vercel.app

   # Test critical flow
   # (manual test of login + trip creation)
   ```

---

## 5. Rollback Decision Matrix

| Symptom | Component | Action |
|---------|-----------|--------|
| 500 errors on API | Backend | Rollback Railway |
| UI not loading | Frontend | Rollback Vercel |
| Data corruption | Database | PITR or forward-fix |
| Auth failures | Backend + Supabase | Check JWT config, then rollback |
| Performance degradation | Backend | Rollback, then investigate |

---

## 6. Communication Template

When executing rollback, notify stakeholders:

```
INCIDENT: [Brief Description]
STATUS: Rollback in progress
IMPACT: [Description of user impact]
ETA: [Expected resolution time]

ACTIONS TAKEN:
- [Timestamp] Identified issue in [component]
- [Timestamp] Initiated rollback to [version/deployment]
- [Timestamp] Rollback complete, verifying

NEXT STEPS:
- Monitor for 15 minutes
- Conduct post-incident review
```

---

## 7. Post-Rollback Checklist

- [ ] Verify all health endpoints responding
- [ ] Test critical user flow (login → create trip → view report)
- [ ] Check error rates in logs (Railway, Vercel)
- [ ] Notify stakeholders of resolution
- [ ] Schedule post-incident review
- [ ] Document root cause in incident log
- [ ] Create fix for forward deployment

---

## 8. Emergency Contacts

| Role | Name | Contact |
|------|------|---------|
| DevOps Lead | TBD | TBD |
| Backend Lead | TBD | TBD |
| Frontend Lead | TBD | TBD |
| On-call | TBD | TBD |

---

## 9. Related Documents

- [Backup/Restore Drill Log](./backup-drill-log.md)
- [Incident Response Runbook](./incident-response.md)
- [Monitoring Dashboard](https://railway.app/project/[id]/metrics)

---

*This playbook should be reviewed and updated after each incident.*
