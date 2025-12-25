# I2 Backend API Testing Guide

**Date**: 2025-12-25
**Status**: Backend Running ✅ | Ready for Testing
**Server**: http://localhost:8000

---

## ✅ Backend Server Status

**Running**: ✅ Yes
**Health Check**: http://localhost:8000/api/health
```json
{
  "status": "healthy",
  "timestamp": "2025-12-25T04:56:25.185872",
  "environment": "development",
  "version": "1.0.0",
  "service": "TIP"
}
```

---

## 🎯 Testing with Swagger UI (Recommended)

### Step 1: Open Swagger UI

Open in your browser:
```
http://localhost:8000/api/docs
```

This provides an interactive API testing interface - no curl or Postman needed!

---

### Step 2: Get Authentication Token

**You need a JWT token from Supabase to test profile endpoints.**

**Option A: Get Token from Frontend (Easiest)**
1. Start the frontend: `cd frontend && npm run dev`
2. Log in to your account at http://localhost:3000/login
3. Open browser DevTools (F12) → Application → Local Storage
4. Find: `sb-bsfmmxjoxwbcsbpjkmcn-auth-token`
5. Copy the `access_token` value

**Option B: Get Token from Supabase Dashboard**
1. Go to https://supabase.com/dashboard
2. Select project: bsfmmxjoxwbcsbpjkmcn
3. Go to Authentication → Users
4. Find your user and copy the JWT token

---

### Step 3: Authorize in Swagger UI

1. In Swagger UI, click the **"Authorize"** button (top right, lock icon)
2. In the "bearerAuth" field, paste your JWT token (just the token, no "Bearer" prefix)
3. Click "Authorize"
4. Click "Close"

Now all your requests will include the Authorization header automatically!

---

## 📝 Testing Profile Endpoints

### 1. GET /api/profile

**Purpose**: Get complete user profile (user_profile + traveler_profile)

**Steps in Swagger UI**:
1. Expand "GET /api/profile"
2. Click "Try it out"
3. Click "Execute"

**Expected Response (200 OK)**:
```json
{
  "id": "uuid-here",
  "email": "user@example.com",
  "display_name": "John Doe",
  "avatar_url": null,
  "created_at": "2025-12-25T00:00:00Z",
  "updated_at": "2025-12-25T00:00:00Z",
  "traveler_profile": {
    "id": "uuid-here",
    "user_id": "uuid-here",
    "nationality": "US",
    "residency_country": "US",
    "residency_status": "citizen",
    "date_of_birth": "1990-01-01",
    "passport_expiry": "2030-12-31",
    "travel_style": "balanced",
    "budget_preference": "moderate",
    "dietary_restrictions": ["vegetarian"],
    "accessibility_needs": null,
    "created_at": "2025-12-25T00:00:00Z",
    "updated_at": "2025-12-25T00:00:00Z"
  }
}
```

---

### 2. PUT /api/profile

**Purpose**: Update user profile (display_name, avatar_url)

**Steps in Swagger UI**:
1. Expand "PUT /api/profile"
2. Click "Try it out"
3. Edit the request body:
```json
{
  "display_name": "Jane Smith",
  "avatar_url": "https://example.com/avatar.jpg"
}
```
4. Click "Execute"

**Expected Response (200 OK)**:
```json
{
  "id": "uuid-here",
  "email": "user@example.com",
  "display_name": "Jane Smith",
  "avatar_url": "https://example.com/avatar.jpg",
  "created_at": "2025-12-25T00:00:00Z",
  "updated_at": "2025-12-25T05:00:00Z"
}
```

---

### 3. GET /api/profile/traveler

**Purpose**: Get traveler profile only

**Steps**:
1. Expand "GET /api/profile/traveler"
2. Click "Try it out"
3. Click "Execute"

**Expected Response**:
- 200 OK with traveler profile data
- 404 Not Found if no traveler profile exists yet

---

### 4. PUT /api/profile/traveler

**Purpose**: Create or update traveler profile

**Steps**:
1. Expand "PUT /api/profile/traveler"
2. Click "Try it out"
3. Edit request body (all fields optional except nationality):
```json
{
  "nationality": "US",
  "residency_country": "US",
  "residency_status": "citizen",
  "date_of_birth": "1990-01-01",
  "passport_expiry": "2030-12-31",
  "travel_style": "luxury",
  "budget_preference": "high",
  "dietary_restrictions": ["vegetarian", "gluten_free"],
  "accessibility_needs": "wheelchair"
}
```
4. Click "Execute"

**Validation Rules**:
- ✅ `nationality`: Must be 2-letter uppercase ISO country code (US, FR, JP)
- ✅ `residency_country`: Must be 2-letter uppercase ISO country code
- ✅ `residency_status`: One of: citizen, permanent_resident, work_visa, student_visa, tourist, other
- ✅ `date_of_birth`: Must be in the past (YYYY-MM-DD)
- ✅ `passport_expiry`: Optional, format YYYY-MM-DD
- ✅ `travel_style`: One of: budget, balanced, luxury, adventure
- ✅ `budget_preference`: One of: low, moderate, high, luxury
- ✅ `dietary_restrictions`: Array of strings
- ✅ `accessibility_needs`: String

---

### 5. PUT /api/profile/preferences

**Purpose**: Update user preferences (notifications, language, currency, units)

**Steps**:
1. Expand "PUT /api/profile/preferences"
2. Click "Try it out"
3. Edit request body:
```json
{
  "email_notifications": true,
  "push_notifications": true,
  "language": "en",
  "currency": "USD",
  "units": "metric"
}
```
4. Click "Execute"

