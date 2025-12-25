# I2 Integration Testing Checklist

**Date**: 2025-12-25
**Tester**: User
**Servers**: Backend (8000) ✅ | Frontend (3000) ✅

---

## 🎯 Test Objectives

1. Verify frontend-backend communication
2. Ensure data persistence in database
3. Validate user workflows end-to-end
4. Confirm error handling works correctly
5. Test all CRUD operations

---

## 📋 Pre-Testing Checklist

- [x] Backend server running on http://localhost:8000
- [x] Frontend server running on http://localhost:3000
- [x] Supabase database active (not paused)
- [ ] User account created in Supabase Auth
- [ ] User logged in to frontend

---

## 🧪 Test Suite 1: Authentication & Profile Loading

### Test 1.1: Login Flow
**Objective**: Verify user can log in and access profile

**Steps**:
1. Open http://localhost:3000/login
2. Log in with email/password or Google OAuth
3. Should redirect to /dashboard after login

**Expected Results**:
- [ ] Login successful
- [ ] Redirected to dashboard
- [ ] No console errors

**Actual Results**:
```
[Record your results here]
```

---

### Test 1.2: Profile Page Load
**Objective**: Verify profile page loads with user data

**Steps**:
1. Navigate to http://localhost:3000/profile
2. Wait for page to load completely
3. Check browser console for errors

**Expected Results**:
- [ ] Page loads without errors
- [ ] User email displayed correctly
- [ ] Display name shown (or empty if not set)
- [ ] All sections rendered (Profile, Traveler Details, etc.)
- [ ] No 401/403 errors in Network tab

**Actual Results**:
```
[Record your results here]
```

---

### Test 1.3: Backend API Call Verification
**Objective**: Verify frontend calls backend API correctly

**Steps**:
1. Open DevTools (F12) → Network tab
2. Refresh profile page
3. Look for API calls to localhost:8000

**Expected Results**:
- [ ] GET /api/profile returns 200 OK
- [ ] GET /api/profile/statistics returns 200 OK (if called)
- [ ] Response includes user data
- [ ] Response includes travelerProfile (or null)
- [ ] Authorization header present in requests

**Actual Results**:
```
[Record your results here]
```

**Screenshot Network Tab**:
```
[Paste screenshot or describe API calls]
```

---

## 🧪 Test Suite 2: Profile Information Updates

### Test 2.1: Update Display Name (Auto-Save)
**Objective**: Verify display name updates and saves automatically

**Steps**:
1. Go to http://localhost:3000/profile
2. Find "Name" field in Profile Information section
3. Type a new name: "Test User Integration"
4. Wait 2 seconds (auto-save delay)
5. Watch for "Saving..." → "Saved" indicator

**Expected Results**:
- [ ] Name field updates as you type
- [ ] "Saving..." indicator appears after 1.5 seconds
- [ ] "Saved" indicator appears after save completes
- [ ] No errors in console
- [ ] Network tab shows PUT /api/profile request
- [ ] PUT request returns 200 OK

**Actual Results**:
```
Name updated: Yes/No
Auto-save triggered: Yes/No
API call made: Yes/No
Errors: None/[Describe]
```

---

### Test 2.2: Verify Name Persistence
**Objective**: Confirm name change persists in database

**Steps**:
1. After updating name in Test 2.1, refresh the page (F5)
2. Check if new name is still displayed

**Expected Results**:
- [ ] Page reloads successfully
- [ ] New name "Test User Integration" is displayed
- [ ] Name persisted in database

**Actual Results**:
```
[Record your results here]
```

---

### Test 2.3: Check Database Directly
**Objective**: Verify data in Supabase

**Steps**:
1. Go to https://supabase.com/dashboard
2. Select project: bsfmmxjoxwbcsbpjkmcn
3. Go to Table Editor → user_profiles
4. Find your user row
5. Check display_name column

**Expected Results**:
- [ ] User row exists in user_profiles table
- [ ] display_name = "Test User Integration"
- [ ] updated_at timestamp is recent (last few minutes)

**Actual Results**:
```
display_name: [Value from database]
updated_at: [Timestamp]
```

---

## 🧪 Test Suite 3: Traveler Profile Updates

### Test 3.1: Create Traveler Profile (First Time)
**Objective**: Create traveler profile for user

**Steps**:
1. Go to http://localhost:3000/profile
2. Scroll to "Traveler Details" section
3. Fill in:
   - Nationality: Select "United States" (US)
   - Residence Country: Select "United States" (US)
   - Residency Status: Select "Citizen"
   - Date of Birth: Select a date (e.g., 1990-01-01)
