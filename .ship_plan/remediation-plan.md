# TIP Go-Live Remediation Plan

> **Status**: NO-SHIP → Targeting SHIP-READY
> **Created**: 2025-12-27
> **Estimated Time to Complete**: 3-5 days

---

## 🚨 PHASE 1: CRITICAL BLOCKERS (Day 1 - Immediate)

### 1.1 BLOCKER: Remove Service Role Key from Frontend

**Risk Level**: 🔴 CRITICAL
**Impact**: Full database bypass - attackers can read/write/delete ALL data
**Location**: `frontend/.env.local:12`

#### What Claude Will Do (Automated):
1. Remove `SUPABASE_SERVICE_ROLE_KEY` from `frontend/.env.local`
2. Update `frontend/.env.example` to remove any reference
3. Add the key to `.gitignore` patterns

#### What User Must Do (Manual):
1. **Rotate the exposed key immediately** in Supabase Dashboard:
   - Go to: https://supabase.com/dashboard/project/bsfmmxjoxwbcsbpjkmcn/settings/api
   - Click "Rotate" on the service_role key
   - Copy the new key

2. **Update Railway environment variables**:
   - Go to: Railway Dashboard → TIP project → Variables
   - Update `SUPABASE_SERVICE_ROLE_KEY` with the new rotated key

3. **Verify the old key is invalidated**:
   ```bash
   # This should fail after rotation
   curl -X GET "https://bsfmmxjoxwbcsbpjkmcn.supabase.co/rest/v1/trips" \
     -H "apikey: OLD_SERVICE_ROLE_KEY" \
     -H "Authorization: Bearer OLD_SERVICE_ROLE_KEY"
   ```

#### Verification:
```bash
# Should NOT find any service role key in frontend
grep -r "SUPABASE_SERVICE_ROLE_KEY" frontend/
```

---

### 1.2 HIGH: Enable Leaked Password Protection

**Risk Level**: 🟠 HIGH
**Impact**: Users can set passwords found in data breaches

#### What User Must Do (Manual):
1. Go to: https://supabase.com/dashboard/project/bsfmmxjoxwbcsbpjkmcn/settings/auth
2. Scroll to "Security" section
3. Enable "Leaked password protection"
4. Click "Save"

#### Verification:
- Try signing up with password "password123" - should be rejected

---

### 1.3 HIGH: Make CI Blocking on Failures

**Risk Level**: 🟠 HIGH
**Impact**: Broken code can be merged to main

#### What Claude Will Do (Automated):
1. Remove `continue-on-error: true` from lint job (lines 50, 56)
2. Remove `continue-on-error: true` from typecheck job (line 194)
3. Keep security scan upload continue-on-error (permissions issue)

#### Verification:
```bash
# CI should fail on lint errors
grep "continue-on-error" .github/workflows/backend-ci.yml
# Should only show security upload line
```

---

### 1.4 HIGH: Create Rollback Playbook

**Risk Level**: 🟠 HIGH
**Impact**: No documented recovery procedure

#### What Claude Will Do (Automated):
Create `docs/runbooks/rollback-playbook.md` with:
- Vercel instant rollback procedure
- Railway deploy rollback steps
- Database migration rollback strategy

---

## 🟡 PHASE 2: HIGH PRIORITY (Days 2-3)

### 2.1 HIGH: Implement Load Tests

**Risk Level**: 🟠 HIGH
**Target**: p95 < 300ms at 100 VUs

#### What Claude Will Do (Automated):
1. Create `tests/load/k6-config.js` with load test scenarios
2. Add load test scripts for:
   - `/api/health` - Health check baseline
   - `/api/trips` - Trip CRUD operations
   - `/api/profile` - Profile operations

#### What User Must Do (Manual):
1. Install k6: https://k6.io/docs/get-started/installation/
2. Run load tests:
   ```bash
   k6 run tests/load/k6-config.js --vus 100 --duration 5m
   ```
3. Verify p95 < 300ms

---

### 2.2 HIGH: Backup/Restore Drill

**Risk Level**: 🟠 HIGH
**Impact**: No proven recovery capability

#### What User Must Do (Manual):

**Step 1: Create Test Data**
```sql
-- Run in Supabase SQL Editor
INSERT INTO trips (user_id, title, status, destinations)
VALUES ('test-user-id', 'BACKUP_TEST_TRIP', 'draft', ARRAY['test-destination']);
```

**Step 2: Note Current State**
```sql
SELECT COUNT(*) as trip_count FROM trips;
SELECT COUNT(*) as profile_count FROM user_profiles;
```

**Step 3: Create Manual Backup (if on Pro plan)**
- Go to: Supabase Dashboard → Database → Backups
- Click "Create backup"
- Wait for completion

**Step 4: Test Restore (on staging project)**
- Create new Supabase project for testing
- Restore backup to new project
- Verify row counts match

**Step 5: Document Results**
Create `docs/runbooks/backup-drill-log.md`:
```markdown
# Backup/Restore Drill Log

- **Date**: YYYY-MM-DD
- **Performed by**: [Name]
- **Backup size**: XX MB
- **Restore time**: XX minutes
- **Row count verification**: ✅ Passed
```