**Validation Rules**:
- ✅ `language`: Must be 2-letter lowercase ISO 639-1 code (en, es, fr)
- ✅ `currency`: Must be 3-letter uppercase ISO 4217 code (USD, EUR, GBP)
- ✅ `units`: One of: metric, imperial

---

### 6. GET /api/profile/statistics

**Purpose**: Get travel statistics

**Steps**:
1. Expand "GET /api/profile/statistics"
2. Click "Try it out"
3. Click "Execute"

**Expected Response (200 OK)**:
```json
{
  "totalTrips": 5,
  "countriesVisited": 3,
  "destinationsExplored": 8,
  "activeTrips": 2
}
```

---

### 7. DELETE /api/profile

**Purpose**: Delete user account (requires confirmation)

**⚠️ WARNING**: This is destructive! Only test with a test account.

**Steps**:
1. Expand "DELETE /api/profile"
2. Click "Try it out"
3. Edit request body:
```json
{
  "confirmation": "DELETE MY ACCOUNT"
}
```
4. Click "Execute"

**Validation**:
- ❌ Wrong confirmation: Returns 400 Bad Request
- ✅ Correct confirmation: Returns 200 OK and deletes account

---

## 🧪 Test Scenarios

### Scenario 1: New User (No Traveler Profile)
1. GET /api/profile → Should return user with `traveler_profile: null`
2. PUT /api/profile/traveler → Create traveler profile
3. GET /api/profile → Should now include traveler_profile

### Scenario 2: Update Profile
1. PUT /api/profile → Update display name
2. GET /api/profile → Verify name changed
3. Check `updated_at` timestamp changed

### Scenario 3: Validation Errors
1. PUT /api/profile/traveler with `nationality: "USA"` → Should fail (must be 2 letters)
2. PUT /api/profile/preferences with `currency: "US"` → Should fail (must be 3 letters)
3. PUT /api/profile/traveler with `date_of_birth: "2030-01-01"` → Should fail (future date)

### Scenario 4: Statistics
1. GET /api/profile/statistics → Check initial counts
2. Create a trip via dashboard
3. GET /api/profile/statistics → Verify totalTrips increased

---

## ✅ Testing Checklist

### Prerequisites
- [x] Backend server running on http://localhost:8000
- [x] Swagger UI accessible at http://localhost:8000/api/docs
- [ ] Valid JWT token obtained
- [ ] Token authorized in Swagger UI

### API Endpoints
- [ ] GET /api/profile (200 OK)
- [ ] GET /api/profile (401 without token)
- [ ] PUT /api/profile (200 OK with valid data)
- [ ] PUT /api/profile (422 with invalid data)
- [ ] GET /api/profile/traveler (200 OK or 404)
- [ ] PUT /api/profile/traveler (200 OK - create)
- [ ] PUT /api/profile/traveler (200 OK - update)
- [ ] PUT /api/profile/traveler (422 - invalid country code)
- [ ] PUT /api/profile/preferences (200 OK)
- [ ] PUT /api/profile/preferences (422 - invalid currency)
- [ ] GET /api/profile/statistics (200 OK)
- [ ] DELETE /api/profile (200 OK - correct confirmation)
- [ ] DELETE /api/profile (400 - wrong confirmation)

### Data Validation
- [ ] Country codes validated (2-letter uppercase)
- [ ] Currency codes validated (3-letter uppercase)
- [ ] Language codes validated (2-letter lowercase)
- [ ] Date of birth must be in past
- [ ] Enum values validated (travel_style, budget_preference, etc.)

### Database Integration
- [ ] RLS policies allow user to access only their data
- [ ] Updates reflect immediately
- [ ] Timestamps (updated_at) auto-update
- [ ] Traveler profile linked to user correctly

---

## 🐛 Troubleshooting

### Error: "Could not authorize: unauthorized"
- **Cause**: JWT token is invalid or expired
- **Solution**: Get a fresh token from frontend or Supabase dashboard

### Error: "Not Found" (404)
- **Cause**: Endpoint URL is wrong or traveler profile doesn't exist
- **Solution**: Check endpoint path, ensure it starts with `/api/`

### Error: "Validation Error" (422)
- **Cause**: Invalid data in request body
- **Solution**: Check validation rules above, ensure country codes are 2-letter uppercase, etc.

### Error: "Internal Server Error" (500)
- **Cause**: Backend configuration issue or database connection problem
- **Solution**: Check backend logs, verify Supabase credentials in .env

---

## 📊 Expected Results

### Success Metrics
- ✅ All GET endpoints return data for authenticated user
- ✅ All PUT endpoints update data successfully
- ✅ Validation errors return 422 with clear error messages
- ✅ Unauthorized requests return 401
- ✅ RLS policies enforce data isolation between users
- ✅ Timestamps update automatically
- ✅ Database constraints enforced (e.g., unique email)

---

## 📝 Next Steps After Testing

1. **If All Tests Pass**:
   - Mark I2 Backend as "Tested ✅"
   - Move to Step 3: Update Frontend Components
   - Test full integration (frontend + backend)

2. **If Tests Fail**:
   - Document failing tests
   - Check backend logs for errors
   - Verify database schema matches expectations
   - Check RLS policies are correct

---

## 💡 Tips

- **Use Swagger UI** - It's the easiest way to test, no curl needed
- **Test with real data** - Use realistic names, dates, country codes
- **Check response times** - Profile endpoints should respond in <500ms
- **Test edge cases** - Empty strings, null values, very long strings
- **Check error messages** - Should be user-friendly and actionable

---

**Testing Status**: ⏳ Ready to Test
**Backend Server**: ✅ Running
**Documentation**: ✅ Complete

Last Updated: 2025-12-25