4. Click outside fields or wait for auto-save

**Expected Results**:
- [ ] All fields accept input
- [ ] Country dropdowns work correctly
- [ ] Date picker works
- [ ] "Saving..." indicator appears
- [ ] "Saved" indicator appears
- [ ] Network tab shows PUT /api/profile/traveler
- [ ] Response returns 200 OK

**Actual Results**:
```
[Record your results here]
```

---

### Test 3.2: Update Traveler Profile
**Objective**: Update existing traveler profile

**Steps**:
1. Change Nationality to "United Kingdom" (GB)
2. Wait for auto-save
3. Refresh page
4. Verify nationality is "United Kingdom"

**Expected Results**:
- [ ] Update successful
- [ ] Data persists after refresh
- [ ] No duplicate traveler profiles created

**Actual Results**:
```
[Record your results here]
```

---

### Test 3.3: Traveler Profile in Database
**Objective**: Verify traveler profile in Supabase

**Steps**:
1. Supabase Dashboard → Table Editor → traveler_profiles
2. Find your user's row (matching user_id)
3. Check all fields

**Expected Results**:
- [ ] Row exists in traveler_profiles table
- [ ] nationality = "GB" (or your selection)
- [ ] residency_country = "US" (or your selection)
- [ ] residency_status = "citizen"
- [ ] date_of_birth matches your input
- [ ] user_id matches your user profile id

**Actual Results**:
```
[Paste database values]
```

---

## 🧪 Test Suite 4: Travel Preferences

### Test 4.1: Update Travel Style
**Objective**: Update travel preferences

**Steps**:
1. Go to "Travel Preferences" section
2. Select Travel Style: "Luxury"
3. Add Dietary Restrictions: Check "Vegetarian"
4. Wait for auto-save

**Expected Results**:
- [ ] Travel style updates
- [ ] Dietary restrictions checkboxes work
- [ ] Data saves successfully
- [ ] PUT /api/profile/traveler called

**Actual Results**:
```
[Record your results here]
```

---

### Test 4.2: Preferences Persistence
**Objective**: Verify preferences persist

**Steps**:
1. Refresh page
2. Check if "Luxury" is still selected
3. Check if "Vegetarian" is still checked

**Expected Results**:
- [ ] Travel style = "Luxury"
- [ ] Dietary restrictions include "Vegetarian"

**Actual Results**:
```
[Record your results here]
```

---

## 🧪 Test Suite 5: Notification Preferences

### Test 5.1: Update Notification Settings
**Objective**: Change notification preferences

**Steps**:
1. Go to "Notifications" section
2. Toggle "Email notifications for trip reports" ON
3. Toggle "Product updates and announcements" OFF
4. Wait for save indicator

**Expected Results**:
- [ ] Toggles switch correctly
- [ ] Auto-save triggers
- [ ] PUT /api/profile/preferences called
- [ ] Response 200 OK

**Actual Results**:
```
[Record your results here]
```

---

### Test 5.2: Preferences in Database
**Objective**: Verify preferences JSONB field

**Steps**:
1. Supabase Dashboard → user_profiles table
2. Find your row
3. Expand "preferences" JSONB column

**Expected Results**:
- [ ] preferences.email_notifications = true
- [ ] preferences.marketing_emails = false
- [ ] preferences object is valid JSON

**Actual Results**:
```
preferences JSON:
{
  "email_notifications": [value],
  "marketing_emails": [value],
  ...
}
```

---

## 🧪 Test Suite 6: Error Handling & Validation

### Test 6.1: Invalid Country Code (Backend Validation)
**Objective**: Test backend validation

**Steps**:
1. Open DevTools → Console
2. In Console, run:
```javascript
fetch('http://localhost:8000/api/profile/traveler', {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + localStorage.getItem('sb-bsfmmxjoxwbcsbpjkmcn-auth-token').split('"access_token":"')[1].split('"')[0]
  },
  body: JSON.stringify({ nationality: 'USA' }) // Invalid: must be 2 letters
}).then(r => r.json()).then(console.log)
```

**Expected Results**:
- [ ] Response status: 422 Unprocessable Entity
- [ ] Error message mentions country code validation
- [ ] Frontend shows error (if UI handles it)

**Actual Results**:
```
[Paste API response]
```

---

### Test 6.2: Unauthenticated Request
**Objective**: Verify authentication required

**Steps**:
1. Open Incognito/Private window
2. Try to access: http://localhost:8000/api/profile
3. Check response

