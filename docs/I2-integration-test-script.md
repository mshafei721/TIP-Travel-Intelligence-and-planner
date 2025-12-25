# I2 Integration Test - Quick Start Guide

**Status**: Both servers running ✅
**Backend**: http://localhost:8000
**Frontend**: http://localhost:3000

---

## 🚀 Quick Testing Steps (5 minutes)

### Option 1: Using Swagger UI (Easiest)

1. **Open Swagger UI**:
   ```
   http://localhost:8000/api/docs
   ```

2. **Get Your JWT Token**:
   - Open http://localhost:3000/login
   - Log in with your account
   - Open DevTools (F12) → Console
   - Run this command:
   ```javascript
   JSON.parse(localStorage.getItem('sb-bsfmmxjoxwbcsbpjkmcn-auth-token')).access_token
   ```
   - Copy the token (long string)

3. **Authorize in Swagger**:
   - Click "Authorize" button (lock icon, top right)
   - Paste your token (no "Bearer" prefix)
   - Click "Authorize" → "Close"

4. **Test Endpoints** (click each one):
   - ✅ GET /api/profile - Click "Try it out" → "Execute"
     - Should return 200 with your profile data

   - ✅ PUT /api/profile - Click "Try it out"
     - Edit body: `{"display_name": "Integration Test User"}`
     - Click "Execute"
     - Should return 200 with updated profile

   - ✅ GET /api/profile/statistics
     - Should return 200 with trip statistics

   - ✅ PUT /api/profile/traveler
     - Edit body: `{"nationality": "US"}`
     - Should return 200 with traveler profile

---

### Option 2: Using Frontend UI

1. **Go to Profile Page**:
   ```
   http://localhost:3000/profile
   ```

2. **Test Updates** (each should auto-save):
   - Change your display name
   - Update traveler nationality
   - Toggle notification settings

3. **Verify Persistence**:
   - Refresh page (F5)
   - Check if changes are still there

4. **Check Database**:
   - Go to https://supabase.com/dashboard
   - Select project: bsfmmxjoxwbcsbpjkmcn
   - Table Editor → user_profiles
   - Verify your changes are saved

---

## ✅ Success Criteria

**All Green** means integration is working:

- [ ] Backend health check returns "healthy"
- [ ] Frontend loads without errors
- [ ] Can log in successfully
- [ ] Profile page displays user data
- [ ] Display name update saves and persists
- [ ] Traveler profile creates/updates successfully
- [ ] Notification preferences save correctly
- [ ] All changes visible in Supabase database

---

## 🐛 If Something Doesn't Work

**Backend Not Responding**:
```bash
# Restart backend
cd backend
python -m uvicorn app.main:app --reload
```

**Frontend Not Loading**:
```bash
# Restart frontend
cd frontend
npm run dev
```

**401 Unauthorized Errors**:
- Token expired - log out and log in again
- Token not sent - check Authorization header in Network tab

**422 Validation Errors**:
- Check request body format
- Country codes must be 2-letter uppercase (US, GB, FR)
- Currency codes must be 3-letter uppercase (USD, EUR, GBP)

---

## 📊 Quick Test Results

After testing, fill this out:

**Backend API**: Working ✅ / Issues ❌
**Frontend UI**: Working ✅ / Issues ❌
**Data Persistence**: Working ✅ / Issues ❌
**Overall Integration**: Pass ✅ / Fail ❌

**Issues Found**:
```
[List any issues here]
```

---

**Time Required**: 5-10 minutes
**Difficulty**: Easy (using Swagger UI)
**Next**: Full testing checklist in I2-integration-testing-checklist.md