---

### 2.3 HIGH: Increase Test Coverage to 80%

**Risk Level**: 🟠 HIGH
**Current**: 10% → **Target**: 80%

#### What Claude Will Do (Automated):
1. Identify uncovered code paths
2. Add unit tests for critical functions
3. Update CI to require 80% coverage

---

## 🟢 PHASE 3: MEDIUM PRIORITY (Days 4-5)

### 3.1 Implement E2E Tests

**What Claude Will Do**:
1. Set up Playwright configuration
2. Create E2E tests for 5 critical flows:
   - Login/Signup
   - Trip Creation
   - Report Generation
   - Profile Update
   - Trip Sharing

---

### 3.2 Consolidate RLS Policies

**What Claude Will Do**:
1. Review overlapping policies on:
   - `share_links`
   - `trip_collaborators`
   - `trip_comments`
   - `trip_templates`
2. Merge redundant policies

---

## 📋 USER ACTION CHECKLIST

### Immediate Actions (Complete Today)

- [ ] **1. Rotate Supabase Service Role Key**
  - Dashboard: https://supabase.com/dashboard/project/bsfmmxjoxwbcsbpjkmcn/settings/api
  - Click "Rotate" on service_role key
  - Copy new key

- [ ] **2. Update Railway with New Key**
  - Railway Dashboard → Variables → SUPABASE_SERVICE_ROLE_KEY
  - Paste new rotated key
  - Redeploy backend

- [ ] **3. Enable Leaked Password Protection**
  - Dashboard: https://supabase.com/dashboard/project/bsfmmxjoxwbcsbpjkmcn/settings/auth
  - Enable "Leaked password protection"
  - Save

- [ ] **4. Rotate Mapbox Token** (also exposed)
  - Dashboard: https://account.mapbox.com/
  - Rotate the sk.* token in frontend/.env.local
  - Update in Vercel environment variables

### Before Soft Launch (Within 3 Days)

- [ ] **5. Run Load Tests**
  - Install k6
  - Run `k6 run tests/load/k6-config.js`
  - Verify p95 < 300ms

- [ ] **6. Complete Backup Drill**
  - Follow steps in section 2.2
  - Document results

- [ ] **7. Review Rollback Playbook**
  - Read `docs/runbooks/rollback-playbook.md`
  - Practice Vercel rollback
  - Practice Railway rollback

### Optional Configurations

- [ ] **8. Set up Sentry DSN**
  - Create Sentry project at https://sentry.io
  - Add DSN to Railway and Vercel environment variables

- [ ] **9. Configure Google OAuth** (if needed)
  - Create OAuth credentials in Google Cloud Console
  - Add to Supabase Auth providers

---

## 🔍 VERIFICATION COMMANDS

### Check Service Role Key Removed
```powershell
# Should return NO results
Select-String -Path "frontend\*" -Pattern "SUPABASE_SERVICE_ROLE_KEY" -Recurse
```

### Check CI Configuration
```powershell
# Should show only 1 continue-on-error (security upload)
Select-String -Path ".github\workflows\backend-ci.yml" -Pattern "continue-on-error"
```

### Test Health Endpoint
```powershell
Invoke-RestMethod -Uri "https://tip-travel-intelligence-and-planner-production.up.railway.app/api/health"
```

---

## 📊 PROGRESS TRACKING

| Phase | Item | Status | Owner | Due Date |
|-------|------|--------|-------|----------|
| 1 | Remove service role key | ⏳ Pending | Claude | Day 1 |
| 1 | User rotates key | ⏳ Pending | User | Day 1 |
| 1 | Enable leaked password protection | ⏳ Pending | User | Day 1 |
| 1 | Make CI blocking | ⏳ Pending | Claude | Day 1 |
| 1 | Create rollback playbook | ⏳ Pending | Claude | Day 1 |
| 2 | Implement load tests | ⏳ Pending | Claude | Day 2 |
| 2 | Backup/restore drill | ⏳ Pending | User | Day 2 |
| 2 | Increase test coverage | ⏳ Pending | Claude | Day 3 |
| 3 | E2E tests | ⏳ Pending | Claude | Day 4 |
| 3 | Consolidate RLS | ⏳ Pending | Claude | Day 5 |

---

## 🎯 SUCCESS CRITERIA

Ship decision changes from NO-SHIP to SHIP when:

1. ✅ Service role key removed from frontend AND rotated
2. ✅ Leaked password protection enabled
3. ✅ CI blocks on lint/type failures
4. ✅ Rollback playbook created and tested
5. ✅ Load tests prove p95 < 300ms at 100 VUs
6. ✅ Backup/restore drill completed with documentation

---

## 📞 ESCALATION

If blocked on any step:
1. Check `docs/runbooks/` for troubleshooting
2. Review Railway/Vercel/Supabase logs
3. Contact project owner

---

*Generated by Claude Opus 4.5 | 2025-12-27*