**Expected Results**:
- [ ] Response status: 401 Unauthorized
- [ ] Error message about missing/invalid token
- [ ] Frontend redirects to login (if accessed via frontend)

**Actual Results**:
```
[Record your results here]
```

---

### Test 6.3: Network Error Handling
**Objective**: Test frontend handles backend errors gracefully

**Steps**:
1. Stop backend server (Ctrl+C in backend terminal)
2. Try to update profile on frontend
3. Observe behavior

**Expected Results**:
- [ ] Frontend shows error message
- [ ] Error message is user-friendly (not raw error)
- [ ] No app crash
- [ ] User can retry

**Actual Results**:
```
[Record your results here]
```

---

## 🧪 Test Suite 7: Account Deletion (⚠️ Use Test Account!)

### Test 7.1: Account Deletion with Wrong Confirmation
**Objective**: Verify deletion requires correct confirmation

**Steps**:
1. Go to "Account" section at bottom of profile page
2. Click "Delete Account" button
3. In modal, type "DELETE MY ACCOUN" (wrong text)
4. Click confirm

**Expected Results**:
- [ ] Deletion blocked
- [ ] Error message shown
- [ ] Account NOT deleted

**Actual Results**:
```
[Record your results here]
```

---

### Test 7.2: Account Deletion with Correct Confirmation (⚠️ Test Account Only!)
**Objective**: Verify account deletion works

**Steps**:
1. Click "Delete Account"
2. Type "DELETE MY ACCOUNT" exactly
3. Click confirm

**Expected Results**:
- [ ] Account deleted
- [ ] User logged out
- [ ] Redirected to signup page
- [ ] User row removed from database (or marked deleted)

**Actual Results**:
```
[Record your results here]
```

**⚠️ WARNING**: Only test this with a test account you don't need!

---

## 🧪 Test Suite 8: Photo Upload (Requires Supabase Storage Setup)

### Test 8.1: Upload Profile Photo
**Objective**: Test photo upload to Supabase Storage

**Steps**:
1. Go to Profile Information section
2. Click on profile photo placeholder
3. Select an image file (< 5MB)
4. Wait for upload

**Expected Results**:
- [ ] File picker opens
- [ ] Upload progress indicator shown
- [ ] Photo appears after upload
- [ ] avatar_url updated in database
- [ ] Photo accessible at public URL

**Actual Results**:
```
Upload successful: Yes/No
Photo URL: [URL from database]
Errors: [Any errors]
```

**Note**: Requires 'profile-photos' bucket in Supabase Storage

---

## 📊 Test Results Summary

### Test Execution Overview

| Test Suite | Total Tests | Passed | Failed | Skipped |
|------------|-------------|--------|--------|---------|
| Suite 1: Auth & Loading | 3 | [ ] | [ ] | [ ] |
| Suite 2: Profile Updates | 3 | [ ] | [ ] | [ ] |
| Suite 3: Traveler Profile | 3 | [ ] | [ ] | [ ] |
| Suite 4: Travel Preferences | 2 | [ ] | [ ] | [ ] |
| Suite 5: Notifications | 2 | [ ] | [ ] | [ ] |
| Suite 6: Error Handling | 3 | [ ] | [ ] | [ ] |
| Suite 7: Account Deletion | 2 | [ ] | [ ] | [ ] |
| Suite 8: Photo Upload | 1 | [ ] | [ ] | [ ] |
| **TOTAL** | **19** | **[ ]** | **[ ]** | **[ ]** |

---

## 🐛 Issues Found

### Issue 1
**Description**:
**Severity**: Critical/High/Medium/Low
**Steps to Reproduce**:
**Expected Behavior**:
**Actual Behavior**:
**Screenshots**:
**Proposed Fix**:

### Issue 2
[Add more as needed]

---

## ✅ Sign-Off

**Tester**: ___________________
**Date**: ___________________
**Overall Status**: Pass / Fail / Partial
**Ready for Production**: Yes / No / With Fixes

**Notes**:
```
[Additional notes, observations, recommendations]
```

---

## 📝 Next Steps

Based on test results:

1. **If All Tests Pass**:
   - Mark I2 as 100% complete
   - Update documentation
   - Prepare for production deployment
   - Move to next increment (I3 or I4)

2. **If Issues Found**:
   - Create bug tickets for each issue
   - Prioritize fixes (Critical → High → Medium → Low)
   - Re-test after fixes
   - Update test results

3. **Production Readiness**:
   - Deploy backend to Railway/Render
   - Deploy frontend to Vercel
   - Run smoke tests in production
   - Monitor for errors

---

**Last Updated**: 2025-12-25
**Document Version**: 1.0
