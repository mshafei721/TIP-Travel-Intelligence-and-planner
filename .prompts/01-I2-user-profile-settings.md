# I2: User Profile & Settings

> **Prerequisites**: Read `00-session-context.md` first

## Objective

Complete user profile management including traveler profile, preferences, and account settings.

## Current Status

| Component | Frontend | Backend | Status |
|-----------|----------|---------|--------|
| Profile View | 30% | 20% | Partial |
| Profile Edit | 0% | 0% | Not Started |
| Traveler Profile | 0% | 0% | Not Started |
| Preferences | 0% | 0% | Not Started |
| Account Settings | 80% | 60% | Mostly Done |

---

## BACKEND TASKS

### API Endpoints to Implement

```python
# backend/app/api/profile.py

# Existing (verify working)
GET  /api/profile              # Get current user profile
GET  /api/profile/statistics   # Get travel statistics

# New endpoints needed
PUT  /api/profile              # Update user profile
GET  /api/profile/traveler     # Get traveler profile
PUT  /api/profile/traveler     # Update traveler profile
GET  /api/profile/preferences  # Get user preferences
PUT  /api/profile/preferences  # Update preferences
DELETE /api/profile            # Delete account (with confirmation)
```

### Pydantic Models

```python
# backend/app/models/profile.py

class UserProfileUpdate(BaseModel):
    full_name: str | None = None
    avatar_url: str | None = None
    phone: str | None = None
    timezone: str | None = None

class TravelerProfile(BaseModel):
    nationality: str
    residence_country: str
    origin_city: str
    passport_expiry: date | None = None
    dietary_restrictions: list[str] = []
    accessibility_needs: list[str] = []
    travel_style: str = "balanced"  # budget, balanced, luxury
    interests: list[str] = []

class UserPreferences(BaseModel):
    email_notifications: bool = True
    push_notifications: bool = False
    marketing_emails: bool = False
    language: str = "en"
    currency: str = "USD"
    units: str = "metric"  # metric, imperial
```

### Database Tables

```sql
-- Verify these exist in Supabase
-- user_profiles (exists)
-- traveler_profiles (exists)

-- Check RLS policies are working
```

---

## FRONTEND TASKS

### Documentation Reference

```
product-plan/instructions/incremental/09-user-profile-settings.md
product-plan/sections/user-profile-settings/
```

### Components to Build

```
frontend/components/profile/
├── ProfileHeader.tsx         # Avatar, name, stats
├── ProfileForm.tsx           # Edit profile form
├── TravelerProfileForm.tsx   # Travel preferences form
├── NationalitySelector.tsx   # Country dropdown
├── InterestsPicker.tsx       # Multi-select interests
├── TravelStyleSelector.tsx   # Budget/Balanced/Luxury
├── DietaryRestrictions.tsx   # Dietary options
├── AccessibilityNeeds.tsx    # Accessibility options
├── PreferencesForm.tsx       # Notification settings
├── AccountDangerZone.tsx     # Delete account section
└── ProfileSkeleton.tsx       # Loading state
```

### Pages to Build

```
frontend/app/(app)/profile/
├── page.tsx                  # Profile overview
├── loading.tsx
├── error.tsx
├── edit/
│   └── page.tsx              # Edit profile form
├── traveler/
│   └── page.tsx              # Traveler profile
├── preferences/
│   └── page.tsx              # Preferences page
└── settings/
    └── page.tsx              # Account settings
```

### API Integration

```typescript
// frontend/lib/api/profile.ts

export async function getProfile(): Promise<UserProfile>
export async function updateProfile(data: UserProfileUpdate): Promise<UserProfile>
export async function getTravelerProfile(): Promise<TravelerProfile>
export async function updateTravelerProfile(data: TravelerProfile): Promise<TravelerProfile>
export async function getPreferences(): Promise<UserPreferences>
export async function updatePreferences(data: UserPreferences): Promise<UserPreferences>
export async function deleteAccount(confirmation: string): Promise<void>
```

---

## TDD TEST CASES

### Backend Tests

```python
# backend/tests/api/test_profile.py

def test_get_profile_authenticated():
    """Should return user profile for authenticated user"""

def test_get_profile_unauthenticated():
    """Should return 401 for unauthenticated request"""

def test_update_profile_valid():
    """Should update profile with valid data"""

def test_update_profile_invalid_timezone():
    """Should reject invalid timezone"""

def test_get_traveler_profile():
    """Should return traveler profile"""

def test_update_traveler_profile():
    """Should update traveler preferences"""

def test_delete_account_with_confirmation():
    """Should delete account when confirmation matches"""

def test_delete_account_wrong_confirmation():
    """Should reject deletion with wrong confirmation"""
```

### Frontend Tests

```typescript
// frontend/__tests__/components/profile/ProfileForm.test.tsx

describe('ProfileForm', () => {
  it('renders profile data correctly')
  it('validates required fields')
  it('shows loading state while saving')
  it('displays success message on save')
  it('handles API errors gracefully')
})

describe('TravelerProfileForm', () => {
  it('renders all travel preference fields')
  it('allows multi-select for interests')
  it('validates nationality selection')
  it('saves preferences to API')
})
```

---

## IMPLEMENTATION ORDER

### Phase 1: Backend APIs (Day 1)
1. [ ] Write tests for profile endpoints
2. [ ] Implement GET/PUT /api/profile
3. [ ] Implement GET/PUT /api/profile/traveler
4. [ ] Implement GET/PUT /api/profile/preferences
5. [ ] Verify RLS policies

### Phase 2: Frontend API Layer (Day 1)
1. [ ] Create frontend/lib/api/profile.ts
2. [ ] Add TypeScript interfaces
3. [ ] Implement API client functions
4. [ ] Add error handling

### Phase 3: Frontend Components (Day 2)
1. [ ] Write component tests
2. [ ] Build ProfileHeader
3. [ ] Build ProfileForm
4. [ ] Build TravelerProfileForm
5. [ ] Build PreferencesForm

### Phase 4: Frontend Pages (Day 2)
1. [ ] Create profile page routes
2. [ ] Integrate components
3. [ ] Add loading/error states
4. [ ] Test full flow

### Phase 5: Integration Testing (Day 3)
1. [ ] Test frontend-backend integration
2. [ ] Verify dark mode
3. [ ] Test responsive design
4. [ ] Update feature_list.json

---

## DESIGN SYSTEM NOTES

### Form Layout
```html
<form class="space-y-6 max-w-2xl">
  <div class="bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 p-6">
    <!-- Form fields -->
  </div>
</form>
```

### Input Fields
```html
<input class="w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700
       bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50
       focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
```

### Section Headers
```html
<h2 class="text-xl font-semibold text-slate-900 dark:text-slate-50 mb-4">
  Traveler Profile
</h2>
<p class="text-slate-600 dark:text-slate-400 text-sm mb-6">
  This information helps us generate personalized travel recommendations.
</p>
```

---

## DELIVERABLES

- [ ] Backend: 6 API endpoints working
- [ ] Frontend: 10+ components built
- [ ] Frontend: 4 pages complete
- [ ] Tests: >80% coverage
- [ ] Dark mode: All components
- [ ] Responsive: Mobile-first
- [ ] feature_list.json updated
- [ ] Committed and pushed
